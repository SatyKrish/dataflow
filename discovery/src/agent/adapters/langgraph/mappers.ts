import { nanoid } from "nanoid";
import type { ChatMessage, StreamEvent } from "../../core/types";

/**
 * Map a LangGraph SDK message (unknown shape) to our ChatMessage.
 * Fill safe defaults and preserve the raw payload in meta._raw
 */
export function mapSdkMessageToChatMessage(sdkMsg: any): ChatMessage {
  const id = sdkMsg?.id ?? sdkMsg?.message_id ?? nanoid();
  // Map common LangGraph/LangChain shapes to roles
  const type = sdkMsg?.type ?? sdkMsg?.role;
  const role = (
    type === "human" ? "user" :
    type === "ai" ? "assistant" :
    type === "system" ? "system" :
    type === "tool" ? "tool" :
    sdkMsg?.role ?? "assistant"
  ) as ChatMessage["role"];
  // Extract content from various shapes
  let content = "";
  const rawContent = sdkMsg?.content ?? sdkMsg?.data?.content;
  if (typeof rawContent === "string") {
    content = rawContent;
  } else if (Array.isArray(rawContent)) {
    content = rawContent
      .map((part: any) => part?.text ?? part?.content ?? "")
      .filter(Boolean)
      .join("");
  } else if (rawContent != null) {
    // Try text property if present
    content = rawContent?.text ?? "";
    if (!content) content = JSON.stringify(rawContent);
  }
  const createdAt =
    (sdkMsg?.created_at && new Date(sdkMsg.created_at).toISOString()) ||
    new Date().toISOString();

  return {
    id,
    role,
    content,
    createdAt,
    artifacts: [],
    toolCalls: [],
    toolResults: [],
    meta: { _raw: sdkMsg },
  };
}

/**
 * Map a LangGraph stream event to our StreamEvent.
 * Adjust the cases here to match the SDK event names you use.
 */
export function mapSdkEventToStreamEvent(ev: any, messageId?: string): StreamEvent | null {
  const event = ev?.event;
  // Map SDK event names to our StreamEvent types
  if (event === "messages/partial") {
    // Partial message delta
    const delta = Array.isArray(ev?.data)
      ? ev.data.map((m: any) => m?.content ?? m?.text ?? "").join("")
      : ev?.data?.content ?? ev?.data?.text ?? "";
    return { type: "message.delta", messageId, textDelta: String(delta), data: ev };
  }
  if (event === "messages/complete") {
    return { type: "message.completed", messageId, data: ev };
  }
  if (event === "error") {
    return { type: "error", messageId, data: ev };
  }
  // Add more mappings as needed for your use case
  return null;
}
