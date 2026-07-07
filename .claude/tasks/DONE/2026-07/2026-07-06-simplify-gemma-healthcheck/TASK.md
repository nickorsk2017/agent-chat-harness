# TASK — 2026-07-06-simplify-gemma-healthcheck
owner: Engineer
immutable: true

## Requirements
- R1: Replace the entire contents of `mcp/scripts/gemma_healthcheck.py` with the
  Engineer-provided minimal test: build `ChatOpenRouter` with
  `model="google/gemma-4-31b-it:free"`, `temperature=0.8`, invoke the
  Super-Bowl/Bieber prompt, print `response.content`.
- R2: Keep it runnable via `make gemma-check`: `ChatOpenRouter` reads
  `OPENROUTER_API_KEY`; the project env provides `GEMMA_API_KEY`, so bridge
  GEMMA_API_KEY -> OPENROUTER_API_KEY if the latter is unset.

## Acceptance
- A1: File contains only the minimal snippet (plus the env bridge), no argparse /
  exit-code machinery / sys.path shims.
- A2: `make gemma-check` runs the script (Makefile unchanged).

## Constraints
- Single file: `mcp/scripts/gemma_healthcheck.py`.
