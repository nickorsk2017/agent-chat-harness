import type { ChatRole } from "@/types/chat";

interface MessageBubbleProps {
  role: ChatRole;
  content: string;
}

/** Presentational chat bubble. No store/service access. */
export function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={[
          "max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm leading-relaxed",
          isUser
            ? "rounded-br-sm bg-blue-600 text-white"
            : "rounded-bl-sm bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100",
        ].join(" ")}
      >
        {content}
      </div>
    </div>
  );
}
