"use client";

import { useEffect, useRef } from "react";
import { useChatStore } from "@/stores/chatStore";
import { MessageBubble } from "@/shared/ui-kit/MessageBubble";
import { MessageInput } from "@/shared/ui-kit/MessageInput";

/**
 * Chat feature: wires the Zustand store to presentational ui-kit parts.
 * All page logic lives here; the route file only renders this component.
 */
export function ChatView() {
  const messages = useChatStore((s) => s.messages);
  const isSending = useChatStore((s) => s.isSending);
  const error = useChatStore((s) => s.error);
  const send = useChatStore((s) => s.send);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const isEmpty = messages.length === 0;

  return (
    <div className="mx-auto flex h-screen w-full max-w-2xl flex-col">
      <header className="border-b border-gray-200 px-4 py-3 dark:border-gray-800">
        <h1 className="text-base font-semibold">AI agent</h1>
        <p className="text-xs text-gray-500">
          Demo chat · replies are stubbed for now (backend and MCP not connected)
        </p>
      </header>

      <main className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {isEmpty && (
          <div className="flex h-full items-center justify-center text-center text-sm text-gray-400">
            Start a conversation — message the agent below.
          </div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.id} role={m.role} content={m.content} />
        ))}

        {isSending && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm bg-gray-100 px-4 py-2 text-sm text-gray-500 dark:bg-gray-800">
              Agent is typing…
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950/40">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      <footer className="border-t border-gray-200 px-4 py-3 dark:border-gray-800">
        <MessageInput onSend={send} disabled={isSending} />
      </footer>
    </div>
  );
}
