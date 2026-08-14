"""
Endpoints para funcionalidades de IA: Chat, Agentes e Text2SQL
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.dependencies.auth import get_current_user
from app.models.user import User
from app.models.agent import Agent, ChatSession, Message, AgentType, ModelProvider, ReasoningEffort
from app.crud.agent import agent as agent_crud, chat_session as session_crud, message as message_crud
from app.services.llm_service import LLMService, ModelCapabilities
from app.services.tool_executor import ToolExecutor, ToolExecutionError


router = APIRouter()


# ==================== SCHEMAS ====================

class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: AgentType = AgentType.CHAT
    model_name: str = "openai/gpt-4o-mini"
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    reasoning_effort: Optional[ReasoningEffort] = None
    model_group: Optional[str] = None
    enabled_tools: list[str] = Field(default_factory=list)
    allowed_tables: list[str] = Field(default_factory=list)
    read_only: bool = True


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    reasoning_effort: Optional[ReasoningEffort] = None
    enabled_tools: Optional[list[str]] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    agent_type: AgentType
    model_name: str
    model_group: Optional[str]
    temperature: Optional[float]
    reasoning_effort: Optional[ReasoningEffort]
    enabled_tools: list[str]
    is_active: bool


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[UUID] = None
    agent_id: UUID
    stream: bool = False


class ChatResponse(BaseModel):
    session_id: UUID
    message_id: UUID
    response: str
    reasoning_summary: Optional[str] = None
    tool_calls: Optional[list] = None
    tokens_used: int
    cost_usd: float


class Text2SQLRequest(BaseModel):
    question: str
    agent_id: UUID
    session_id: Optional[UUID] = None


class Text2SQLResponse(BaseModel):
    question: str
    sql_query: str
    results: list[dict]
    explanation: str
    columns: list[str]


# ==================== AGENTES ====================

@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os agentes do tenant"""
    agents = await agent_crud.get_all(db, tenant_id=current_user.tenant_id)
    return [
        AgentResponse(
            id=a[0].id,
            name=a[0].name,
            description=a[0].description,
            agent_type=a[0].agent_type,
            model_name=a[0].model_name,
            model_group=a[0].model_group,
            temperature=a[0].temperature,
            reasoning_effort=a[0].reasoning_effort,
            enabled_tools=a[0].enabled_tools,
            is_active=a[0].is_active,
        )
        for a in agents
    ]


@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo agente"""
    
    # Validar modelo
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OPENROUTER_API_KEY não configurada. Configure no .env"
        )
    
    agent_data = data.model_dump()
    agent = await agent_crud.create(db, obj_in=agent_data, tenant_id=current_user.tenant_id)
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type,
        model_name=agent.model_name,
        model_group=agent.model_group,
        temperature=agent.temperature,
        reasoning_effort=agent.reasoning_effort,
        enabled_tools=agent.enabled_tools,
        is_active=agent.is_active,
    )


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém detalhes de um agente"""
    agent = await agent_crud.get_by_id(db, agent_id=agent_id, tenant_id=current_user.tenant_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado")
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type,
        model_name=agent.model_name,
        model_group=agent.model_group,
        temperature=agent.temperature,
        reasoning_effort=agent.reasoning_effort,
        enabled_tools=agent.enabled_tools,
        is_active=agent.is_active,
    )


