# CLAUDE.md — Frontend (Next.js / Tailwind 4 / Zustand)

Rules for the `frontend/` subsystem. These are **in addition to**, never instead of,
the harness in [`.claude/CLAUDE.md`](../.claude/CLAUDE.md) and the root
[`CLAUDE.md`](../CLAUDE.md). All work still goes through the execution harness as a task.

**Precedence on conflict:** `.claude/` harness > root `CLAUDE.md` > this file.

## Layers (existing structure — respect boundaries)
- `app/` — routes/pages only. Render a feature; no business logic.
- `shared/features/` — feature composition (client components). Wires stores + ui-kit.
- `shared/ui-kit/` — presentational primitives (design system). No store/service access.
- `services/` — the single network/backend boundary (currently mock).
- `stores/` — Zustand state. Delegates requests to `services/`; never calls HTTP directly.
- `types/` — entity types.

## Rules

### RULE-A — React components are capped at 200 lines of code
No single React component file may exceed **200 lines of code**. When a component
approaches the limit, split it: extract subcomponents, custom hooks (`useX`), or plain
helper functions. Prefer many small, focused components over one large one. Presentational
pieces belong in `shared/ui-kit/`; composition/logic belongs in `shared/features/`.
A component over 200 LOC is a defect the Validator must flag (raise an `architecture`
issue and re-route through Planner to plan the split).

### RULE-B — Use UI Kit components instead of raw `<div>` markup
Build interfaces from `shared/ui-kit/` primitives rather than hand-rolling layout out of
bare `<div>`s. Before writing markup, reach for an existing kit component (e.g.
`MessageBubble`, `MessageInput`, and future Button/Input/Modal/Stack primitives).
If the primitive you need doesn't exist, **add it to the UI Kit first**, then consume it —
do not inline one-off `<div>` structures in feature or page files. Raw `<div>` is
acceptable only inside `shared/ui-kit/` itself (that is where primitives are defined) and
for trivial, non-reusable wrappers with no styling responsibility. This keeps styling and
structure centralized, consistent, and themeable.

## Stack conventions
- Next.js App Router; pages are server components unless they need interactivity.
- Tailwind v4 utility classes for styling (no ad-hoc CSS files for component styling).
- Zustand for state; the store delegates side effects to `services/`.
- TypeScript throughout; import via aliases (`@/types`, `@/services`, `@/stores`,
  `@/shared/...`).
