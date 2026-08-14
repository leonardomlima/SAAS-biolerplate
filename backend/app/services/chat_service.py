"""
Serviço de Chat para Agentes de IA.
Gerencia sessões, histórico de mensagens e contexto no Redis.
"""

import json
import structlog
from typing import Any, Optional, List, Dict
from uuid import UUID
from datetime import datetime, timedelta

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis_client
from app.models.agent import Agent, ChatSession, Message, AgentType
from app.schemas.agent import ChatMessageRequest, ChatMessageResponse
from app.services.llm_agent_service import LLMService, ModelGroup
from app.services.tool_executor import ToolExecutor

logger = structlog.get_logger()


class ChatService:
    """
    Serviço de chat para interação com agentes de IA.
    
    Funcionalidades:
    - Gerenciamento de sessões de chat
    - Histórico de mensagens no PostgreSQL
    - Contexto de sessão no Redis (para performance)
    - Execução de tools
    - Streaming de respostas
    """
    
    def __init__(self, tenant_id: UUID, user_id: UUID):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.redis_prefix = f"chat_session:{tenant_id}"
        
    async def _get_redis_client(self):
        """Obtém cliente Redis"""
        return await get_redis_client()
    
    def _get_redis_key(self, session_id: UUID) -> str:
        """Gera chave Redis para uma sessão"""
        return f"{self.redis_prefix}:{session_id}"
    
    async def _save_context_to_redis(
        self, 
        session_id: UUID, 
        messages: List[Dict[str, Any]],
        ttl_seconds: int = 3600
    ):
        """Salva contexto da sessão no Redis"""
        try:
            redis = await self._get_redis_client()
            if not redis:
                logger.warning("Redis não disponível, pulando cache")
                return
            
            key = self._get_redis_key(session_id)
            context_data = {
                "messages": messages[-10:],  # Últimas 10 mensagens para contexto
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            await redis.setex(
                key,
                ttl_seconds,
                json.dumps(context_data, default=str)
            )
            logger.debug("Contexto salvo no Redis", session_id=session_id)
            
        except Exception as e:
            logger.error("Erro ao salvar contexto no Redis", error=str(e))
    
    async def _get_context_from_redis(self, session_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """Recupera contexto da sessão do Redis"""
        try:
            redis = await self._get_redis_client()
            if not redis:
                return None
            
            key = self._get_redis_key(session_id)
            data = await redis.get(key)
            
            if data:
                context_data = json.loads(data)
                return context_data.get("messages", [])
            
            return None
            
        except Exception as e:
            logger.error("Erro ao recuperar contexto do Redis", error=str(e))
            return None
    
    async def create_session(self, agent_id: UUID, title: Optional[str] = None) -> ChatSession:
        """Cria nova sessão de chat"""
        async with AsyncSessionLocal() as session:
            # Verificar se agente existe e pertence ao tenant
            result = await session.execute(
                select(Agent).where(
                    Agent.id == agent_id,
                    Agent.tenant_id == self.tenant_id,
                    Agent.is_active == True
                )
            )
            agent = result.first()
            
            if not agent:
                raise ValueError(f"Agente {agent_id} não encontrado ou inativo")
            
            # Criar sessão
            chat_session = ChatSession(
                tenant_id=self.tenant_id,
                agent_id=agent_id,
                user_id=self.user_id,
                title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                redis_key=self._get_redis_key(UUID(int=0)),  # Será atualizado
            )
            
            session.add(chat_session)
            await session.commit()
            await session.refresh(chat_session)
            
            # Atualizar redis_key com ID real
            chat_session.redis_key = self._get_redis_key(chat_session.id)
            session.add(chat_session)
            await session.commit()
            
            logger.info("Sessão de chat criada", session_id=chat_session.id)
            return chat_session
    
    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        """Recupera sessão de chat com mensagens"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ChatSession)
                .where(
                    ChatSession.id == session_id,
                    ChatSession.tenant_id == self.tenant_id,
                    ChatSession.is_active == True
                )
            )
            chat_session = result.first()
            
            if not chat_session:
                return None
            
            # Carregar mensagens
            messages_result = await session.execute(
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.created_at.asc())
            )
            chat_session.messages = messages_result.all()
            
            return chat_session
    
    async def list_sessions(
        self, 
        agent_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ChatSession]:
        """Lista sessões de chat do usuário"""
        async with AsyncSessionLocal() as session:
            query = select(ChatSession).where(
                ChatSession.tenant_id == self.tenant_id,
                ChatSession.user_id == self.user_id,
                ChatSession.is_active == True
            )
            
            if agent_id:
                query = query.where(ChatSession.agent_id == agent_id)
            
            query = query.order_by(ChatSession.updated_at.desc()).limit(limit).offset(offset)
            
            result = await session.execute(query)
            sessions = result.all()
            
            return [s[0] for s in sessions]
    
    async def send_message(
        self,
        request: ChatMessageRequest,
        agent: Agent,
        session: Optional[ChatSession] = None
    ) -> ChatMessageResponse:
        """
        Envia mensagem para o agente e processa resposta.
        
        Fluxo:
        1. Salvar mensagem do usuário
        2. Preparar contexto (histórico + Redis)
        3. Chamar LLM com tools
        4. Executar tools se necessário
        5. Salvar resposta do assistente
        6. Atualizar contexto no Redis
        """
        async with AsyncSessionLocal() as db_session:
            # Usar sessão existente ou criar nova
            if not session:
                session = await self.create_session(agent_id=agent.id, title=None)
            
            # 1. Salvar mensagem do usuário
            user_message = Message(
                tenant_id=self.tenant_id,
                session_id=session.id,
                role="user",
                content=request.message,
            )
            db_session.add(user_message)
            await db_session.flush()
            
            # 2. Preparar contexto
            # Buscar últimas N mensagens para contexto
            messages_result = await db_session.execute(
                select(Message)
                .where(Message.session_id == session.id)
                .order_by(Message.created_at.desc())
                .limit(20)  # Últimas 20 mensagens
            )
            recent_messages = messages_result.all()
            
            # Converter para formato OpenAI
            openai_messages = []
            
            # Adicionar system prompt se existir
            if agent.system_prompt:
                openai_messages.append({
                    "role": "system",
                    "content": agent.system_prompt
                })
            
            # Adicionar histórico (ordem cronológica)
            for msg in reversed(recent_messages):
                openai_messages.append({
                    "role": msg[0].role,
                    "content": msg[0].content,
                })
            
            # Adicionar mensagem atual
            openai_messages.append({
                "role": "user",
                "content": request.message,
            })
            
            # 3. Preparar tools
            tool_executor = ToolExecutor(tenant_id=self.tenant_id, user_id=self.user_id)
            tools = []
            
            if agent.enabled_tools and len(agent.enabled_tools) > 0:
                all_tools = tool_executor.get_all_tools()
                tools = [
                    t for t in all_tools 
                    if t["function"]["name"] in agent.enabled_tools
                ]
            
            # 4. Determinar parâmetros baseados no modelo
            llm_service = LLMService(tenant_id=self.tenant_id, user_id=self.user_id)
            
            # Usar overrides da requisição ou padrões do agente
            temperature = request.override_temperature or agent.temperature
            reasoning_effort = request.override_reasoning_effort or agent.reasoning_effort
            max_tokens = request.override_max_tokens or agent.max_tokens
            
            # 5. Chamar LLM
            llm_response = await llm_service.chat_completion(
                messages=openai_messages,
                model_name=agent.model_name,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
                reasoning_summary=agent.reasoning_summary,
                max_tokens=max_tokens,
                top_p=agent.top_p,
                tools=tools if len(tools) > 0 else None,
                tool_choice="auto" if len(tools) > 0 else None,
            )
            
            # 6. Processar tool calls se existirem
            final_content = llm_response["content"]
            tool_calls = llm_response.get("tool_calls", [])
            
            if tool_calls and len(tool_calls) > 0:
                # Executar cada tool call
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    tool_name = function.get("name")
                    tool_args_str = function.get("arguments", "{}")
                    
                    try:
                        tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
                        
                        # Executar tool
                        tool_result = await tool_executor.execute_tool(
                            tool_name=tool_name,
                            arguments=tool_args
                        )
                        
                        # Salvar mensagem de tool call
                        tool_call_msg = Message(
                            tenant_id=self.tenant_id,
                            session_id=session.id,
                            role="tool",
                            content=json.dumps(tool_result.get("result", {})),
                            tool_call_id=tool_call.get("id"),
                            tool_name=tool_name,
                            tool_args=tool_args,
                            tool_result=json.dumps(tool_result.get("result", {})),
                        )
                        db_session.add(tool_call_msg)
                        
                        # Adicionar resultado ao contexto para próximo loop do LLM
                        openai_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.get("id"),
                            "content": json.dumps(tool_result.get("result", {})),
                        })
                        
                    except Exception as e:
                        logger.error("Erro ao executar tool", tool=tool_name, error=str(e))
                
                # Se houve tool calls, chamar LLM novamente com resultados
                if len(openai_messages) > len(recent_messages) + 2:
                    llm_response = await llm_service.chat_completion(
                        messages=openai_messages,
                        model_name=agent.model_name,
                        temperature=temperature,
                        reasoning_effort=reasoning_effort,
                        max_tokens=max_tokens,
                    )
                    final_content = llm_response["content"]
            
            # 7. Salvar resposta do assistente
            assistant_message = Message(
                tenant_id=self.tenant_id,
                session_id=session.id,
                role="assistant",
                content=final_content,
                reasoning_summary=llm_response.get("reasoning_summary"),
                reasoning_effort_used=reasoning_effort,
                prompt_tokens=llm_response.get("prompt_tokens"),
                completion_tokens=llm_response.get("completion_tokens"),
                total_tokens=llm_response.get("total_tokens"),
                cost_usd=llm_response.get("cost_usd"),
            )
            db_session.add(assistant_message)
            
            # Atualizar timestamp da sessão
            session.updated_at = datetime.utcnow()
            db_session.add(session)
            
            await db_session.commit()
            await db_session.refresh(assistant_message)
            
            # 8. Atualizar contexto no Redis
            await self._save_context_to_redis(
                session_id=session.id,
                messages=openai_messages + [{"role": "assistant", "content": final_content}]
            )
            
            logger.info(
                "Mensagem processada",
                session_id=session.id,
                tokens=llm_response.get("total_tokens"),
                cost_usd=llm_response.get("cost_usd")
            )
            
            # Retornar resposta
            return ChatMessageResponse(
                message_id=assistant_message.id,
                session_id=session.id,
                content=final_content,
                reasoning_summary=llm_response.get("reasoning_summary"),
                tool_calls=tool_calls if len(tool_calls) > 0 else None,
                prompt_tokens=llm_response.get("prompt_tokens", 0),
                completion_tokens=llm_response.get("completion_tokens", 0),
                total_tokens=llm_response.get("total_tokens", 0),
                cost_usd=llm_response.get("cost_usd"),
                created_at=assistant_message.created_at,
            )
    
    async def delete_session(self, session_id: UUID) -> bool:
        """Deleta sessão de chat (soft delete)"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ChatSession).where(
                    ChatSession.id == session_id,
                    ChatSession.tenant_id == self.tenant_id
                )
            )
            chat_session = result.first()
            
            if not chat_session:
                return False
            
            # Soft delete
            chat_session[0].is_active = False
            session.add(chat_session[0])
            await session.commit()
            
            # Remover do Redis
            try:
                redis = await self._get_redis_client()
                if redis:
                    key = self._get_redis_key(session_id)
                    await redis.delete(key)
            except Exception as e:
                logger.error("Erro ao remover sessão do Redis", error=str(e))
            
            logger.info("Sessão deletada", session_id=session_id)
            return True
    
    async def clear_session_history(self, session_id: UUID, keep_last: int = 0) -> bool:
        """Limpa histórico de mensagens de uma sessão"""
        async with AsyncSessionLocal() as session:
            if keep_last == 0:
                # Deletar todas as mensagens
                result = await session.execute(
                    select(Message).where(Message.session_id == session_id)
                )
                messages = result.all()
                
                for msg in messages:
                    await session.delete(msg[0])
            else:
                # Manter últimas N mensagens
                messages_result = await session.execute(
                    select(Message.id)
                    .where(Message.session_id == session_id)
                    .order_by(Message.created_at.desc())
                    .offset(keep_last)
                )
                messages_to_delete = messages_result.all()
                
                for msg_id_tuple in messages_to_delete:
                    msg_id = msg_id_tuple[0]
                    msg_result = await session.execute(
                        select(Message).where(Message.id == msg_id)
                    )
                    msg = msg_result.first()
                    if msg:
                        await session.delete(msg[0])
            
            await session.commit()
            
            # Limpar Redis também
            await self._save_context_to_redis(session_id, [], ttl_seconds=60)
            
            logger.info("Histórico limpo", session_id=session_id, keep_last=keep_last)
            return True


async def get_chat_service(tenant_id: UUID, user_id: UUID) -> ChatService:
    """Factory para obter instância do ChatService"""
    return ChatService(tenant_id=tenant_id, user_id=user_id)
