# PLAN — 2026-07-04-i18n-en

plan_version: 1

## Strategy
Pure string/comment translation across 7 files. No layer or logic changes.
Each Russian span maps 1:1 to an English span; interpolation, emoji, and the
`(mock)` marker are preserved. Test prompts and their assertions are translated
together so equality checks stay valid.

## Translation map (Executor applies)
- P1 app/page.tsx
     "Открыть чат с агентом →" -> "Open agent chat →"
- P2 shared/ui-kit/MessageInput.tsx
     placeholder "Напишите сообщение агенту…" -> "Message the agent…"
     aria-label "Сообщение"                   -> "Message"
     button     "Отправить"                    -> "Send"
- P3 shared/features/chat/ChatView.tsx
     h1 "AI-агент"                                             -> "AI agent"
     subtitle "Демо-чат · ответы пока заглушка (backend и MCP не подключены)"
        -> "Demo chat · replies are stubbed for now (backend and MCP not connected)"
     empty "Начните диалог — напишите сообщение агенту ниже."
        -> "Start a conversation — message the agent below."
     typing "Агент печатает…"                                  -> "Agent is typing…"
- P4 stores/chatStore.ts
     error "Не удалось получить ответ агента. Попробуйте ещё раз."
        -> "Failed to get a response from the agent. Please try again."
- P5 services/chatService.ts (mock reply, keep emoji + (mock) + ${text})
     "🤖 (mock) Принял ваше сообщение: «${text}».\n\n"
        -> "🤖 (mock) Received your message: “${text}”.\n\n"
     "Backend-шлюз и MCP-оркестратор пока не подключены — это заглушка ответа "
        -> "The backend gateway and the MCP orchestrator are not connected yet — this is a stubbed reply "
     "AI-агента. Позже здесь появится реальный ответ от суб-агентов "
        -> "from the AI agent. A real response from the sub-agents "
     "(веб, PDF, изображения), выполняемых параллельно."
        -> "(web, PDF, images) running in parallel will appear here later."
- P6 __tests__/chatStore.test.ts
     send("Привет, агент") and expect content "Привет, агент" -> "Hello, agent" (both sites)
- P7 __tests__/chatService.test.ts
     prompt "Какая погода в Берлине?" -> "What's the weather in Berlin?"

## Verification (Validator)
- grep -rP '[\x{0400}-\x{04FF}]' frontend (excl node_modules) -> zero hits (A1).
- Confirm only string/comment content changed (A3): no import/identifier diffs.
- Runtime `pnpm test` deferred to operator macOS (sandbox cannot run macOS SWC),
  consistent with the chat-page task; assertions verified by inspection (A2).

## Out of scope
- The `error` message copy, endpoint wiring, i18n framework — none introduced.
