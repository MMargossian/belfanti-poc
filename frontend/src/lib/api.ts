const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(
  path: string,
  options: RequestInit = {},
  sessionId?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (sessionId) {
    headers["x-session-id"] = sessionId;
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export function createSession() {
  return fetchAPI<{ session_id: string; has_api_key: boolean }>("/api/session", { method: "POST" });
}

export function resetSession(sessionId: string) {
  return fetchAPI<{ status: string }>("/api/session", { method: "DELETE" }, sessionId);
}

export function getSessionState(sessionId: string) {
  return fetchAPI<Record<string, unknown>>("/api/session/state", {}, sessionId);
}

export function setApiKey(sessionId: string, apiKey: string) {
  return fetchAPI<{ status: string }>(
    "/api/config/api-key",
    { method: "PUT", body: JSON.stringify({ api_key: apiKey }) },
    sessionId
  );
}

export function getPipeline(sessionId: string) {
  return fetchAPI<{
    current_stage: string;
    completed_stages: string[];
    failed_stage: string | null;
    error_message: string | null;
  }>("/api/pipeline", {}, sessionId);
}

export function getModules(sessionId: string) {
  return fetchAPI<
    { name: string; label: string; group: string; enabled: boolean }[]
  >("/api/modules", {}, sessionId);
}

export function updateModules(sessionId: string, enabledModules: string[]) {
  return fetchAPI<{ status: string; enabled_modules: string[] }>(
    "/api/modules",
    { method: "PUT", body: JSON.stringify({ enabled_modules: enabledModules }) },
    sessionId
  );
}

export function loadDemo(sessionId: string, index: number) {
  return fetchAPI<{ message: string; rfq: Record<string, unknown> }>(
    "/api/demo/load",
    { method: "POST", body: JSON.stringify({ index }) },
    sessionId
  );
}

export function getSSEUrl(path: string): string {
  return `${API_URL}${path}`;
}

export { API_URL };
