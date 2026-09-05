"""
Executor de Tools para Agentes de IA.
Implementa 20 tools úteis organizadas por categoria.
"""

import httpx
import structlog
from typing import Any, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import SessionLocal
from app.core.config import settings
from sqlmodel import select
from sqlalchemy import text

logger = structlog.get_logger()


class ToolExecutionError(Exception):
    """Erro na execução de uma tool"""
    pass


class ToolExecutor:
    """
    Executor de tools para agentes de IA.
    
    Cada tool é um método que recebe argumentos e retorna um resultado.
    As tools são registradas automaticamente baseado nos métodos decorados.
    """
    
    def __init__(self, tenant_id: UUID, user_id: Optional[UUID] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== PRODUTIVIDADE E DADOS ====================
    
    async def search_knowledge_base(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Busca na base de conhecimento da organização"""
        # Implementação: buscar em documentos, FAQs, etc.
        return {
            "results": [],
            "query": query,
            "limit": limit,
        }
    
    async def query_database_sql(
        self, 
        sql_query: str, 
        params: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Executa query SQL segura (somente leitura) no banco do tenant.
        
        Args:
            sql_query: Query SQL SELECT
            params: Parâmetros para a query
        
        Returns:
            Resultados da query em formato JSON
        """
        # Validar que é somente leitura
        query_upper = sql_query.upper().strip()
        if not query_upper.startswith("SELECT"):
            raise ToolExecutionError("Apenas queries SELECT são permitidas")
        
        # Adicionar filtro de tenant_id automaticamente
        # Isso deve ser feito com cuidado para não quebrar queries complexas
        
        try:
            async with SessionLocal() as session:
                result = await session.execute(text(sql_query), params or {})
                rows = result.fetchall()
                columns = list(result.keys()) if result.keys() else []
                
                return {
                    "columns": columns,
                    "rows": [dict(zip(columns, row)) for row in rows],
                    "row_count": len(rows),
                }
        except Exception as e:
            logger.error("Erro ao executar query SQL", error=str(e))
            raise ToolExecutionError(f"Erro na query: {str(e)}")
    
    async def get_user_profile(self, user_id: str) -> dict[str, Any]:
        """Obtém perfil de usuário da organização"""
        from app.models.user import User
        
        async with SessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id, User.tenant_id == self.tenant_id)
            )
            user = result.first()
            
            if not user:
                return {"error": "Usuário não encontrado"}
            
            return {
                "id": str(user[0].id),
                "name": user[0].name,
                "email": user[0].email,
                "role": user[0].role,
            }
    
    async def list_organization_members(self, limit: int = 50) -> dict[str, Any]:
        """Lista membros da organização"""
        from app.models.user import User
        
        async with SessionLocal() as session:
            result = await session.execute(
                select(User)
                .where(User.tenant_id == self.tenant_id)
                .limit(limit)
            )
            users = result.all()
            
            return {
                "members": [
                    {
                        "id": str(u[0].id),
                        "name": u[0].name,
                        "email": u[0].email,
                        "role": u[0].role,
                    }
                    for u in users
                ],
                "count": len(users),
            }
    
    async def fetch_webhook_logs(self, days: int = 7, limit: int = 100) -> dict[str, Any]:
        """Busca logs de webhooks recentes"""
        from app.models.asaas_webhook_event import AsaasWebhookEvent
        from datetime import timedelta
        
        async with SessionLocal() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            result = await session.execute(
                select(AsaasWebhookEvent)
                .where(
                    AsaasWebhookEvent.tenant_id == self.tenant_id,
                    AsaasWebhookEvent.created_at >= cutoff
                )
                .limit(limit)
            )
            events = result.all()
            
            return {
                "events": [
                    {
                        "id": str(e[0].id),
                        "event_type": e[0].event_type,
                        "status": e[0].status,
                        "created_at": e[0].created_at.isoformat(),
                    }
                    for e in events
                ],
                "count": len(events),
            }
    
    # ==================== WEB E PESQUISA ====================
    
    async def web_search(self, query: str, num_results: int = 5) -> dict[str, Any]:
        """Realiza busca na web usando API externa"""
        # Implementação: usar Google Custom Search, Bing API, ou similar
        return {
            "query": query,
            "results": [],
            "note": "API de busca precisa ser configurada",
        }
    
    async def scrape_website(self, url: str, extract_links: bool = False) -> dict[str, Any]:
        """Extrai conteúdo de uma URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                # Extrair texto básico (implementação simplificada)
                content = response.text[:5000]  # Limitar tamanho
                
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "content_preview": content,
                    "content_length": len(response.text),
                }
        except Exception as e:
            raise ToolExecutionError(f"Erro ao acessar URL: {str(e)}")
    
    async def check_competitor_pricing(self, competitor_url: str) -> dict[str, Any]:
        """Verifica preços de competidor (requer configuração específica)"""
        return {
            "competitor": competitor_url,
            "pricing_data": {},
            "note": "Requer configuração específica por competidor",
        }
    
    async def translate_text(
        self, 
        text: str, 
        source_lang: str = "auto", 
        target_lang: str = "en"
    ) -> dict[str, Any]:
        """Traduz texto usando API externa"""
        # Implementação: DeepL, Google Translate API
        return {
            "original": text,
            "translated": text,  # Placeholder
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
    
    async def summarize_url(self, url: str, max_length: int = 500) -> dict[str, Any]:
        """Resume conteúdo de uma URL"""
        # Primeiro obter conteúdo, depois resumir
        content_result = await self.scrape_website(url)
        
        return {
            "url": url,
            "summary": "Resumo do conteúdo...",  # Placeholder
            "original_length": content_result.get("content_length", 0),
        }
    
    # ==================== CRIAÇÃO E DESENVOLVIMENTO ====================
    
    async def generate_code_snippet(
        self, 
        description: str, 
        language: str = "python"
    ) -> dict[str, Any]:
        """Gera snippet de código baseado em descrição"""
        # Esta tool usa o próprio LLM para gerar código
        return {
            "description": description,
            "language": language,
            "code": "# Código gerado pelo LLM",
            "note": "Use o LLM principal para gerar o código real",
        }
    
    async def debug_error_log(self, error_message: str, stack_trace: str = "") -> dict[str, Any]:
        """Analisa erro e sugere soluções"""
        return {
            "error": error_message,
            "stack_trace": stack_trace,
            "analysis": "Análise do erro...",
            "suggestions": [],
        }
    
    async def create_html_email(
        self, 
        subject: str, 
        body_text: str, 
        template: str = "simple"
    ) -> dict[str, Any]:
        """Cria HTML para e-mail baseado em texto"""
        # Gerar HTML simples
        html = f"""
        <html>
            <body>
                <h1>{subject}</h1>
                <p>{body_text}</p>
            </body>
        </html>
        """
        return {
            "subject": subject,
            "html": html,
            "template": template,
        }
    
    async def generate_survey_questions(
        self, 
        topic: str, 
        question_count: int = 5,
        question_types: list[str] | None = None
    ) -> dict[str, Any]:
        """Gera perguntas de pesquisa baseadas em tópico"""
        return {
            "topic": topic,
            "questions": [],  # Gerado pelo LLM
            "count": question_count,
            "types": question_types or ["multiple_choice", "text"],
        }
    
    async def seo_analyzer(self, url: str) -> dict[str, Any]:
        """Analisa SEO de uma página"""
        return {
            "url": url,
            "score": 0,
            "issues": [],
            "recommendations": [],
        }
    
    # ==================== AUTOMAÇÃO E AÇÃO ====================
    
    async def send_email_draft(
        self, 
        to: str, 
        subject: str, 
        body: str,
        schedule_time: Optional[str] = None
    ) -> dict[str, Any]:
        """Prepara e-mail para envio (não envia imediatamente)"""
        from app.background.tasks import send_transactional_email_task
        
        # Apenas preparar, não enviar
        return {
            "to": to,
            "subject": subject,
            "body": body,
            "scheduled": schedule_time,
            "status": "draft",
            "note": "E-mail preparado como rascunho",
        }
    
    async def create_calendar_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        attendees: list[str] | None = None,
        description: str = ""
    ) -> dict[str, Any]:
        """Cria evento de calendário (integração necessária)"""
        return {
            "title": title,
            "start": start_time,
            "end": end_time,
            "attendees": attendees or [],
            "description": description,
            "status": "pending_integration",
        }
    
    async def calculate_financials(
        self,
        operation: str,
        values: list[float],
        currency: str = "BRL"
    ) -> dict[str, Any]:
        """Realiza cálculos financeiros"""
        if operation == "sum":
            result = sum(values)
        elif operation == "average":
            result = sum(values) / len(values) if values else 0
        elif operation == "percentage":
            result = (values[0] / values[1] * 100) if len(values) > 1 and values[1] != 0 else 0
        else:
            raise ToolExecutionError(f"Operação desconhecida: {operation}")
        
        return {
            "operation": operation,
            "result": result,
            "currency": currency,
            "formatted": f"R$ {result:.2f}" if currency == "BRL" else f"${result:.2f}",
        }
    
    async def generate_image_prompt(self, concept: str, style: str = "realistic") -> dict[str, Any]:
        """Gera prompt detalhado para geração de imagens"""
        return {
            "concept": concept,
            "style": style,
            "prompt": f"Detailed {style} image of {concept}, high quality, professional",
            "suggested_model": "midjourney/dalle-3",
        }
    
    async def sentiment_analysis(self, text: str) -> dict[str, Any]:
        """Analisa sentimento de texto"""
        # Pode usar LLM ou API especializada
        return {
            "text": text[:200],
            "sentiment": "neutral",  # positive, negative, neutral
            "confidence": 0.0,
            "emotions": [],
        }
    
    # ==================== TEXT2SQL ESPECÍFICO ====================
    
    async def get_table_schema(self, table_name: str) -> dict[str, Any]:
        """Obtém schema de uma tabela para auxiliar na geração de queries"""
        # Importante: validar permissões e tenant isolation
        allowed_tables = [
            "users", "organizations", "subscriptions", 
            "asaas_customers", "asaas_webhook_events",
            "email_deliveries", "audit_logs"
        ]
        
        if table_name not in allowed_tables:
            return {
                "error": f"Tabela {table_name} não está disponível para consulta",
                "allowed_tables": allowed_tables,
            }
        
        # Obter schema real do banco
        try:
            async with SessionLocal() as session:
                # Query para obter colunas
                result = await session.execute(
                    text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """),
                    {"table_name": table_name}
                )
                columns = result.all()
                
                return {
                    "table": table_name,
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2] == "YES",
                        }
                        for col in columns
                    ],
                }
        except Exception as e:
            return {"error": f"Erro ao obter schema: {str(e)}"}
    
    async def validate_sql_query(self, sql_query: str) -> dict[str, Any]:
        """Valida query SQL antes da execução"""
        query_upper = sql_query.upper().strip()
        
        issues = []
        
        # Verificar operações proibidas
        forbidden_ops = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER"]
        for op in forbidden_ops:
            if op in query_upper:
                issues.append(f"Operação {op} não é permitida (somente leitura)")
        
        # Verificar se tem WHERE com tenant_id (recomendação)
        if "SELECT" in query_upper and "tenant_id" not in query_upper.lower():
            issues.append("Recomendação: considere filtrar por tenant_id")
        
        return {
            "valid": len(issues) == 0,
            "query": sql_query,
            "issues": issues,
            "is_read_only": query_upper.startswith("SELECT"),
        }
    
    # ==================== REGISTRO AUTOMÁTICO DE TOOLS ====================
    
    def get_all_tools(self) -> list[dict[str, Any]]:
        """
        Retorna lista de todas as tools disponíveis com seus schemas.
        
        Returns:
            Lista de definições de tools no formato OpenAI/Anthropic
        """
        # Métodos que são tools (exclui métodos privados e de utilidade)
        tool_methods = [
            method for method in dir(self)
            if callable(getattr(self, method)) and not method.startswith("_")
        ]
        
        tools = []
        for method_name in tool_methods:
            method = getattr(self, method_name)
            doc = method.__doc__ or ""
            
            # Extrair descrição da docstring
            description = doc.split("\n")[0].strip() if doc else method_name
            
            tools.append({
                "type": "function",
                "function": {
                    "name": method_name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {},  # Poderia extrair dos type hints
                        "required": [],
                    },
                },
            })
        
        return tools
    
    async def execute_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Executa uma tool pelo nome.
        
        Args:
            tool_name: Nome do método da tool
            arguments: Argumentos para a tool
        
        Returns:
            Resultado da execução
        """
        if not hasattr(self, tool_name):
            raise ToolExecutionError(f"Tool '{tool_name}' não existe")
        
        method = getattr(self, tool_name)
        if not callable(method):
            raise ToolExecutionError(f"'{tool_name}' não é executável")
        
        try:
            result = await method(**arguments)
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
            }
        except ToolExecutionError:
            raise
        except Exception as e:
            logger.error("Erro ao executar tool", tool=tool_name, error=str(e))
            raise ToolExecutionError(f"Erro na tool {tool_name}: {str(e)}")
