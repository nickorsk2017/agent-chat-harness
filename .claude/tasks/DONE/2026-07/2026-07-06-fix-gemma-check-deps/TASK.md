# TASK — 2026-07-06-fix-gemma-check-deps
owner: Engineer
immutable: true

## Requirements
- R1: `make gemma-check` fails with `No module named 'langchain_openrouter'` — the
  `.venv-gemma` bootstrap in the root `Makefile` does not install
  `langchain-openrouter` (required since `mcp/agent_core/llm.py` switched to
  `ChatOpenRouter`).
- R2: Add `langchain-openrouter` to `GEMMA_DEPS`.
- R3: Extend the import probe in the `gemma-check` target to also probe
  `langchain_openrouter`, so a stale pre-existing `.venv-gemma` fails the probe and
  re-runs the pip install instead of skipping it.

## Acceptance
- A1: `GEMMA_DEPS` includes `langchain-openrouter`.
- A2: The probe line imports `langchain_openrouter`.
- A3: No other Makefile targets changed.

## Constraints
- Single file (`Makefile`); no changes outside it.
