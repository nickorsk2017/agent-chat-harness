import { create } from "zustand";
import type { ChatMessage, ChatRole } from "@/types/chat";
import { sendChatMessage } from "@/services/chatService";

interface ChatState {
  messages: ChatMessage[];
  isSending: boolean;
  error: string | null;
  /** Send a user prompt to the (mock) agent and record both messages. */
  send: (prompt: string) => Promise<void>;
  reset: () => void;
}

function makeMessage(role: ChatRole, content: string): ChatMessage {
  return {
    id:
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    content,
    createdAt: Date.now(),
  };
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isSending: false,
  error: null,

  send: async (prompt: string) => {
    const text = prompt.trim();
    if (!text || get().isSending) return;

    const userMessage = makeMessage("user", text);
    set((state) => ({
      messages: [...state.messages, userMessage],
      isSending: true,
      error: null,
    }));

    try {
      // The request lives in the service layer, never in the store itself.
      const { reply } = await sendChatMessage({ prompt: text });
      set((state) => ({
        messages: [...state.messages, makeMessage("assistant", reply)],
        isSending: false,
      }));
    } catch {
      set({
        isSending: false,
        error: "Failed to get a response from the agent. Please try again.",
      });
    }
  },

  reset: () => set({ messages: [], isSending: false, error: null }),
}));
