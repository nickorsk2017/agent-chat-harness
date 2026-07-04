# TASK — 2026-07-04-chat-page
owner: Engineer
immutable: true

## Requirements
- R1: Add a `/chat` page where the user can type and send messages to the AI agent
      and see the conversation (user + agent bubbles).
- R2: No backend/MCP yet -> sending is a MOCK endpoint implemented in a Service
      (services/), returning a simulated agent reply after a short delay.
- R3: Respect the frontend layer roles:
  - app/chat = page only (renders the feature, no logic).
  - shared/features/chat = chat logic/composition (client component).
  - shared/ui-kit = presentational primitives (bubble, input), no store/service access.
  - services = the mock request handler (single backend boundary).
  - stores = Zustand chat state; delegates the request to the service.
  - types = chat entity types (*.d.ts).
- R4: UX: message list, send on Enter (Shift+Enter = newline), disabled/loading
      state while awaiting the mock reply, empty state, error handling.

## Acceptance
- A1: Navigating to /chat renders a working chat UI.
- A2: Sending a message appends a user bubble, then a mock agent bubble.
- A3: The network/mock call lives ONLY in services/ (store calls the service).
- A4: Layer boundaries in R3 are respected (no service call in ui-kit; no HTTP in store).
- A5: Tests cover the mock service and the store send-flow.

## Constraints
- pnpm/Next 16 App Router, Tailwind v4, Zustand 5, TypeScript.
- Mock only; clearly marked as a placeholder for the future gateway/MCP call.
- No secrets. Keep ui-kit presentational.
