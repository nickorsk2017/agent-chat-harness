// Chat domain types. Ambient module: consumed via `@/types/chat`.

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  /** epoch millis */
  createdAt: number;
}

/** Payload sent to the agent (mock for now, real gateway/MCP later). */
export interface SendMessageRequest {
  prompt: string;
}

/** Agent response. */
export interface SendMessageResponse {
  reply: string;
}
