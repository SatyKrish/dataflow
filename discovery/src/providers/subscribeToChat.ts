// Optional helper if your backend exposes /chats/:id/stream (SSE)
export function subscribeToChat(
  baseUrl: string,
  chatId: string,
  onEvent: (evt: { type: string; data: any }) => void
) {
  const url = `${baseUrl}/chats/${encodeURIComponent(chatId)}/stream`;
  const es = new EventSource(url, { withCredentials: false });
  es.onmessage = (ev) => {
    try {
      onEvent(JSON.parse(ev.data));
    } catch {}
  };
  es.onerror = () => es.close(); // simple retry policy can be added
  return () => es.close();
}
