# TASK — 2026-07-06-fix-gemma-check-mount
owner: Engineer
immutable: true

## Requirements
- R1: `make gemma-check` failed: `python: can't open file '/app/scripts/gemma_healthcheck.py'`.
  Cause: the pre-existing `agent-chat/mcp` image predates mcp/scripts/, and
  `docker compose run` reuses that stale image (no rebuild), so the file is absent.
- R2: Make the target work without forcing a slow full image rebuild on every check.
  Deps (agent_core, master_orchestrator, langchain) are already installed in the image;
  only the script file is new.

## Acceptance
- A1: `make gemma-check` runs the CURRENT host copy of the script regardless of image
  age, by bind-mounting mcp/scripts -> /app/scripts (read-only). ARGS still forwarded.
- A2: Makefile parses; target still listed in `make help`; no other targets changed.

## Constraints
- No new deps. Keep --no-deps (don't spin up postgres). One file changed (Makefile).
