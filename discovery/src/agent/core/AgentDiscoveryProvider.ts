import { createProviderFromEnv } from "@/agent/core/providerFactory";
import type { DiscoveryAgentDataProvider, Chat, Message, Artifact } from "@/components/discovery-agent/discovery-agent-ui";
import type { AgentProvider, ChatMessage, ChatCapabilities } from "@/agent/core/types";

// Minimal wrapper to adapt AgentProvider to DiscoveryAgentDataProvider
export class AgentDiscoveryProvider implements DiscoveryAgentDataProvider {
  private agent: AgentProvider;
  private chatId: string | undefined;
  private caps: ChatCapabilities | undefined;

  constructor() {
    this.agent = createProviderFromEnv();
  }

  async listChats(): Promise<Chat[]> {
    // For now, just one chat session
    if (!this.chatId) {
      const { chatId } = await this.agent.createChat();
      this.chatId = chatId;
    }
    return [
      {
        id: this.chatId,
        title: "Chat",
        tags: [],
        lastActivity: new Date().toISOString(),
      },
    ];
  }

  async createChat(): Promise<{ id: string }> {
    const { chatId } = await this.agent.createChat();
    this.chatId = chatId;
    return { id: chatId };
  }

  async listMessages(chatId: string): Promise<Message[]> {
    const msgs = await this.agent.listMessages(chatId);
    return msgs.map(this.mapToMessage);
  }

  async sendMessage(params: { chatId: string; text: string }): Promise<void> {
    await this.agent.sendMessage(params.chatId, { text: params.text });
  }

  async togglePin(): Promise<void> {
    // Not implemented for LangGraph adapter; could be enabled via REST backend.
    return;
  }

  private mapToMessage(msg: ChatMessage): Message {
    return {
      id: msg.id,
      role: (msg.role === "assistant" ? "agent" : msg.role) as Message["role"],
      text: msg.content,
      artifacts: (msg.artifacts ?? []).map(this.mapToArtifact),
      createdAt: msg.createdAt,
    };
  }

  private mapToArtifact(a: import("@/agent/core/types").Artifact): Artifact {
    const kind = a.kind;
    let type: Artifact["type"];
    if (kind === "table") type = "table.json";
    else if (kind === "file") type = "file";
    else if (kind === "json" || kind === "text" || kind === "trace" || kind === "image") {
      // Represent non-table content as a chart only if explicit chart spec is present
      // Otherwise fallback to a table/json preview in viewer
      type = "table.json";
    } else {
      // Default safe fallback
      type = "table.json";
    }
    return {
      id: a.id,
      type,
      title: a.name ?? a.mime ?? kind,
      uri: a.url,
      json: a.data,
      meta: {},
      pinned: false,
    };
  }
}
