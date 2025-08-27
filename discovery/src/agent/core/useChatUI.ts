"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { AgentProvider, ChatMessage, ChatCapabilities } from "./types";

type State = {
  chatId?: string;
  messages: ChatMessage[];
  isStreaming: boolean;
  pendingText: string;
  capabilities?: ChatCapabilities;
  error?: string;
};

export function useChatUI(provider: AgentProvider) {
  const [state, setState] = useState<State>({
    messages: [],
    isStreaming: false,
    pendingText: "",
  });

  const appendMessage = useCallback((msg: ChatMessage) => {
    setState((s) => ({ ...s, messages: [...s.messages, msg] }));
  }, []);

  const updateAssistantDelta = useRef<((delta: string) => void) | undefined>(undefined);

  const initChat = useCallback(async () => {
    const caps = await provider.capabilities();
    const { chatId } = await provider.createChat();
    const existing = await provider.listMessages(chatId);
    setState((s) => ({ ...s, chatId, capabilities: caps, messages: existing }));
  }, [provider]);

  const setPendingText = useCallback((t: string) => {
    setState((s) => ({ ...s, pendingText: t }));
  }, []);

  const send = useCallback(async () => {
    if (!state.chatId || !state.pendingText.trim()) return;
    const userContent = state.pendingText;
    setState((s) => ({ ...s, pendingText: "" }));

    // optimistic user message
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userContent,
      createdAt: new Date().toISOString(),
    };
    appendMessage(userMsg);

    // placeholder assistant message we’ll fill via streaming
    const assistantId = `assistant-${Date.now()}`;
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
    };
    appendMessage(assistantMsg);

    // local updater to merge token deltas
    updateAssistantDelta.current = (delta: string) => {
      setState((s) => ({
        ...s,
        messages: s.messages.map((m) =>
          m.id === assistantId ? { ...m, content: (m.content ?? "") + delta } : m
        ),
      }));
    };

    try {
      setState((s) => ({ ...s, isStreaming: true }));
      const { messageId } = await provider.sendMessage(state.chatId, { text: userContent });

      for await (const ev of provider.stream(state.chatId, messageId)) {
        if (ev.type === "message.delta" && ev.textDelta) {
          updateAssistantDelta.current?.(ev.textDelta);
        } else if (ev.type === "message.completed") {
          // finalize
        } else if (ev.type === "status") {
          // TODO: surface trace UI if desired
        } else if (ev.type === "error") {
          setState((s) => ({ ...s, error: "Stream error" }));
        }
      }
    } catch (e: any) {
      setState((s) => ({ ...s, error: e?.message ?? "Send failed" }));
    } finally {
      setState((s) => ({ ...s, isStreaming: false }));
    }
  }, [appendMessage, provider, state.chatId, state.pendingText]);

  const interrupt = useCallback(async () => {
    // best-effort; may be unsupported
    const last = [...state.messages].reverse().find((m) => m.role === "assistant");
    if (!state.chatId || !last) return;
    await provider.interrupt?.(state.chatId, last.id);
  }, [provider, state.chatId, state.messages]);

  const resume = useCallback(async (input?: unknown) => {
    const last = [...state.messages].reverse().find((m) => m.role === "assistant");
    if (!state.chatId || !last) return;
    await provider.resume?.(state.chatId, last.id, input);
  }, [provider, state.chatId, state.messages]);

  return {
    ...state,
    initChat,
    setPendingText,
    send,
    interrupt,
    resume,
  };
}
