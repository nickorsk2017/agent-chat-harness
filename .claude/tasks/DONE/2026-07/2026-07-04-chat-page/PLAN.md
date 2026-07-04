# PLAN — 2026-07-04-chat-page

plan_version: 1

## Layered file set (Executor writes)
- P1 types/chat.d.ts               ChatRole, ChatMessage, SendMessageRequest/Response (R3)
- P2 services/chatService.ts       sendChatMessage(req, signal?) MOCK: setTimeout delay ->
                                    canned agent reply echoing prompt (R2,A3)
- P3 stores/chatStore.ts           Zustand: {messages,isSending,error, send(), reset()};
                                    send() appends user msg, calls P2, appends agent msg,
                                    handles error. NO direct HTTP (delegates to service) (R3,A4)
- P4 shared/ui-kit/MessageBubble.tsx  presentational bubble by role (R3)
- P5 shared/ui-kit/MessageInput.tsx   controlled textarea + send btn; Enter=send,
                                       Shift+Enter=newline; local useState only (R3,R4)
- P6 shared/features/chat/ChatView.tsx  "use client"; wires store + ui-kit; list, empty
                                        state, typing indicator, error, auto-scroll (R1,R4)
- P7 app/chat/page.tsx             server page rendering <ChatView/> — pages only (R3,A1)
- P8 app/page.tsx (edit)           add a link to /chat from Hello World (nicety)

## Tests (R5)
- P9 __tests__/chatService.test.ts  awaits sendChatMessage -> reply references prompt
- P10 __tests__/chatStore.test.ts   send() -> messages == [user, assistant] w/ correct roles

## Boundary decisions
- S1 Only the service performs the (mock) request; store imports the service, ui-kit does not.
- S2 Client boundary at ChatView (features) + MessageInput (ui-kit local input state);
     page + MessageBubble stay non-stateful. app/chat/page is a server component.
- S3 ids via crypto.randomUUID(); timestamps via Date.now().
- S4 Alias imports (@/types, @/services, @/stores, @/shared/...).

## Verification (Validator)
- Static: config-free syntax scan; confirm S1 boundary (grep: no service/store import in ui-kit);
  confirm mock marker present. Runtime `pnpm test`/`pnpm dev` deferred to operator (Linux
  sandbox can't run macOS-installed binaries).

## Risks / out of scope
- Real gateway/MCP wiring, streaming, persistence, auth -> future tasks. Mock clearly labeled.