@router.patch("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza um agente"""
    agent = await agent_crud.get_by_id(db, agent_id=agent_id, tenant_id=current_user.tenant_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    updated_agent = await agent_crud.update(db, db_obj=agent, obj_in=update_data)
    
    return AgentResponse(
        id=updated_agent.id,
        name=updated_agent.name,
        description=updated_agent.description,
        agent_type=updated_agent.agent_type,
        model_name=updated_agent.model_name,
        model_group=updated_agent.model_group,
        temperature=updated_agent.temperature,
        reasoning_effort=updated_agent.reasoning_effort,
        enabled_tools=updated_agent.enabled_tools,
        is_active=updated_agent.is_active,
    )


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deleta um agente"""
    success = await agent_crud.delete(db, agent_id=agent_id, tenant_id=current_user.tenant_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado")


@router.get("/models/groups")
async def get_model_groups():
    """Retorna grupos de modelos disponíveis"""
    return {
        "reasoning": ModelCapabilities.get_models_by_group("reasoning"),
        "creative": ModelCapabilities.get_models_by_group("creative"),
        "coding": ModelCapabilities.get_models_by_group("coding"),
        "fast": ModelCapabilities.get_models_by_group("fast"),
    }


@router.get("/models/all")
async def get_all_models():
    """Retorna todos os modelos disponíveis"""
    return {"models": ModelCapabilities.get_all_models()}


@router.get("/models/recommended-params/{model_name:path}")
async def get_model_params(model_name: str):
    """Retorna parâmetros recomendados para um modelo"""
    llm = LLMService()
    return llm.get_recommended_params(model_name)


# ==================== CHAT ====================

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Envia mensagem para um agente e recebe resposta"""
    
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OPENROUTER_API_KEY não configurada"
        )
    
    # Obter agente
    agent = await agent_crud.get_by_id(db, agent_id=data.agent_id, tenant_id=current_user.tenant_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado")
    
    # Criar ou obter sessão
    if data.session_id:
        session = await session_crud.get_by_id(db, session_id=data.session_id, tenant_id=current_user.tenant_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada")
    else:
        session = await session_crud.create(
            db,
            obj_in={
                "agent_id": agent.id,
                "user_id": current_user.id,
                "title": data.message[:50],
            },
            tenant_id=current_user.tenant_id,
        )
    
    # Salvar mensagem do usuário
    user_msg = await message_crud.create(
        db,
        obj_in={
            "session_id": session.id,
            "role": "user",
            "content": data.message,
        },
        tenant_id=current_user.tenant_id,
    )
    
    # Obter histórico da sessão (últimas 20 mensagens)
    history = await message_crud.get_session_messages(db, session_id=session.id, tenant_id=current_user.tenant_id, limit=20)
    messages = [{"role": m.role, "content": m.content} for m in history]
    
    # Preparar tools se habilitadas
    tools = None
    if agent.enabled_tools:
        executor = ToolExecutor(tenant_id=current_user.tenant_id, user_id=current_user.id)
        all_tools = executor.get_all_tools()
        tools = [t for t in all_tools if t["function"]["name"] in agent.enabled_tools]
    
    # Chamar LLM
    llm = LLMService()
    response = await llm.chat_completion(
        messages=messages,
        model_name=agent.model_name,
        temperature=agent.temperature,
        reasoning_effort=agent.reasoning_effort.value if agent.reasoning_effort else None,
        reasoning_summary=agent.reasoning_summary,
        max_tokens=agent.max_tokens,
        system_prompt=agent.system_prompt,
        tools=tools,
    )
    
    # Salvar resposta do assistente
    assistant_msg = await message_crud.create(
        db,
        obj_in={
            "session_id": session.id,
            "role": "assistant",
            "content": response["content"],
            "tool_calls": response.get("tool_calls"),
            "reasoning_summary": response.get("reasoning_summary"),
            "prompt_tokens": response.get("prompt_tokens"),
            "completion_tokens": response.get("completion_tokens"),
            "total_tokens": response.get("total_tokens"),
            "cost_usd": response.get("cost_usd"),
        },
        tenant_id=current_user.tenant_id,
    )
    
    return ChatResponse(
        session_id=session.id,
        message_id=assistant_msg.id,
        response=response["content"],
        reasoning_summary=response.get("reasoning_summary"),
        tool_calls=response.get("tool_calls"),
        tokens_used=response.get("total_tokens", 0),
        cost_usd=response.get("cost_usd", 0.0),
    )


@router.get("/chat/sessions")
async def list_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista sessões de chat do usuário"""
    sessions = await session_crud.get_user_sessions(db, user_id=current_user.id, tenant_id=current_user.tenant_id)
    return [
        {
            "id": s.id,
            "title": s.title,
            "agent_id": s.agent_id,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in sessions
    ]


@router.get("/chat/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém mensagens de uma sessão"""
    session = await session_crud.get_by_id(db, session_id=session_id, tenant_id=current_user.tenant_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada")
    
    messages = await message_crud.get_session_messages(db, session_id=session_id, tenant_id=current_user.tenant_id, limit=100)
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
            "tool_name": m.tool_name,
            "tool_result": m.tool_result,
        }
        for m in messages
    ]


@router.delete("/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deleta uma sessão de chat"""
    success = await session_crud.delete(db, session_id=session_id, tenant_id=current_user.tenant_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada")


# ==================== TEXT2SQL ====================

@router.post("/text2sql", response_model=Text2SQLResponse)
async def text2sql_query(
    data: Text2SQLRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Agente especializado em Text2SQL para análise de dados.
    
    O analista faz uma pergunta em linguagem natural e o agente:
    1. Gera query SQL baseada na pergunta
    2. Valida a query (somente leitura)
    3. Executa a query com tenant isolation
    4. Retorna resultados formatados
    """
    
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OPENROUTER_API_KEY não configurada"
        )
    
    # Obter agente especializado em Text2SQL
    agent = await agent_crud.get_by_id(db, agent_id=data.agent_id, tenant_id=current_user.tenant_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado")
    
    # Configurar prompt especializado para Text2SQL
    sql_system_prompt = f"""
Você é um especialista em SQL para análise de dados.
Sua tarefa é converter perguntas em linguagem natural em queries SQL precisas.

Regras IMPORTANTÍSSIMAS:
1. TODAS as queries DEVEM incluir "WHERE tenant_id = '{current_user.tenant_id}'" para isolamento
2. Apenas queries SELECT são permitidas (somente leitura)
3. Use tabelas disponíveis: {', '.join(agent.allowed_tables) if agent.allowed_tables else 'todas as tabelas do schema'}
4. Sempre valide o schema antes de gerar queries
5. Explique a query gerada de forma clara

Responda APENAS no formato JSON:
{{
    "sql_query": "SELECT ...",
    "explanation": "Explicação da query..."
}}
"""
    
    # Obter schemas das tabelas permitidas
    executor = ToolExecutor(tenant_id=current_user.tenant_id)
    table_schemas = {}
    for table in agent.allowed_tables or ["users", "organizations", "subscriptions"]:
        schema = await executor.get_table_schema(table)
        if "columns" in schema:
            table_schemas[table] = schema["columns"]
    
    # Contexto com schemas
    schema_context = "\n".join([
        f"Tabela {table}: {cols}" 
        for table, cols in table_schemas.items()
    ])
    
    full_system_prompt = f"{sql_system_prompt}\n\nSchemas disponíveis:\n{schema_context}"
    
    # Chamar LLM para gerar SQL
    llm = LLMService()
    messages = [{"role": "user", "content": f"Pergunta: {data.question}"}]
    
    response = await llm.chat_completion(
        messages=messages,
        model_name=agent.model_name,
        system_prompt=full_system_prompt,
        temperature=0.1,  # Baixa temperatura para precisão
        max_tokens=1000,
    )
    
    # Parse da resposta (espera-se JSON)
    import json
    try:
        result = json.loads(response["content"])
        sql_query = result.get("sql_query", "")
        explanation = result.get("explanation", "")
    except:
        # Fallback: extrair SQL da resposta
        sql_query = response["content"]
        explanation = "Query gerada pelo LLM"
    
    # Validar query
    validation = await executor.validate_sql_query(sql_query)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query inválida: {validation['issues']}"
        )
    
    # Garantir tenant_id na query (segurança extra)
    if "tenant_id" not in sql_query.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query deve incluir filtro por tenant_id"
        )
    
    # Executar query
    from sqlalchemy import text
    try:
        result = await db.execute(text(sql_query))
        rows = result.fetchall()
        columns = list(result.keys()) if result.keys() else []
        
        formatted_results = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao executar query: {str(e)}"
        )
    
    return Text2SQLResponse(
        question=data.question,
        sql_query=sql_query,
        results=formatted_results,
        explanation=explanation,
        columns=columns,
    )
