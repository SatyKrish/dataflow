// providers/DiscoveryAgentHTTPProvider.ts
// NOTE: Avoid importing component-local types to prevent tight coupling.
// These should be moved to a shared types module. For now, redefine minimal shapes.
export type Role = "user" | "agent" | "tool";
export type Artifact = {
  id: string;
  type: "chart.vegaLite" | "table.json" | "file";
  title: string;
  uri?: string;
  json?: any;
  meta?: Record<string, any>;
  pinned?: boolean;
};
export type Message = { id: string; role: Role; text: string; artifacts?: Artifact[]; createdAt: string };
export type Chat = { id: string; title: string; tags?: string[]; lastActivity?: string };

export interface DiscoveryAgentDataProvider {
  listChats(signal?: AbortSignal): Promise<Chat[]>;
  listMessages(chatId: string, signal?: AbortSignal): Promise<Message[]>;
  sendMessage(params: { chatId: string; text: string; pinNext?: boolean }, signal?: AbortSignal): Promise<void>;
  togglePin(params: { chatId: string; artifactId: string }, signal?: AbortSignal): Promise<void>;
}

type ServerChat = {
  id: string;
  title: string;
  tags?: string[];
  last_activity?: string; // server uses snake_case
};

type ServerMessage = {
  id: string;
  role: "user" | "agent" | "tool";
  text: string;
  created_at: string;
  artifacts?: Array<{
    id: string;
    kind: "chart.vegaLite" | "table.json" | "file";
    title: string;
    uri?: string;
    json?: any;
    meta?: Record<string, any>;
    pinned?: boolean;
  }>;
};

export class DiscoveryAgentHTTPProvider implements DiscoveryAgentDataProvider {
  constructor(
    private baseUrl: string,
    private opts?: { authToken?: string; headers?: Record<string, string> }
  ) {}

  private headers(extra?: Record<string, string>) {
    return {
      "Content-Type": "application/json",
      ...(this.opts?.authToken ? { Authorization: `Bearer ${this.opts.authToken}` } : {}),
      ...(this.opts?.headers ?? {}),
      ...(extra ?? {}),
    };
  }

  /** GET /chats */
  async listChats(signal?: AbortSignal): Promise<Chat[]> {
    const res = await fetch(`${this.baseUrl}/chats`, { headers: this.headers(), signal });
    if (!res.ok) throw new Error(`listChats failed: ${res.status} ${await res.text()}`);
    const data: ServerChat[] = await res.json();
    return data.map<Chat>((c) => ({
      id: c.id,
      title: c.title,
      tags: c.tags ?? [],
      lastActivity: c.last_activity,
    }));
  }

  /** GET /chats/:id/messages */
  async listMessages(chatId: string, signal?: AbortSignal): Promise<Message[]> {
    const res = await fetch(`${this.baseUrl}/chats/${encodeURIComponent(chatId)}/messages`, {
      headers: this.headers(),
      signal,
    });
    if (!res.ok) throw new Error(`listMessages failed: ${res.status} ${await res.text()}`);
    const data: ServerMessage[] = await res.json();
    return data.map<Message>((m) => ({
      id: m.id,
      role: m.role,
      text: m.text,
      createdAt: m.created_at,
      artifacts: (m.artifacts ?? []).map<Artifact>((a) => ({
        id: a.id,
        type: a.kind,
        title: a.title,
        uri: a.uri,
        json: a.json,
        meta: a.meta,
        pinned: !!a.pinned,
      })),
    }));
  }

  /** POST /chats/:id/messages (supports pinNext flag) */
  async sendMessage(
    params: { chatId: string; text: string; pinNext?: boolean },
    signal?: AbortSignal
  ): Promise<void> {
    const res = await fetch(
      `${this.baseUrl}/chats/${encodeURIComponent(params.chatId)}/messages`,
      {
        method: "POST",
        headers: this.headers(),
        body: JSON.stringify({ text: params.text, pin_next: !!params.pinNext }),
        signal,
      }
    );
    if (!res.ok) throw new Error(`sendMessage failed: ${res.status} ${await res.text()}`);
  }

  /** POST /chats/:id/artifacts/:artifactId/toggle-pin */
  async togglePin(
    params: { chatId: string; artifactId: string },
    signal?: AbortSignal
  ): Promise<void> {
    const res = await fetch(
      `${this.baseUrl}/chats/${encodeURIComponent(params.chatId)}/artifacts/${encodeURIComponent(
        params.artifactId
      )}/toggle-pin`,
      {
        method: "POST",
        headers: this.headers(),
        signal,
      }
    );
    if (!res.ok) throw new Error(`togglePin failed: ${res.status} ${await res.text()}`);
  }
}
