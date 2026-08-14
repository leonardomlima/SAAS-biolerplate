"""
Serviço de LLM para integração com OpenRouter e outros provedores.
Suporta múltiplos modelos, grupos especializados e parâmetros avançados.
"""

import httpx
import structlog
from typing import Any, Optional, AsyncGenerator, List, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum

from app.core.config import settings
from app.models.agent import ModelProvider, ReasoningEffort, AgentType
from app.services.tool_executor import ToolExecutor

logger = structlog.get_logger()


class ModelGroup(str, Enum):
    """Grupos de modelos especializados"""
    REASONING = "reasoning"  # Raciocínio complexo (o1, Claude Thinking)
    CREATIVE = "creative"    # Criatividade e copywriting
    CODING = "coding"        # Código e tarefas técnicas
    FAST = "fast"           # Rápido e barato
    BALANCED = "balanced"   # Equilíbrio custo/desempenho


# Configuração dos grupos de modelos
MODEL_GROUPS_CONFIG = {
    ModelGroup.REASONING: {
        "name": "Raciocínio Complexo",
        "description": "Modelos especializados em raciocínio lógico, matemática e análise profunda",
        "recommended_models": [
            "openai/o1-pro",
            "openai/o1-mini",
            "anthropic/claude-3.7-sonnet-thinking",
            "deepseek/deepseek-r1",
        ],
        "use_cases": [
            "Análise de dados complexa",
            "Resolução de problemas matemáticos",
            "Planejamento estratégico",
            "Debug de código complexo",
        ],
        "default_reasoning_effort": ReasoningEffort.HIGH,
        "default_temperature": None,  # Modelos de raciocínio não usam temperature
    },
    ModelGroup.CREATIVE: {
        "name": "Criatividade e Copywriting",
        "description": "Modelos otimizados para criação de conteúdo, marketing e escrita criativa",
        "recommended_models": [
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-pro-1.5",
        ],
        "use_cases": [
            "Criação de copy para marketing",
            "Redação de blogs e artigos",
            "Brainstorming de ideias",
            "Tradução criativa",
        ],
        "default_temperature": 0.8,
        "default_reasoning_effort": None,
    },
    ModelGroup.CODING: {
        "name": "Código e Tarefas Técnicas",
        "description": "Modelos especializados em programação e tarefas técnicas",
        "recommended_models": [
            "deepseek/deepseek-coder-v2",
            "openai/gpt-4-turbo",
            "anthropic/claude-3.5-sonnet",
            "qwen/qwen-2.5-coder",
        ],
        "use_cases": [
            "Geração de código",
            "Code review",
            "Refatoração",
            "Documentação técnica",
        ],
        "default_temperature": 0.2,
        "default_reasoning_effort": None,
    },
    ModelGroup.FAST: {
        "name": "Rápido e Barato",
        "description": "Modelos leves para tarefas simples e alto volume",
        "recommended_models": [
            "meta-llama/llama-3-8b-instruct",
            "google/gemma-7b",
            "mistral/mistral-7b-instruct",
            "openai/gpt-3.5-turbo",
        ],
        "use_cases": [
            "Classificação de texto",
            "Extração de entidades",
            "Respostas rápidas",
            "Pré-processamento",
        ],
        "default_temperature": 0.5,
        "default_reasoning_effort": None,
    },
    ModelGroup.BALANCED: {
        "name": "Equilibrado",
        "description": "Modelos com bom equilíbrio entre custo e desempenho",
        "recommended_models": [
            "openai/gpt-4o-mini",
            "anthropic/claude-3-haiku",
            "google/gemini-flash-1.5",
        ],
        "use_cases": [
            "Chatbots gerais",
            "Assistentes virtuais",
            "Análise moderada",
            "Uso diário",
        ],
        "default_temperature": 0.7,
        "default_reasoning_effort": None,
    },
}


