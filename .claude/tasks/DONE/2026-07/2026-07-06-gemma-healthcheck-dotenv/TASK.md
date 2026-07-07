# TASK — 2026-07-06-gemma-healthcheck-dotenv
owner: Engineer
immutable: true

## Requirements
- R1: `make gemma-check` fails: `OPENROUTER_API_KEY must be set`. The key lives in
  the repo-root `.env` (`GEMMA_API_KEY=...`), not the shell env; the minimal script
  only checked `os.environ`.
- R2: Before building the model, load `OPENROUTER_API_KEY`/`GEMMA_API_KEY` from the
  repo-root `.env` (script lives at `mcp/scripts/`, root is two levels up) when not
  already in the environment. Shell env wins over `.env`.

## Acceptance
- A1: With the key only in `.env`, the script reaches the model call.
- A2: Test snippet itself (model, temperature, prompt, print) unchanged.

## Constraints
- Single file: `mcp/scripts/gemma_healthcheck.py`. No new deps.
