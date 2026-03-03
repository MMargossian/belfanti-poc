export interface PipelineState {
  current_stage: string;
  completed_stages: string[];
  failed_stage: string | null;
  error_message: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCall[];
  timestamp: number;
}

export interface ToolCall {
  tool_name: string;
  tool_input: Record<string, unknown>;
  result?: string;
  status: "running" | "ok" | "fail";
}

export interface ApprovalGate {
  gate_name: string;
  gate_data: Record<string, unknown>;
}

export interface SSEEvent {
  event: string;
  data: Record<string, unknown>;
}

export interface ModuleInfo {
  name: string;
  label: string;
  group: string;
  enabled: boolean;
}

export interface DemoRFQ {
  message: string;
  rfq: Record<string, unknown>;
}
