# EXEC — 2026-07-04-frontend-rules

exec_version: 1

## Applied
- Created frontend/CLAUDE.md (frontend subsystem rules), filling the gap referenced by
  root CLAUDE.md.
- Encodes RULE-A (React components ≤ 200 LOC; split via subcomponents/hooks/helpers;
  Validator flags violations as an `architecture` issue) and RULE-B (compose from
  shared/ui-kit primitives instead of raw <div>; add a kit primitive if missing;
  bare <div> only inside ui-kit / trivial wrappers).
- Restates layer boundaries (app/features/ui-kit/services/stores/types), stack
  conventions (App Router, Tailwind v4, Zustand, TS aliases), and precedence
  (.claude harness > root > this file).

## Notes
- Single new file. No source or behavior changes.
