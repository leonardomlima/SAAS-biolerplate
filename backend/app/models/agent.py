from datetime import UTC, datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB, JSON
from sqlalchemy import Text


class ModelProvider(str, Enum):
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class ReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AgentType(str, Enum):
    CHAT = "chat"
    TEXT2SQL = "text2sql"
    SURVEY = "survey"
    EMAIL = "email"


class Agent(SQLModel, table=True):
    __tablename__ = "agents"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(index=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    agent_type: AgentType = Field(default=AgentType.CHAT)
    
    # Configurações do modelo
    provider: ModelProvider = Field(default=ModelProvider.OPENROUTER)
    model_name: str = Field(default="openai/gpt-4o-mini")
    system_prompt: Optional[str] = Field(default=None)
    
    # Parâmetros de geração - temperature ou reasoning_effort dependendo do modelo
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    reasoning_effort: Optional[ReasoningEffort] = Field(default=None)
    reasoning_summary: bool = Field(default=False)
    max_tokens: int = Field(default=2048)
    top_p: float = Field(default=1.0)
    
    # Configurações específicas para grupos de modelos
    model_group: Optional[str] = Field(default=None, index=True)  # "reasoning", "creative", "coding", "fast"
    
    # Tools habilitadas (armazenado como JSONB)
    enabled_tools: Optional[list[str]] = Field(default=None, sa_type=JSONB)
    
    # Configurações específicas para Text2SQL
    allowed_tables: Optional[list[str]] = Field(default=None, sa_type=JSONB)
    read_only: bool = Field(default=True)
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(index=True)
    agent_id: UUID = Field(foreign_key="agents.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    title: Optional[str] = Field(default=None, max_length=200)
    metadata: dict = Field(default_factory=dict, sa_type=JSON)
    
    # Contexto da sessão no Redis (não persistido aqui)
    redis_key: Optional[str] = Field(default=None, max_length=200)
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    agent: Optional["Agent"] = Relationship(back_populates="sessions")
    messages: List["Message"] = Relationship(back_populates="session")


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(index=True)
    session_id: UUID = Field(foreign_key="chat_sessions.id", index=True)
    
    role: str = Field(index=True)  # "user", "assistant", "system", "tool"
    content: str = Field(sa_type=Text)
    
    # Para mensagens de tool
    tool_call_id: Optional[str] = Field(default=None, max_length=100)
    tool_name: Optional[str] = Field(default=None, max_length=100)
    tool_args: Optional[dict] = Field(default=None, sa_type=JSON)
    tool_result: Optional[str] = Field(default=None, sa_type=Text)
    
    # Metadados de raciocínio (para modelos com CoT)
    reasoning_summary: Optional[str] = Field(default=None, sa_type=Text)
    reasoning_effort_used: Optional[ReasoningEffort] = Field(default=None)
    
    # Tokens e custos
    prompt_tokens: Optional[int] = Field(default=None)
    completion_tokens: Optional[int] = Field(default=None)
    total_tokens: Optional[int] = Field(default=None)
    cost_usd: Optional[float] = Field(default=None)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    session: Optional["ChatSession"] = Relationship(back_populates="messages")


class ToolDefinition(SQLModel, table=True):
    """Definição de tools disponíveis para os agentes"""
    __tablename__ = "tool_definitions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: Optional[UUID] = Field(default=None, index=True)  # NULL = tool global
    
    name: str = Field(index=True, unique=True)
    description: str = Field(sa_type=Text)
    
    # Schema da tool em JSON Schema format
    parameters_schema: dict = Field(sa_type=JSON)
    
    # Função Python que executa a tool (nome do método no ToolExecutor)
    handler_method: str = Field(max_length=100)
    
    # Categorias para organização
    category: str = Field(default="general", max_length=50)  # "productivity", "web", "data", "automation"
    tags: Optional[list[str]] = Field(default_factory=list, sa_type=JSON)
    
    # Controle de acesso
    requires_auth: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60)
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# Atualizar relacionamento no Agent
Agent.sessions = Relationship(back_populates="agent")
