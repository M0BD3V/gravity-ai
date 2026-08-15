import type { ChatResponse, HealthResponse, ToolDefinition, ToolResult } from "@gravity-ai/shared";

const API_BASE_URL = import.meta.env.VITE_GRAVITY_API_URL ?? "http://127.0.0.1:8765";

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export async function getTools(): Promise<ToolDefinition[]> {
  const response = await request<{ tools: ToolDefinition[] }>("/tools");
  return response.tools;
}

export async function sendChat(message: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export async function executeTool(payload: {
  toolName: string;
  arguments?: Record<string, unknown>;
  confirmed?: boolean;
}): Promise<ToolResult> {
  return request<ToolResult>("/tools/execute", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Gravity API returned ${response.status}`);
  }

  return (await response.json()) as T;
}

