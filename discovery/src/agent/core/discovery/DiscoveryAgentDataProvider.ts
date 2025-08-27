// src/agent/core/discovery/DiscoveryAgentDataProvider.ts
export type DA_Role = "user" | "assistant" | "system" | "tool";

export interface DA_Artifact {
  id: string;
  kind: "text" | "json" | "table" | "image" | "file" | "trace";
  mime?: string;
  name?: string;
  url?: string;
  data?: unknown;
}

export interface DA_Message {
  id: string;
  role: DA_Role;
  content: string;
  createdAt: string;
  artifacts?: DA_Artifact[];
  meta?: Record<string, unknown>;
}

export interface DA_StreamEvent {
  type:
    | "message.delta"
    | "message.completed"
    | "artifact.created"
    | "tool.call"
    | "tool.result"
    | "status"
    | "error";
  messageId?: string;
  textDelta?: string;
  data?: unknown;
}

export interface DiscoveryAgentDataProvider {
  readonly isLoading?: boolean;
  capabilities(): Promise<{
    streaming: boolean;
    threads: boolean;
    interrupts: boolean;
    toolCalling: boolean;
    artifacts: boolean;
    branches: boolean;
    systemTrace: boolean;
  }>;
  createChat(opts?: { title?: string; threadId?: string }): Promise<{ id: string }>;
  listMessages(chatId: string, cursor?: { before?: string; limit?: number }): Promise<DA_Message[]>;
  sendMessage(
    chatId: string,
    input: { text?: string; attachments?: DA_Artifact[]; meta?: Record<string, unknown> }
  ): Promise<{ id: string }>;
  stream?(chatId: string, messageId: string): AsyncIterable<DA_StreamEvent>;
  interrupt?(chatId: string, messageId: string): Promise<void>;
  resume?(chatId: string, messageId: string, input?: unknown): Promise<void>;
}
