"use client";

import { Client } from "@langchain/langgraph-sdk";
import type { AgentProvider, ChatCapabilities, ChatMessage, StreamEvent } from "../../core/types";
import { mapSdkEventToStreamEvent, mapSdkMessageToChatMessage } from "./mappers";

// Small helper: convert an SDK stream (AsyncIterable-like) into our AsyncIterable<StreamEvent>
async function* mapEvents(iterable: AsyncIterable<any>, messageId?: string): AsyncIterable<StreamEvent> {
  for await (const ev of iterable) {
    const mapped = mapSdkEventToStreamEvent(ev, messageId);
    if (mapped) yield mapped;
  }
}

export class LangGraphAdapter implements AgentProvider {
  name = "langgraph";
  private client: Client;
  private graph: string;

  constructor(cfg: { baseUrl: string; graph?: string }) {
    this.client = new Client({ apiUrl: cfg.baseUrl });
    this.graph = cfg.graph ?? "research";
  }

  async capabilities(): Promise<ChatCapabilities> {
    return {
      streaming: true,
      threads: true,
      interrupts: true,
      toolCalling: true,
      artifacts: true,
      branches: true,
      systemTrace: true,
    };
  }

  async createChat(): Promise<{ chatId: string }> {
    // Create a thread and tag with graph id for clarity
    const thread = await this.client.threads.create({ graphId: this.graph });
    const chatId = (thread as any).thread_id ?? (thread as any).id;
    if (!chatId) throw new Error("Failed to create LangGraph thread.");
    return { chatId };
  }

  async listMessages(chatId: string): Promise<ChatMessage[]> {
    // Prefer thread state for current messages
    const resp = await this.client.threads.getState(chatId as any);
    const msgs = (resp as any)?.values?.messages ?? [];
    if (!Array.isArray(msgs)) return [];
    return (msgs as any[]).map(mapSdkMessageToChatMessage);
  }

  async sendMessage(chatId: string, input: { text?: string }): Promise<{ messageId: string }> {
    // Use the configured graph/assistant name
    const run = await this.client.runs.create(chatId, this.graph, { input: { text: input?.text ?? "" } });
    const messageId = (run as any).message_id ?? (run as any).id ?? (run as any).run_id;
    if (!messageId) throw new Error("LangGraph run did not return a message id.");
    return { messageId };
  }

  async *stream(chatId: string, messageId: string): AsyncIterable<StreamEvent> {
    // Placeholder: For live streaming, consider keeping the run id and calling runs.stream()
    // Here we just emit a completed event to satisfy interface.
    yield { type: "message.completed", messageId, data: { synthetic: true } };
  }

  // Interrupt/resume are not available in the SDK as of now.
}
