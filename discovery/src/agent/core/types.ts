// Types for chat, agent, and message structures
export type Role = "user" | "assistant" | "system" | "tool";

export interface Artifact {
  id: string;
  kind: "text" | "json" | "table" | "image" | "file" | "trace";
  mime?: string;
  name?: string;
  url?: string;
  data?: unknown;
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  createdAt: string; // ISO
  artifacts?: Artifact[];
  toolCalls?: Array<{ id: string; name: string; args: unknown }>;
  toolResults?: Array<{ callId: string; result: unknown }>;
  meta?: Record<string, unknown>;
}

export interface StreamEvent {
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
  data?: unknown; // raw adapter payload
}

export interface ChatCapabilities {
  streaming: boolean;
  threads: boolean;
  interrupts: boolean;
  toolCalling: boolean;
  artifacts: boolean;
  branches: boolean;
  systemTrace: boolean;
}

export interface AgentProvider {
  name: string;
  capabilities(): Promise<ChatCapabilities>;

  createChat(opts?: { title?: string; threadId?: string }): Promise<{ chatId: string }>;
  listMessages(chatId: string, cursor?: { before?: string; limit?: number }): Promise<ChatMessage[]>;

  sendMessage(
    chatId: string,
    input: { text?: string; attachments?: Artifact[]; meta?: Record<string, unknown> }
  ): Promise<{ messageId: string }>;

  stream(chatId: string, messageId: string): AsyncIterable<StreamEvent>;

  interrupt?(chatId: string, messageId: string): Promise<void>;
  resume?(chatId: string, messageId: string, input?: unknown): Promise<void>;
}
