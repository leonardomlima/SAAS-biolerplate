# 🤖 Módulo de IA - Guia Completo

Guia detalhado para uso do módulo de Inteligência Artificial do SaaS Boilerplate Pro.

## Índice

1. [Visão Geral](#visão-geral)
2. [Configuração Inicial](#configuração-inicial)
3. [Criando Agentes](#criando-agentes)
4. [Grupos de Modelos](#grupos-de-modelos)
5. [Tools Disponíveis](#tools-disponíveis)
6. [Text2SQL](#text2sql)
7. [Gerenciamento de Contexto](#gerenciamento-de-contexto)
8. [Melhores Práticas](#melhores-práticas)
9. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O módulo de IA fornece:

- **Chat com Agentes**: Conversas contextuais com histórico persistente
- **Agentes Especializados**: Configurações customizadas por caso de uso
- **Text2SQL**: Análise de dados em linguagem natural
- **20+ Tools Integradas**: Funcionalidades estendidas via function calling
- **Multi-Modelo**: Acesso a 100+ modelos via OpenRouter
- **Contexto Redis**: Buffer de sessão ativo com controle de custos

### Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│  API (FastAPI)│────▶│ LLM Service │
│  (React)    │◀────│  + Auth/RBAC  │◀────│ (OpenRouter)│
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │Tool Executor │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  PostgreSQL   │ │    Redis      │ │  External APIs│
│ (Histórico)   │ │  (Contexto)   │ │  (Web, Email) │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## Configuração Inicial

### 1. Obter API Key do OpenRouter

1. Acesse [openrouter.ai](https://openrouter.ai/)
2. Crie uma conta
3. Vá para "Keys" e gere uma nova chave
4. Copie a chave para seu `.env`:

```bash
OPENROUTER_API_KEY=sk_or_xxxxxxxxxxxxx
```

### 2. Configurar Variáveis de Ambiente

```bash
# .env
OPENROUTER_API_KEY=sk_or_xxx
DATABASE_URL=postgresql://postgres:postgres@db:5432/saas_boilerplate
REDIS_URL=redis://redis:6379/0

# Opcional: Limitar gastos mensais
OPENROUTER_MONTHLY_LIMIT_USD=50.00
```

### 3. Executar Migrations

```bash
docker-compose exec backend alembic upgrade head
```

Isso cria as tabelas:
- `agents` - Definições de agentes
- `chat_sessions` - Sessões de conversa
- `messages` - Histórico de mensagens
- `tool_definitions` - Tools disponíveis

---

## Criando Agentes

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/ai/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente de Suporte",
    "description": "Agente especializado em atendimento ao cliente",
    "agent_type": "chat",
    "model_name": "openai/gpt-4o-mini",
    "model_group": "balanced",
    "temperature": 0.7,
    "system_prompt": "Você é um assistente de suporte prestativo...",
    "enabled_tools": ["search_knowledge_base", "get_user_profile"]
  }'
```

### Via Python (SDK)

```python
from app.models.agent import AgentType, ModelProvider, ReasoningEffort

# Agente de Chat Geral
agent = await agent_crud.create(
    db,
    obj_in={
        "name": "Assistente Geral",
        "agent_type": AgentType.CHAT,
        "model_name": "openai/gpt-4o-mini",
        "model_group": "balanced",
        "temperature": 0.7,
        "system_prompt": "Você é um assistente útil e amigável.",
        "enabled_tools": ["search_knowledge_base", "get_user_profile"],
    },
    tenant_id=tenant_id,
)

# Agente de Raciocínio Complexo (usa reasoning_effort)
agent_reasoning = await agent_crud.create(
    db,
    obj_in={
        "name": "Analista de Dados",
        "agent_type": AgentType.TEXT2SQL,
        "model_name": "openai/o1-pro",
        "model_group": "reasoning",
        "reasoning_effort": ReasoningEffort.HIGH,
        "reasoning_summary": True,
        "allowed_tables": ["users", "subscriptions", "payments"],
        "read_only": True,
    },
    tenant_id=tenant_id,
)

# Agente de Código
agent_coding = await agent_crud.create(
    db,
    obj_in={
        "name": "Code Assistant",
        "agent_type": AgentType.CHAT,
        "model_name": "deepseek/deepseek-coder-v2",
        "model_group": "coding",
        "temperature": 0.2,
        "system_prompt": "Você é um desenvolvedor sênior especializado em Python e TypeScript.",
        "enabled_tools": ["generate_code_snippet", "debug_error_log"],
    },
    tenant_id=tenant_id,
)
```

### Parâmetros Importantes

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `model_name` | string | Nome do modelo (ex: `openai/gpt-4o-mini`) |
| `model_group` | string | Grupo especializado (`reasoning`, `creative`, `coding`, `fast`, `balanced`) |
| `temperature` | float | Criatividade (0.0-2.0). Ignorado para modelos o1 |
| `reasoning_effort` | enum | Nível de raciocínio (`low`, `medium`, `high`). Apenas modelos o1 |
| `reasoning_summary` | bool | Incluir resumo do Chain of Thought |
| `system_prompt` | string | Instruções de comportamento do agente |
| `enabled_tools` | list | Tools habilitadas para este agente |
| `allowed_tables` | list | Tabelas permitidas para Text2SQL |
| `read_only` | bool | Restringir a queries SELECT (Text2SQL) |

---

## Grupos de Modelos

Os grupos simplificam a escolha do modelo ideal para cada caso de uso.

### Reasoning (Raciocínio Complexo)

**Casos de Uso:**
- Análise de dados complexa
- Resolução de problemas matemáticos
- Planejamento estratégico
- Debug de código complexo

**Modelos Sugeridos:**
- `openai/o1-pro`
- `openai/o1-mini`
- `anthropic/claude-3.7-sonnet-thinking`
- `deepseek/deepseek-r1`

**Parâmetros Padrão:**
```python
{
    "reasoning_effort": ReasoningEffort.HIGH,
    "temperature": None,  # Não usado
    "reasoning_summary": True,
}
```

### Creative (Criatividade)

**Casos de Uso:**
- Copywriting e marketing
- Redação de blogs e artigos
- Brainstorming de ideias
- Tradução criativa

**Modelos Sugeridos:**
- `openai/gpt-4o`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-pro-1.5`

**Parâmetros Padrão:**
```python
{
    "temperature": 0.8,
    "reasoning_effort": None,
}
```

### Coding (Programação)

**Casos de Uso:**
- Geração de código
- Code review
- Refatoração
- Documentação técnica

**Modelos Sugeridos:**
- `deepseek/deepseek-coder-v2`
- `openai/gpt-4-turbo`
- `anthropic/claude-3.5-sonnet`
- `qwen/qwen-2.5-coder`

**Parâmetros Padrão:**
```python
{
    "temperature": 0.2,
    "reasoning_effort": None,
}
```

### Fast (Rápido e Barato)

**Casos de Uso:**
- Classificação de texto
- Extração de entidades
- Respostas rápidas
- Pré-processamento

**Modelos Sugeridos:**
- `meta-llama/llama-3-8b-instruct`
- `google/gemma-7b`
- `mistral/mistral-7b-instruct`
- `openai/gpt-3.5-turbo`

**Parâmetros Padrão:**
```python
{
    "temperature": 0.5,
    "reasoning_effort": None,
}
```

### Balanced (Equilibrado)

**Casos de Uso:**
- Chatbots gerais
- Assistentes virtuais
- Análise moderada
- Uso diário

**Modelos Sugeridos:**
- `openai/gpt-4o-mini`
- `anthropic/claude-3-haiku`
- `google/gemini-flash-1.5`

**Parâmetros Padrão:**
```python
{
    "temperature": 0.7,
    "reasoning_effort": None,
}
```

---

## Tools Disponíveis

### Produtividade & Dados

#### 1. `search_knowledge_base`
Busca na base de conhecimento da organização.

```json
{
  "name": "search_knowledge_base",
  "description": "Busca documentos e artigos na base de conhecimento",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "limit": {"type": "integer", "default": 5}
    },
    "required": ["query"]
  }
}
```

#### 2. `query_database_sql`
Executa queries SQL seguras (somente leitura).

```json
{
  "name": "query_database_sql",
  "description": "Executa query SQL com tenant isolation",
  "parameters": {
    "type": "object",
    "properties": {
      "sql_query": {"type": "string"}
    },
    "required": ["sql_query"]
  }
}
```

#### 3. `get_user_profile`
Obtém perfil do usuário atual.

#### 4. `list_organization_members`
Lista membros da organização.

#### 5. `fetch_webhook_logs`
Busca logs de webhooks de billing.

### Web & Pesquisa

#### 6. `web_search`
Pesquisa na web via DuckDuckGo/SerpAPI.

#### 7. `scrape_website`
Extrai conteúdo de URLs.

#### 8. `check_competitor_pricing`
Monitora preços de concorrentes.

#### 9. `translate_text`
Traduz entre 100+ idiomas.

#### 10. `summarize_url`
Resume artigos e páginas web.

### Criação & Desenvolvimento

#### 11. `generate_code_snippet`
Gera código em múltiplas linguagens.

#### 12. `debug_error_log`
Analisa logs de erro e sugere fixes.

#### 13. `create_html_email`
Cria templates HTML para emails.

#### 14. `generate_survey_questions`
Gera perguntas para pesquisas.

#### 15. `seo_analyzer`
Analisa SEO de páginas web.

### Automação & Ação

#### 16. `send_email_draft`
Envia rascunho de email via Brevo.

#### 17. `create_calendar_event`
Cria eventos no Google Calendar.

#### 18. `calculate_financials`
Realiza cálculos financeiros complexos.

#### 19. `generate_image_prompt`
Cria prompts para DALL-E/Midjourney.

#### 20. `sentiment_analysis`
Analisa sentimento de textos.

---

## Text2SQL

### Visão Geral

O agente Text2SQL permite que analistas façam perguntas em linguagem natural e recebam:
- Query SQL gerada automaticamente
- Resultados da execução
- Explicação da query
- Isolamento automático por tenant

### Exemplo de Uso

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/text2sql \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual o MRR total por plano nos últimos 3 meses?",
    "agent_id": "uuid-do-agente-text2sql"
  }'
```

**Response:**
```json
{
  "question": "Qual o MRR total por plano nos últimos 3 meses?",
  "sql_query": "SELECT p.name, SUM(s.amount) as mrr FROM subscriptions s JOIN plans p ON s.plan_id = p.id WHERE s.status = 'active' AND s.created_at >= NOW() - INTERVAL '3 months' AND s.tenant_id = 'xxx' GROUP BY p.name",
  "results": [
    {"name": "Basic", "mrr": 1500.00},
    {"name": "Pro", "mrr": 4500.00},
    {"name": "Enterprise", "mrr": 12000.00}
  ],
  "explanation": "Query calcula MRR somando valores de assinaturas ativas dos últimos 3 meses, agrupadas por plano",
  "columns": ["name", "mrr"]
}
```

### Segurança

O Text2SQL implementa:
1. **Tenant Isolation**: Todas as queries incluem `WHERE tenant_id = 'xxx'`
2. **Read-Only**: Apenas queries SELECT são permitidas
3. **Schema Validation**: Validação das tabelas antes da execução
4. **Rate Limiting**: Limite de requisições por minuto
5. **Query Timeout**: Máximo de 30 segundos de execução

### Configurando Tables Permitidas

```python
agent = await agent_crud.create(
    db,
    obj_in={
        "name": "Analista Financeiro",
        "agent_type": AgentType.TEXT2SQL,
        "model_name": "openai/o1-pro",
        "allowed_tables": [
            "subscriptions",
            "payments",
            "plans",
            "invoices"
        ],
        "read_only": True,
    },
    tenant_id=tenant_id,
)
```

---

## Gerenciamento de Contexto

### Redis para Contexto de Sessão

O contexto ativo é mantido no Redis para:
- **Baixa latência**: Acesso rápido ao histórico recente
- **Controle de custos**: LRU para limitar tokens
- **Escalabilidade**: Sessões distribuídas

### Estrutura de Chaves

```
chat:session:{session_id}:context
chat:session:{session_id}:messages
chat:user:{user_id}:active_sessions
```

### Configuração de Contexto

```python
# Número máximo de mensagens no contexto ativo
CONTEXT_MAX_MESSAGES = 20

# TTL para sessões inativas (24 horas)
SESSION_TTL_SECONDS = 86400

# Tamanho máximo do contexto em tokens
CONTEXT_MAX_TOKENS = 4000
```

### Persistência de Longo Prazo

O histórico completo é persistido no PostgreSQL:
- Tabela `messages` com todas as interações
- Metadados de tokens e custos
- Ferramentas executadas e resultados

---

## Melhores Práticas

### 1. Escolha do Modelo

- Use **modelos fast** para tarefas simples e alto volume
- Use **modelos reasoning** apenas quando necessário (custo mais alto)
- Teste diferentes modelos para seu caso de uso específico

### 2. Otimização de Custos

```python
# Configure limites de tokens
agent.max_tokens = 1000  # Evite respostas muito longas

# Use temperature baixa para tarefas objetivas
agent.temperature = 0.2  # Mais consistente, menos criativo

# Habilite reasoning_summary apenas para debugging
agent.reasoning_summary = False  # Economia de tokens
```

### 3. System Prompts Eficazes

```python
# Ruim: Muito genérico
system_prompt = "Seja útil."

# Bom: Específico e com contexto
system_prompt = """
Você é um especialista em suporte técnico para SaaS B2B.
- Responda de forma clara e concisa
- Use exemplos práticos quando possível
- Se não souber, diga claramente
- Mantenha tom profissional mas amigável
"""
```

### 4. Tools e Permissões

- Habilite apenas tools necessárias para cada agente
- Use `requires_auth=True` para tools sensíveis
- Configure rate limits adequados por tool

### 5. Monitoramento

```python
# Acompanhe custos por agente
total_cost = sum(msg.cost_usd for msg in messages)

# Monitore uso de tokens
avg_tokens = sum(msg.total_tokens for msg in messages) / len(messages)

# Identifique agents mais usados
popular_agents = await agent_crud.get_most_used(db, tenant_id)
```

---

## Troubleshooting

### Problema: Erro "OPENROUTER_API_KEY não configurada"

**Solução:**
```bash
# Verifique se a variável está no .env
grep OPENROUTER_API_KEY .env

# Reinicie o backend
docker-compose restart backend
```

### Problema: Modelo retorna erro de capacidade

**Solução:**
- O modelo pode estar sobrecarregado
- Tente um modelo alternativo do mesmo grupo
- Implemente retry com backoff exponencial

### Problema: Text2SQL gera query incorreta

**Solução:**
1. Verifique se o schema das tabelas está correto
2. Adicione mais contexto no system prompt
3. Use modelo de reasoning (o1-pro) para queries complexas
4. Revise as tabelas permitidas

### Problema: Contexto muito longo excede limite de tokens

**Solução:**
```python
# Reduza CONTEXT_MAX_MESSAGES
CONTEXT_MAX_MESSAGES = 10

# Implemente summarization do histórico
# (manter apenas últimas N mensagens + resumo das anteriores)
```

### Problema: Tool execution falha

**Solução:**
- Verifique permissões do tenant
- Valide parâmetros da tool
- Confira logs de erro no Sentry
- Teste a tool isoladamente

---

## Recursos Adicionais

- [Documentação OpenRouter](https://openrouter.ai/docs)
- [Exemplos de Prompts](https://github.com/openai/openai-cookbook)
- [Best Practices for LLM Apps](https://docs.anthropic.com/claude/docs/best-practices)

---

<div align="center">

**Precisa de ajuda?** [Abra uma issue](https://github.com/yourorg/saas-boilerplate-pro/issues) ou entre no [Discord](https://discord.gg/xxxxx)

</div>
