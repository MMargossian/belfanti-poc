import { API_URL } from "./api";

export interface SSECallbacks {
  onText?: (content: string) => void;
  onToolCall?: (toolName: string, toolInput: Record<string, unknown>) => void;
  onToolResult?: (toolName: string, result: string) => void;
  onPipelineUpdate?: (data: {
    current_stage: string;
    completed_stages: string[];
    failed_stage: string | null;
    error_message: string | null;
  }) => void;
  onApprovalNeeded?: (gateName: string, gateData: Record<string, unknown>) => void;
  onError?: (message: string) => void;
  onDone?: () => void;
}

export async function streamSSE(
  path: string,
  body: Record<string, unknown>,
  sessionId: string,
  callbacks: SSECallbacks,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-session-id": sessionId,
    },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok) {
    callbacks.onError?.(`HTTP ${res.status}: ${res.statusText}`);
    callbacks.onDone?.();
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    callbacks.onError?.("No response body");
    callbacks.onDone?.();
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";
  let currentData = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          currentEvent = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          currentData = line.slice(6);
        } else if (line === "" && currentEvent && currentData) {
          try {
            const parsed = JSON.parse(currentData);
            dispatchEvent(currentEvent, parsed, callbacks);
          } catch {
            // skip malformed
          }
          currentEvent = "";
          currentData = "";
        }
      }
    }
  } catch (err) {
    if ((err as Error).name !== "AbortError") {
      callbacks.onError?.((err as Error).message);
    }
  } finally {
    callbacks.onDone?.();
  }
}

function dispatchEvent(
  event: string,
  data: Record<string, unknown>,
  callbacks: SSECallbacks
) {
  switch (event) {
    case "text":
      callbacks.onText?.(data.content as string);
      break;
    case "tool_call":
      callbacks.onToolCall?.(
        data.tool_name as string,
        data.tool_input as Record<string, unknown>
      );
      break;
    case "tool_result":
      callbacks.onToolResult?.(data.tool_name as string, data.result as string);
      break;
    case "pipeline_update":
      callbacks.onPipelineUpdate?.(
        data as {
          current_stage: string;
          completed_stages: string[];
          failed_stage: string | null;
          error_message: string | null;
        }
      );
      break;
    case "approval_needed":
      callbacks.onApprovalNeeded?.(
        data.gate_name as string,
        data.gate_data as Record<string, unknown>
      );
      break;
    case "error":
      callbacks.onError?.(data.message as string);
      break;
    case "done":
      // onDone is called in finally block
      break;
  }
}
