export const RiskLevel = {
  Safe: "safe",
  Low: "low",
  Medium: "medium",
  High: "high",
  Destructive: "destructive",
} as const;

export type RiskLevel = (typeof RiskLevel)[keyof typeof RiskLevel];

export const ToolStatus = {
  Success: "success",
  Error: "error",
  RequiresConfirmation: "requires_confirmation",
  Skipped: "skipped",
} as const;

export type ToolStatus = (typeof ToolStatus)[keyof typeof ToolStatus];

export const ToolPermission = {
  FilesystemRead: "filesystem.read",
  FilesystemWrite: "filesystem.write",
  FilesystemDelete: "filesystem.delete",
  SystemProcess: "system.process",
  SystemSettings: "system.settings",
  Network: "network",
  Browser: "browser",
  Automation: "automation",
  MemoryRead: "memory.read",
  MemoryWrite: "memory.write",
} as const;

export type ToolPermission = (typeof ToolPermission)[keyof typeof ToolPermission];

export interface ToolDefinition {
  name: string;
  description: string;
  parameters_schema: Record<string, unknown>;
  permissions: ToolPermission[];
  risk: RiskLevel;
  requires_confirmation: boolean;
}

export interface ToolCall {
  toolName: string;
  arguments: Record<string, unknown>;
  confirmed: boolean;
}

export interface ToolResult {
  tool_name: string;
  status: ToolStatus;
  content: Record<string, unknown>;
  error: string | null;
  call_id: string | null;
  completed_at: string;
}

export type PluginPermission = ToolPermission | string;

export interface PluginCommand {
  name: string;
  description: string;
  tool: string;
}

export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  entrypoint: string;
  permissions: PluginPermission[];
  commands: PluginCommand[];
  settings: Record<string, unknown>;
}

export interface ChatMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: string;
  metadata?: Record<string, string>;
}

export interface ModelResponse {
  content: string;
  model: string;
  provider: string;
  usage: Record<string, number>;
}

export const MemoryScope = {
  ShortTerm: "short_term",
  LongTerm: "long_term",
  Preference: "preference",
  History: "history",
  Context: "context",
} as const;

export type MemoryScope = (typeof MemoryScope)[keyof typeof MemoryScope];

export interface MemoryEntry {
  entry_id: string;
  scope: MemoryScope;
  key: string;
  value: string;
  metadata: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface MemoryQuery {
  scope?: MemoryScope;
  text?: string;
  limit?: number;
}

export interface HealthResponse {
  name: string;
  version: string;
  status: "ok";
  rootDir: string;
  tools: number;
  plugins: number;
}

export interface ChatResponse {
  message: string;
  model: string;
  toolSuggestions: string[];
  memoryMatches: Array<{ scope: string; key: string; value: string }>;
}

