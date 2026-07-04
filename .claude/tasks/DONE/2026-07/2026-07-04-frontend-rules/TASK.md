# TASK — 2026-07-04-frontend-rules
owner: Engineer
immutable: true

## Requirements
- R1: Create `frontend/CLAUDE.md`, the frontend subsystem rule file referenced by the
      root CLAUDE.md ("frontend/CLAUDE.md — Next.js, Tailwind 4, Zustand") but missing.
- R2: It MUST encode the two mandated rules:
  - RULE-A: React components are capped at 200 lines of code. A component exceeding
            200 LOC must be split (extract subcomponents / hooks / helpers).
  - RULE-B: Build UIs from UI Kit components (shared/ui-kit) instead of hand-rolling raw
            `<div>` markup. Reach for a kit primitive first; add one to the kit if missing.
- R3: Follow the existing subsystem-CLAUDE.md conventions (concise, rule-oriented,
      states precedence under the harness; mirrors backend/mcp sibling style).

## Acceptance
- A1: `frontend/CLAUDE.md` exists at the frontend root.
- A2: Both RULE-A (≤200 LOC per component) and RULE-B (UI Kit over raw div) are stated
      unambiguously and are actionable.
- A3: Defers to the `.claude/` harness and root CLAUDE.md on precedence; does not
      contradict them.

## Constraints
- Single new file; no source/behavior changes.
- Reference real layer names in this repo (app/, shared/features/, shared/ui-kit/,
  services/, stores/, types/).