class LLMService:
    """
    Serviço de LLM para interação com múltiplos provedores via OpenRouter.
    """
    
    def __init__(self, tenant_id: UUID, user_id: Optional[UUID] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        
        # API Key do OpenRouter (deve ser configurada no .env)
        self.api_key = settings.OPENROUTER_API_KEY or ""
        
    def _get_headers(self) -> dict[str, str]:
        """Retorna headers para requisições à OpenRouter"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.FRONTEND_URL or "http://localhost:5173",
            "X-Title": "SaaS Boilerplate AI",
        }
    
    def _detect_model_capabilities(self, model_name: str) -> dict[str, bool]:
        """
        Detecta capacidades de um modelo baseado no nome.
        
        Returns:
            Dict com flags: supports_tools, supports_vision, supports_reasoning, requires_reasoning_effort
        """
        model_lower = model_name.lower()
        
        # Modelos que requerem reasoning_effort ao invés de temperature
        reasoning_models = ["o1-pro", "o1-mini", "o1-preview", "r1", "thinking"]
        requires_reasoning = any(kw in model_lower for kw in reasoning_models)
        
        # Modelos que suportam tools
        tools_supported = not any(kw in model_lower for kw in ["gemini-1.0", "llama-2"])
        
        # Modelos que suportam visão
        vision_supported = any(kw in model_lower for kw in ["vision", "gpt-4o", "claude-3", "gemini"])
        
        return {
            "supports_tools": tools_supported,
            "supports_vision": vision_supported,
            "supports_reasoning": requires_reasoning,
            "requires_reasoning_effort": requires_reasoning,
        }
    
    def _prepare_generation_params(
        self,
        model_name: str,
        temperature: Optional[float] = None,
        reasoning_effort: Optional[ReasoningEffort] = None,
        reasoning_summary: bool = False,
        max_tokens: int = 2048,
        top_p: float = 1.0,
    ) -> dict[str, Any]:
        """
        Prepara parâmetros de geração adequados para o modelo.
        
        Para modelos da família o1, usa reasoning_effort ao invés de temperature.
        """
        capabilities = self._detect_model_capabilities(model_name)
        params: dict[str, Any] = {"max_tokens": max_tokens}
        
        if capabilities["requires_reasoning_effort"]:
            # Modelo de raciocínio: usar reasoning_effort
            if reasoning_effort:
                params["reasoning_effort"] = reasoning_effort.value
            
            # Reasoning summary para Chain of Thought
            if reasoning_summary:
                params["include_reasoning"] = True
        else:
            # Modelo padrão: usar temperature
            if temperature is not None:
                params["temperature"] = temperature
            
            if top_p != 1.0:
                params["top_p"] = top_p
        
        return params
    
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model_name: str = "openai/gpt-4o-mini",
        temperature: Optional[float] = None,
        reasoning_effort: Optional[ReasoningEffort] = None,
        reasoning_summary: bool = False,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        tools: Optional[list[dict]] = None,
        tool_choice: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Realiza chat completion usando OpenRouter.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            model_name: Nome do modelo (ex: "openai/gpt-4o-mini")
            temperature: Temperatura (ignorado para modelos o1)
            reasoning_effort: Nível de esforço de raciocínio (para modelos o1)
            reasoning_summary: Incluir resumo do raciocínio (CoT)
            max_tokens: Máximo de tokens na resposta
            top_p: Top-p sampling
            tools: Lista de tools disponíveis
            tool_choice: Escolha de tool ("auto", "none", ou nome específico)
            system_prompt: Prompt de sistema (adicionado como primeira mensagem)
        
        Returns:
            Resposta completa com conteúdo, tokens usados, custos, etc.
        """
        # Adicionar system prompt se existir
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Preparar parâmetros
        generation_params = self._prepare_generation_params(
            model_name=model_name,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            reasoning_summary=reasoning_summary,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        
        # Montar payload
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            **generation_params,
        }
        
        # Adicionar tools se fornecidas
        if tools and len(tools) > 0:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extrair informações da resposta
                choice = data["choices"][0]
                message = choice["message"]
                usage = data.get("usage", {})
                
                # Calcular custo aproximado (OpenRouter fornece pricing)
                cost_usd = None
                if "cost" in data:
                    cost_usd = data["cost"]
                
                return {
                    "content": message.get("content", ""),
                    "tool_calls": message.get("tool_calls", []),
                    "reasoning_summary": message.get("reasoning", None),
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "cost_usd": cost_usd,
                    "model": data.get("model", model_name),
                    "finish_reason": choice.get("finish_reason", "stop"),
                }
                
        except httpx.HTTPError as e:
            logger.error("Erro na chamada OpenRouter", error=str(e), model=model_name)
            raise Exception(f"Erro na API de LLM: {str(e)}")
    
    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model_name: str = "openai/gpt-4o-mini",
        temperature: Optional[float] = None,
        reasoning_effort: Optional[ReasoningEffort] = None,
        max_tokens: int = 2048,
        tools: Optional[list[dict]] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Streaming de chat completion.
        
        Yields:
            Chunks da resposta conforme chegam
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        generation_params = self._prepare_generation_params(
            model_name=model_name,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            reasoning_summary=False,
            max_tokens=max_tokens,
        )
        
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            **generation_params,
        }
        
        if tools and len(tools) > 0:
            payload["tools"] = tools
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                yield {"type": "done"}
                                break
                            
                            try:
                                import json
                                data = json.loads(data_str)
                                
                                if data["choices"] and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    
                                    # Conteúdo
                                    if "content" in delta:
                                        yield {
                                            "type": "content",
                                            "data": delta["content"],
                                        }
                                    
                                    # Tool calls
                                    if "tool_calls" in delta:
                                        yield {
                                            "type": "tool_call",
                                            "data": delta["tool_calls"],
                                        }
                                    
                                    # Reasoning
                                    if "reasoning" in delta:
                                        yield {
                                            "type": "reasoning",
                                            "data": delta["reasoning"],
                                        }
                                    
                            except json.JSONDecodeError:
                                continue
                                
        except httpx.HTTPError as e:
            logger.error("Erro no streaming OpenRouter", error=str(e))
            yield {"type": "error", "data": str(e)}
    
    def get_model_groups(self) -> list[dict[str, Any]]:
        """Retorna lista de grupos de modelos disponíveis"""
        return [
            {
                "group_id": group.value,
                "name": config["name"],
                "description": config["description"],
                "recommended_models": config["recommended_models"],
                "use_cases": config["use_cases"],
                "default_temperature": config.get("default_temperature"),
                "default_reasoning_effort": config.get("default_reasoning_effort"),
            }
            for group, config in MODEL_GROUPS_CONFIG.items()
        ]
    
    def get_recommended_model(self, group: ModelGroup) -> str:
        """Retorna o primeiro modelo recomendado para um grupo"""
        config = MODEL_GROUPS_CONFIG.get(group)
        if config and config["recommended_models"]:
            return config["recommended_models"][0]
        return "openai/gpt-4o-mini"  # Default
    
    def get_default_params_for_group(self, group: ModelGroup) -> dict[str, Any]:
        """Retorna parâmetros padrão para um grupo de modelos"""
        config = MODEL_GROUPS_CONFIG.get(group)
        if not config:
            return {"temperature": 0.7}
        
        params = {}
        if config.get("default_temperature"):
            params["temperature"] = config["default_temperature"]
        if config.get("default_reasoning_effort"):
            params["reasoning_effort"] = config["default_reasoning_effort"]
        
        return params


async def get_llm_service(tenant_id: UUID, user_id: Optional[UUID] = None) -> LLMService:
    """Factory para obter instância do LLMService"""
    return LLMService(tenant_id=tenant_id, user_id=user_id)
