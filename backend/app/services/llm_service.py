"""
Serviço de LLM com suporte a múltiplos provedores via OpenRouter.
Gerencia parâmetros específicos para diferentes famílias de modelos.
"""

import httpx
from typing import Optional, Any
from app.core.config import settings


class ModelCapabilities:
    """Capabilidades e parâmetros suportados por diferentes modelos"""
    
    # Modelos que usam reasoning_effort em vez de temperature
    REASONING_MODELS = {
        "o1", "o1-pro", "o1-mini", "o3", "o3-mini",
        "claude-3.7-sonnet-thinking", "claude-3.5-sonnet-thinking"
    }
    
    # Grupos de modelos especializados
    MODEL_GROUPS = {
        "reasoning": [
            "openai/o1-pro",
            "openai/o3-mini",
            "anthropic/claude-3.7-sonnet-thinking",
            "google/gemini-2.0-flash-thinking-exp",
        ],
        "creative": [
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-haiku",
            "google/gemini-2.0-flash",
        ],
        "coding": [
            "deepseek/deepseek-coder-v3",
            "openai/gpt-4-turbo",
            "anthropic/claude-3.5-sonnet",
            "qwen/qwen-2.5-coder-32b-instruct",
        ],
        "fast": [
            "meta-llama/llama-3-8b-instruct",
            "google/gemma-2-9b-it",
            "mistral/mistral-7b-instruct",
            "openai/gpt-4o-mini",
        ],
    }
    
    @classmethod
    def is_reasoning_model(cls, model_name: str) -> bool:
        """Verifica se o modelo usa reasoning_effort em vez de temperature"""
        model_lower = model_name.lower()
        return any(reasoning in model_lower for reasoning in cls.REASONING_MODELS)
    
    @classmethod
    def get_model_group(cls, model_name: str) -> Optional[str]:
        """Retorna o grupo do modelo (reasoning, creative, coding, fast)"""
        for group, models in cls.MODEL_GROUPS.items():
            if any(model in model_name.lower() for model in models):
                return group
        return None
    
    @classmethod
    def get_models_by_group(cls, group: str) -> list[str]:
        """Retorna lista de modelos para um grupo específico"""
        return cls.MODEL_GROUPS.get(group, [])
    
    @classmethod
    def get_all_models(cls) -> list[str]:
        """Retorna todos os modelos disponíveis"""
        all_models = []
        for models in cls.MODEL_GROUPS.values():
            all_models.extend(models)
        return list(set(all_models))


class LLMService:
    """Serviço para chamadas a LLMs via OpenRouter"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
    
    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.PROJECT_NAME,
            "X-Title": settings.PROJECT_NAME,
        }
    
    def _prepare_parameters(
        self,
        model_name: str,
        temperature: Optional[float] = None,
        reasoning_effort: Optional[str] = None,
        reasoning_summary: bool = False,
        max_tokens: int = 2048,
        top_p: float = 1.0,
    ) -> dict[str, Any]:
        """
        Prepara parâmetros da chamada baseado no tipo de modelo.
        
        Para modelos de raciocínio (o1, claude-thinking):
            - Usa reasoning_effort em vez de temperature
            - Suporta reasoning_summary para Chain of Thought
        
        Para modelos tradicionais:
            - Usa temperature normalmente
        """
        params: dict[str, Any] = {
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        
        is_reasoning = ModelCapabilities.is_reasoning_model(model_name)
        
        if is_reasoning:
            # Modelos de raciocínio não aceitam temperature
            if reasoning_effort:
                params["reasoning_effort"] = reasoning_effort
            
            # Alguns modelos suportam reasoning_summary
            if reasoning_summary and "claude" in model_name.lower():
                params["thinking"] = {"type": "enabled"}
        else:
            # Modelos tradicionais usam temperature
            if temperature is not None:
                params["temperature"] = temperature
        
        return params
    
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model_name: str = "openai/gpt-4o-mini",
        temperature: Optional[float] = 0.7,
        reasoning_effort: Optional[str] = None,
        reasoning_summary: bool = False,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        tool_choice: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Realiza chamada de chat completion.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            model_name: Nome do modelo (ex: "openai/gpt-4o-mini")
            temperature: Temperatura para modelos tradicionais
            reasoning_effort: Nível de esforço de raciocínio (low/medium/high)
            reasoning_summary: Habilitar resumo do raciocínio (CoT)
            max_tokens: Máximo de tokens na resposta
            top_p: Top-p sampling
            system_prompt: Prompt de sistema opcional
            tools: Lista de ferramentas disponíveis
            tool_choice: Escolha de ferramenta ("auto", "none", "required", ou nome específico)
        
        Returns:
            Dict com resposta da API incluindo choice, usage, cost
        """
        # Preparar mensagens com system prompt se existir
        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)
        
        # Preparar parâmetros específicos do modelo
        parameters = self._prepare_parameters(
            model_name=model_name,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            reasoning_summary=reasoning_summary,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        
        payload = {
            "model": model_name,
            "messages": final_messages,
            **parameters,
        }
        
        # Adicionar tools se fornecidas
        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
        
        # Extrair informações de custo e uso
        usage = result.get("usage", {})
        cost = result.get("cost", 0.0)
        
        return {
            "content": result["choices"][0]["message"]["content"],
            "role": result["choices"][0]["message"]["role"],
            "tool_calls": result["choices"][0]["message"].get("tool_calls"),
            "reasoning_summary": result["choices"][0]["message"].get("reasoning_summary"),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "cost_usd": cost,
            "model": result.get("model", model_name),
            "raw_response": result,
        }
    
    async def stream_chat_completion(
        self,
        messages: list[dict[str, str]],
        model_name: str = "openai/gpt-4o-mini",
        temperature: Optional[float] = 0.7,
        reasoning_effort: Optional[str] = None,
        reasoning_summary: bool = False,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict]] = None,
    ):
        """
        Realiza chamada de chat completion com streaming.
        
        Yields:
            Chunks da resposta do modelo
        """
        # Implementação similar à chat_completion mas com stream=True
        # e processamento de Server-Sent Events
        pass
    
    def get_recommended_params(self, model_name: str) -> dict[str, Any]:
        """
        Retorna parâmetros recomendados para um modelo específico.
        
        Útil para configurar automaticamente a UI baseada no modelo selecionado.
        """
        is_reasoning = ModelCapabilities.is_reasoning_model(model_name)
        
        if is_reasoning:
            return {
                "use_reasoning_effort": True,
                "temperature_visible": False,
                "reasoning_effort_default": "medium",
                "reasoning_summary_supported": "claude" in model_name.lower(),
            }
        else:
            return {
                "use_reasoning_effort": False,
                "temperature_visible": True,
                "temperature_default": 0.7,
                "reasoning_summary_supported": False,
            }
