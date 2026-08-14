/**
 * Tipos e interfaces para funcionalidades de IA, Chat e Agentes
 */

import { z } from 'zod';

// ==================== ENUMS ====================

export enum AgentType {
  CHAT = 'chat',
  TEXT2SQL = 'text2sql',
  SURVEY = 'survey',
  EMAIL = 'email',
}

export enum ModelProvider {
  OPENROUTER = 'openrouter',
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
  GOOGLE = 'google',
}

export enum ReasoningEffort {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

export enum ModelGroup {
  REASONING = 'reasoning',
  CREATIVE = 'creative',
  CODING = 'coding',
  FAST = 'fast',
  BALANCED = 'balanced',
}

// ==================== SCHEMAS (Zod) ====================

export const agentSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  name: z.string().min(1).max(200),
  description: z.string().max(500).optional().nullable(),
  agent_type: z.nativeEnum(AgentType),
  provider: z.nativeEnum(ModelProvider),
  model_name: z.string(),
  model_group: z.string().optional().nullable(),
  system_prompt: z.string().optional().nullable(),
  temperature: z.number().min(0).max(2).optional().nullable(),
  reasoning_effort: z.nativeEnum(ReasoningEffort).optional().nullable(),
  reasoning_summary: z.boolean().default(false),
  max_tokens: z.number().int().positive().default(2048),
  top_p: z.number().min(0).max(1).default(1),
  enabled_tools: z.array(z.string()).optional().nullable(),
  allowed_tables: z.array(z.string()).optional().nullable(),
  read_only: z.boolean().default(true),
  is_active: z.boolean().default(true),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const chatSessionSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  agent_id: z.string().uuid(),
  user_id: z.string().uuid(),
  title: z.string().max(200).optional().nullable(),
  metadata: z.record(z.unknown()).default({}),
  redis_key: z.string().optional().nullable(),
  is_active: z.boolean().default(true),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  messages: z.array(z.unknown()).optional(),
});

export const messageSchema = z.object({
  id: z.string().uuid().optional(),
  session_id: z.string().uuid(),
  role: z.enum(['user', 'assistant', 'system', 'tool']),
  content: z.string(),
  tool_call_id: z.string().optional().nullable(),
  tool_name: z.string().optional().nullable(),
  tool_args: z.record(z.unknown()).optional().nullable(),
  tool_result: z.string().optional().nullable(),
  reasoning_summary: z.string().optional().nullable(),
  reasoning_effort_used: z.nativeEnum(ReasoningEffort).optional().nullable(),
  prompt_tokens: z.number().int().optional().nullable(),
  completion_tokens: z.number().int().optional().nullable(),
  total_tokens: z.number().int().optional().nullable(),
  cost_usd: z.number().optional().nullable(),
  created_at: z.string().datetime().optional(),
});

export const text2SQLRequestSchema = z.object({
  question: z.string().min(1).max(5000),
  agent_id: z.string().uuid(),
  session_id: z.string().uuid().optional().nullable(),
  include_explanation: z.boolean().default(true),
  max_results: z.number().int().min(1).max(1000).default(100),
});

export const text2SQLResponseSchema = z.object({
  query_id: z.string().uuid().optional(),
  natural_language_question: z.string(),
  generated_sql: z.string(),
  explanation: z.string().optional().nullable(),
  results: z.array(z.record(z.unknown())),
  row_count: z.number().int(),
  execution_time_ms: z.number().int(),
  columns: z.array(z.string()),
  created_at: z.string().datetime().optional(),
});

// ==================== TIPOS DERIVADOS ====================

export type Agent = z.infer<typeof agentSchema>;
export type AgentCreate = Omit<Agent, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>;
export type AgentUpdate = Partial<AgentCreate>;

export type ChatSession = z.infer<typeof chatSessionSchema>;
export type ChatSessionCreate = Omit<ChatSession, 'id' | 'tenant_id' | 'user_id' | 'created_at' | 'updated_at'>;

export type Message = z.infer<typeof messageSchema>;
export type MessageCreate = Omit<Message, 'id' | 'session_id' | 'created_at'>;

export type Text2SQLRequest = z.infer<typeof text2SQLRequestSchema>;
export type Text2SQLResponse = z.infer<typeof text2SQLResponseSchema>;

// ==================== GRUPOS DE MODELOS ====================

export interface ModelGroupInfo {
  group_id: string;
  name: string;
  description: string;
  recommended_models: string[];
  use_cases: string[];
  default_temperature?: number | null;
  default_reasoning_effort?: ReasoningEffort | null;
}

export interface ModelInfo {
  model_id: string;
  name: string;
  provider: string;
  context_window: number;
  supports_tools: boolean;
  supports_vision: boolean;
  supports_reasoning: boolean;
  pricing_input_usd?: number | null;
  pricing_output_usd?: number | null;
  groups: string[];
}

// ==================== TOOLS ====================

export interface ToolDefinition {
  id: string;
  tenant_id?: string | null;
  name: string;
  description: string;
  parameters_schema: Record<string, unknown>;
  handler_method: string;
  category: string;
  tags: string[];
  requires_auth: boolean;
  rate_limit_per_minute: number;
  is_active: boolean;
  created_at: string;
}

export interface ToolExecutionRequest {
  tool_name: string;
  arguments: Record<string, unknown>;
  session_id?: string | null;
}

export interface ToolExecutionResponse {
  success: boolean;
  result: unknown;
  error?: string | null;
  execution_time_ms: number;
}

// ==================== REQUEST/RESPONSE ====================

export interface ChatMessageRequest {
  message: string;
  session_id?: string | null;
  stream?: boolean;
  override_temperature?: number | null;
  override_reasoning_effort?: ReasoningEffort | null;
  override_max_tokens?: number | null;
}

export interface ChatMessageResponse {
  message_id: string;
  session_id: string;
  content: string;
  reasoning_summary?: string | null;
  tool_calls?: Array<{
    id: string;
    type: string;
    function: {
      name: string;
      arguments: string;
    };
  }> | null;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost_usd?: number | null;
  created_at: string;
}

export interface ChatStreamChunk {
  type: 'content' | 'reasoning' | 'tool_call' | 'done' | 'error';
  data: unknown;
  message_id?: string | null;
  session_id?: string | null;
}

export interface SQLValidationRequest {
  sql: string;
  agent_id: string;
}

export interface SQLValidationResponse {
  is_valid: boolean;
  is_read_only: boolean;
  tables_accessed: string[];
  warnings: string[];
  error?: string | null;
}

// ==================== FILTROS E PAGINAÇÃO ====================

export interface AgentListFilters {
  agent_type?: AgentType | null;
  model_group?: string | null;
  provider?: ModelProvider | null;
  is_active?: boolean | null;
  search?: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}
