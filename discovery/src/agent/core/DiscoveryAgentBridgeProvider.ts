"use client";

import type { DiscoveryAgentDataProvider, DA_Message, DA_StreamEvent } from "./discovery/DiscoveryAgentDataProvider";
import type { AgentProvider, ChatMessage, StreamEvent } from "./types";

function mapMsg(m: ChatMessage): DA_Message {
  return {
    id: m.id,
    role: m.role,
    content: m.content ?? "",
    createdAt: m.createdAt,
    artifacts: m.artifacts,
    meta: m.meta,
  };
}

async function* mapStream(ev: AsyncIterable<StreamEvent>, messageId?: string): AsyncIterable<DA_StreamEvent> {
  for await (const e of ev) {
    yield {
      type: e.type as DA_StreamEvent["type"],
      messageId: e.messageId ?? messageId,
      textDelta: e.textDelta,
      data: e.data,
    };
  }
}

export class DiscoveryAgentBridgeProvider implements DiscoveryAgentDataProvider {
  private loading = false;
  public get isLoading() { return this.loading; }
  public get isStreaming() { return this.loading; } // optional alias

  constructor(private agent: AgentProvider) {}

  async capabilities() {
    return this.agent.capabilities();
  }

  async createChat(opts?: { title?: string; threadId?: string }) {
    if (opts?.threadId) return { id: opts.threadId };
    const { chatId } = await this.agent.createChat({ title: opts?.title });
    return { id: chatId };
  }

  async listMessages(chatId: string, cursor?: { before?: string; limit?: number }) {
    const msgs = await this.agent.listMessages(chatId);
    return msgs.map(mapMsg);
  }

  async sendMessage(
    chatId: string,
    input: { text?: string; attachments?: unknown[]; meta?: Record<string, unknown> }
  ) {
    this.loading = true;
    try {
      const { messageId } = await this.agent.sendMessage(chatId, { text: input.text, attachments: input.attachments as any, meta: input.meta });
      return { id: messageId };
    } finally {
      // Keep loading true while streaming
    }
  }

  async *stream(chatId: string, messageId: string): AsyncIterable<DA_StreamEvent> {
    this.loading = true;
    try {
      const evs = this.agent.stream(chatId, messageId);
      yield* mapStream(evs, messageId);
    } finally {
      this.loading = false;
    }
  }

  async interrupt(chatId: string, messageId: string) {
    await this.agent.interrupt?.(chatId, messageId);
  }

  async resume(chatId: string, messageId: string, input?: unknown) {
    await this.agent.resume?.(chatId, messageId, input);
  }
}
