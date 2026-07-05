# TASK — 2026-07-04-add-harness-reasoning-rule
owner: Engineer
immutable: true

## Requirements
- R1: Add an explicit rule to the ROOT `CLAUDE.md` stating that all reasoning,
  analysis, and design decisions must occur at the Planner stage (in `PLAN.md`),
  not ad hoc in chat or improvised by other actors. Reinforce that the harness
  in `.claude/` is always mandatory.

## Acceptance
- A1: Root `CLAUDE.md` contains a clear, self-consistent statement that
  reasoning/analysis belongs to the Planner (PLAN.md) and must not happen off-harness.
- A2: No contradiction with existing Prime Directive / No-exceptions sections;
  precedence and roles remain intact.
- A3: Only the root `CLAUDE.md` is changed (single file, LOW complexity).

## Constraints
- Do not weaken or alter existing harness rules; only add the new rule.
- Keep the file's existing structure and tone.
