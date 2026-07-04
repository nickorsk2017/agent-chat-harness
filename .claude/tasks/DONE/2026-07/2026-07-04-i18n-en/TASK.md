# TASK — 2026-07-04-i18n-en
owner: Engineer
immutable: true

## Requirements
- R1: Translate all Russian (Cyrillic) text in the `frontend/` subsystem to English.
      Scope = user-facing UI strings, `aria-label`s, mock reply text, code comments,
      and test string literals/expectations. Identifiers (variable/function/type
      names) are already English and are NOT renamed.
- R2: Affected files (7):
  - app/page.tsx                         ("Открыть чат с агентом →")
  - shared/features/chat/ChatView.tsx    (header, subtitle, empty state, typing indicator)
  - shared/ui-kit/MessageInput.tsx       (placeholder, aria-label, button label)
  - services/chatService.ts              (mock reply body)
  - stores/chatStore.ts                  (error message)
  - __tests__/chatStore.test.ts          (prompt + expectation string)
  - __tests__/chatService.test.ts        (prompt string)
- R3: Translations must be natural, idiomatic English and preserve meaning, tone,
      punctuation style, and any interpolation (${text}) / emoji.
- R4: Tests must still pass — expectation strings and the prompts they assert on
      must be translated consistently so assertions remain valid.

## Acceptance
- A1: No Cyrillic characters remain anywhere under `frontend/` (excluding node_modules).
- A2: `chatStore.test.ts` and `chatService.test.ts` still pass with translated strings.
- A3: No identifier, import, alias, or logic changed — string/comment content only.

## Constraints
- String/comment content edits only; no structural or behavioral changes.
- Keep the emoji and the `(mock)` marker in the mock reply.
- Do not touch files outside the 7 listed.
