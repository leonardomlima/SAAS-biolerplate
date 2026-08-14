from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from app.models.agent import AgentType, ModelProvider, ReasoningEffort


# ============ SCHEMAS DE AGENTE ============

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    agent_type: AgentType = Field(default=AgentType.CHAT)
    
    # Configurações do modelo
    provider: ModelProvider = Field(default=ModelProvider.OPENROUTER)
    model_name: str = Field(default="openai/gpt-4o-mini")
    system_prompt: Optional[str] = Field(default=None)
    
    # Parâmetros de geração
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    reasoning_effort: Optional[ReasoningEffort] = Field(default=None)
    reasoning_summary: bool = Field(default=False)
    max_tokens: int = Field(default=2048, ge=100, le=32000)
    top_p: float = Field(default=1.0, ge=0, le=1)
    
    # Grupos de modelos
    model_group: Optional[str] = Field(default=None)
    
    # Tools habilitadas
    enabled_tools: Optional[List[str]] = Field(default=None)
    
    # Configurações Text2SQL
    allowed_tables: Optional[List[str]] = Field(default=None)
    read_only: bool = Field(default=True)
    
    is_active: bool = Field(default=True)


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    agent_type: Optional[AgentType] = Field(default=None)
    provider: Optional[ModelProvider] = Field(default=None)
    model_name: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    reasoning_effort: Optional[ReasoningEffort] = Field(default=None)
    reasoning_summary: Optional[bool] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None, ge=100, le=32000)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    model_group: Optional[str] = Field(default=None)
    enabled_tools: Optional[List[str]] = Field(default=None)
    allowed_tables: Optional[List[str]] = Field(default=None)
    read_only: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class AgentResponse(AgentBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ SCHEMAS DE SESSÃO E MENSAGEM ============

class MessageBase(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system|tool)$")
    content: str
    
    # Para mensagens de tool
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[str] = None
    
    # Metadados de raciocínio
    reasoning_summary: Optional[str] = None
    reasoning_effort_used: Optional[ReasoningEffort] = None
    
    # Tokens e custos
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None


class MessageCreate(MessageBase):
    session_id: UUID


class MessageResponse(MessageBase):
    id: UUID
    tenant_id: UUID
    session_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatSessionCreate(ChatSessionBase):
    agent_id: UUID


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ChatSessionResponse(ChatSessionBase):
    id: UUID
    tenant_id: UUID
    agent_id: UUID
    user_id: UUID
    redis_key: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = None
    
    class Config:
        from_attributes = True


# ============ SCHEMAS DE CHAT (REQUEST/RESPONSE) ============

class ChatMessageRequest(BaseModel):
    """Requisição para enviar mensagem ao agente"""
    message: str = Field(..., min_length=1, max_length=50000)
    session_id: Optional[UUID] = None  # Se None, cria nova sessão
    stream: bool = Field(default=False)
    
    # Override de parâmetros para esta mensagem específica
    override_temperature: Optional[float] = Field(default=None, ge=0, le=2)
    override_reasoning_effort: Optional[ReasoningEffort] = Field(default=None)
    override_max_tokens: Optional[int] = Field(default=None, ge=100, le=32000)


class ChatMessageResponse(BaseModel):
    """Resposta de mensagem do agente"""
    message_id: UUID
    session_id: UUID
    content: str
    reasoning_summary: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: Optional[float] = None
    created_at: datetime


class ChatStreamChunk(BaseModel):
    """Chunk para streaming de resposta"""
    type: str  # "content", "reasoning", "tool_call", "done", "error"
    data: Any
    message_id: Optional[UUID] = None
    session_id: Optional[UUID] = None


# ============ SCHEMAS DE TOOL ============

class ToolDefinitionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    parameters_schema: Dict[str, Any]
    handler_method: str
    category: str = Field(default="general", max_length=50)
    tags: List[str] = Field(default_factory=list)
    requires_auth: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60)
    is_active: bool = Field(default=True)


class ToolDefinitionCreate(ToolDefinitionBase):
    tenant_id: Optional[UUID] = None


class ToolDefinitionResponse(ToolDefinitionBase):
    id: UUID
    tenant_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    session_id: Optional[UUID] = None


class ToolExecutionResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: int


# ============ SCHEMAS ESPECÍFICOS PARA TEXT2SQL ============

class Text2SQLRequest(BaseModel):
    """Requisição para query em linguagem natural"""
    question: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[UUID] = None
    include_explanation: bool = Field(default=True)
    max_results: int = Field(default=100, ge=1, le=1000)


class Text2SQLResponse(BaseModel):
    """Resposta de query Text2SQL"""
    query_id: UUID
    natural_language_question: str
    generated_sql: str
    explanation: Optional[str] = None
    results: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: int
    columns: List[str]
    created_at: datetime


class SQLValidationRequest(BaseModel):
    """Validação manual de SQL gerado"""
    sql: str
    agent_id: UUID


class SQLValidationResponse(BaseModel):
    is_valid: bool
    is_read_only: bool
    tables_accessed: List[str]
    warnings: List[str]
    error: Optional[str] = None


# ============ SCHEMAS DE GRUPOS DE MODELOS ============

class ModelGroupInfo(BaseModel):
    """Informações sobre um grupo de modelos"""
    group_id: str
    name: str
    description: str
    recommended_models: List[str]
    use_cases: List[str]
    default_temperature: Optional[float] = None
    default_reasoning_effort: Optional[ReasoningEffort] = None


class ModelInfo(BaseModel):
    """Informações sobre um modelo específico"""
    model_id: str
    name: str
    provider: str
    context_window: int
    supports_tools: bool
    supports_vision: bool
    supports_reasoning: bool
    pricing_input_usd: Optional[float] = None
    pricing_output_usd: Optional[float] = None
    groups: List[str] = Field(default_factory=list)


# ============ SCHEMAS DE PESQUISA E FILTRO ============

class AgentListFilters(BaseModel):
    """Filtros para listagem de agentes"""
    agent_type: Optional[AgentType] = None
    model_group: Optional[str] = None
    provider: Optional[ModelProvider] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Resposta paginada genérica"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_more: bool
