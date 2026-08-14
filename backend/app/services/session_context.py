"""
Gerenciamento de Contexto de Sessão no Redis.
Armazena histórico de conversas temporário para agentes de IA.
"""

import json
import structlog
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from app.core.cache import redis_client

logger = structlog.get_logger()


class SessionContextManager:
    """
    Gerencia o contexto de sessões de chat no Redis.
    
    O Redis armazena:
    - Histórico recente de mensagens (últimas N interações)
    - Metadados da sessão (tokens usados, custo, etc.)
    - Estado temporário de tool calls em andamento
    """
    
    def __init__(self, tenant_id: UUID, session_id: UUID):
        self.tenant_id = tenant_id
        self.session_id = session_id
        self.redis_key_prefix = f"chat_session:{tenant_id}:{session_id}"
    
    def _get_messages_key(self) -> str:
        """Retorna a chave Redis para mensagens da sessão"""
        return f"{self.redis_key_prefix}:messages"
    
    def _get_metadata_key(self) -> str:
        """Retorna a chave Redis para metadados da sessão"""
        return f"{self.redis_key_prefix}:metadata"
    
    def _get_context_key(self) -> str:
        """Retorna a chave Redis para contexto de raciocínio"""
        return f"{self.redis_key_prefix}:context"
    
    async def add_message(
        self,
        role: str,
        content: str,
        tool_call_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict] = None,
        tool_result: Optional[str] = None,
        reasoning_summary: Optional[str] = None,
        tokens_used: Optional[int] = None,
    ) -> int:
        """
        Adiciona mensagem ao histórico da sessão no Redis.
        
        Args:
            role: "user", "assistant", "system", ou "tool"
            content: Conteúdo da mensagem
            tool_call_id: ID do tool call (se aplicável)
            tool_name: Nome da tool executada
            tool_args: Argumentos passados para a tool
            tool_result: Resultado da execução da tool
            reasoning_summary: Resumo do raciocínio (CoT)
            tokens_used: Tokens consumidos nesta mensagem
        
        Returns:
            Número total de mensagens na sessão
        """
        if not redis_client:
            logger.warning("Redis não inicializado, pulando cache de sessão")
            return 0
        
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Campos opcionais para tool calls
        if tool_call_id:
            message_data["tool_call_id"] = tool_call_id
        if tool_name:
            message_data["tool_name"] = tool_name
        if tool_args:
            message_data["tool_args"] = json.dumps(tool_args)
        if tool_result:
            message_data["tool_result"] = tool_result
        if reasoning_summary:
            message_data["reasoning_summary"] = reasoning_summary
        if tokens_used:
            message_data["tokens_used"] = tokens_used
        
        messages_key = self._get_messages_key()
        
        # Adicionar à lista de mensagens (LRU - menos recentes são removidas)
        pipe = redis_client.pipeline()
        pipe.rpush(messages_key, json.dumps(message_data))
        pipe.ltrim(messages_key, -50, -1)  # Manter apenas últimas 50 mensagens
        pipe.expire(messages_key, timedelta(hours=24))  # Expirar em 24h
        await pipe.execute()
        
        # Atualizar contagem de tokens nos metadados
        if tokens_used:
            await self.increment_token_count(tokens_used)
        
        return await redis_client.llen(messages_key)
    
    async def get_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Recupera histórico de mensagens da sessão.
        
        Args:
            limit: Número máximo de mensagens para retornar
        
        Returns:
            Lista de mensagens em ordem cronológica
        """
        if not redis_client:
            return []
        
        messages_key = self._get_messages_key()
        raw_messages = await redis_client.lrange(messages_key, -limit, -1)
        
        messages = []
        for msg in raw_messages:
            try:
                message_data = json.loads(msg)
                # Parse de campos JSON serializados
                if "tool_args" in message_data:
                    message_data["tool_args"] = json.loads(message_data["tool_args"])
                messages.append(message_data)
            except json.JSONDecodeError:
                logger.error("Erro ao parsear mensagem do Redis", raw=msg)
                continue
        
        return messages
    
    async def clear_messages(self) -> bool:
        """Limpa todas as mensagens da sessão"""
        if not redis_client:
            return False
        
        messages_key = self._get_messages_key()
        await redis_client.delete(messages_key)
        return True
    
    async def set_metadata(self, key: str, value: Any) -> bool:
        """Define um valor de metadado na sessão"""
        if not redis_client:
            return False
        
        metadata_key = self._get_metadata_key()
        await redis_client.hset(metadata_key, key, json.dumps(value))
        await redis_client.expire(metadata_key, timedelta(hours=24))
        return True
    
    async def get_metadata(self, key: str) -> Optional[Any]:
        """Recupera um valor de metadado da sessão"""
        if not redis_client:
            return None
        
        metadata_key = self._get_metadata_key()
        value = await redis_client.hget(metadata_key, key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def get_all_metadata(self) -> Dict[str, Any]:
        """Recupera todos os metadados da sessão"""
        if not redis_client:
            return {}
        
        metadata_key = self._get_metadata_key()
        raw_data = await redis_client.hgetall(metadata_key)
        
        metadata = {}
        for key, value in raw_data.items():
            try:
                metadata[key] = json.loads(value)
            except json.JSONDecodeError:
                metadata[key] = value
        
        return metadata
    
    async def increment_token_count(self, count: int) -> int:
        """Incrementa contador de tokens usados na sessão"""
        if not redis_client:
            return 0
        
        metadata_key = self._get_metadata_key()
        new_total = await redis_client.hincrby(metadata_key, "total_tokens", count)
        return new_total
    
    async def increment_cost(self, cost_usd: float) -> float:
        """Incrementa custo acumulado da sessão"""
        if not redis_client:
            return 0.0
        
        metadata_key = self._get_metadata_key()
        # Redis hincrby trabalha com inteiros, então multiplicamos por 1000000
        cost_int = int(cost_usd * 1000000)
        new_total = await redis_client.hincrby(metadata_key, "total_cost_micro", cost_int)
        return new_total / 1000000
    
    async def set_reasoning_context(self, context: str) -> bool:
        """Armazena contexto de raciocínio para Chain of Thought"""
        if not redis_client:
            return False
        
        context_key = self._get_context_key()
        await redis_client.set(context_key, context)
        await redis_client.expire(context_key, timedelta(hours=1))  # Contexto expira em 1h
        return True
    
    async def get_reasoning_context(self) -> Optional[str]:
        """Recupera contexto de raciocínio armazenado"""
        if not redis_client:
            return None
        
        context_key = self._get_context_key()
        return await redis_client.get(context_key)
    
    async def delete_session(self) -> bool:
        """Remove completamente a sessão do Redis"""
        if not redis_client:
            return False
        
        keys_to_delete = [
            self._get_messages_key(),
            self._get_metadata_key(),
            self._get_context_key(),
        ]
        
        deleted = await redis_client.delete(*keys_to_delete)
        return deleted > 0
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão"""
        if not redis_client:
            return {}
        
        messages_key = self._get_messages_key()
        metadata_key = self._get_metadata_key()
        
        message_count = await redis_client.llen(messages_key)
        metadata = await self.get_all_metadata()
        
        return {
            "message_count": message_count,
            "total_tokens": metadata.get("total_tokens", 0),
            "total_cost_usd": (metadata.get("total_cost_micro", 0) or 0) / 1000000,
            "session_id": str(self.session_id),
            "tenant_id": str(self.tenant_id),
        }


async def get_session_context(tenant_id: UUID, session_id: UUID) -> SessionContextManager:
    """Factory para obter gerenciador de contexto de sessão"""
    return SessionContextManager(tenant_id=tenant_id, session_id=session_id)
