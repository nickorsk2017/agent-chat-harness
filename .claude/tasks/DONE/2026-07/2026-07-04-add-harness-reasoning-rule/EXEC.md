# EXEC — 2026-07-04-add-harness-reasoning-rule
exec_version: 1

## Change
Root `CLAUDE.md` — added the "Reasoning belongs to the Planner" rule (R1).

Two edits, single file (`CLAUDE.md`):
1. New section "## Reasoning belongs to the Planner" after the Prime Directive
   chat-transport paragraph: reasoning/analysis/design live in `PLAN.md`; actors
   must not improvise analysis in chat or non-Planner artifacts; Executor implements,
   Validator checks; new reasoning routes back through Planner (bump `plan_version`).
2. New prohibition bullet in "## No exceptions": no analysis/design/decision-making
   outside the Planner stage; route new reasoning through the Planner.

## Acceptance mapping
- A1: satisfied by edit 1 (explicit Planner/PLAN.md ownership of reasoning).
- A2: additive only; Prime Directive, No-exceptions, precedence, roles unchanged.
- A3: single file changed (root `CLAUDE.md`); LOW complexity holds.
