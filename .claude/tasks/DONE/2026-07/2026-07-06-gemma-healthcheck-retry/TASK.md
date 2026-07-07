# TASK — 2026-07-06-gemma-healthcheck-retry
owner: Engineer
immutable: true

## Requirements
- R1: `make gemma-check` intermittently fails with OpenRouter 429
  (TooManyRequests) on `google/gemma-4-31b-it:free` — shared free pool.
- R2: Retry each attempt with backoff (3 tries), then fall back from `:free` to the
  paid `google/gemma-4-31b-it` variant.
- R3: Silence the harmless "Core Pydantic V1 ... Python 3.14" UserWarning.
- R4: Exit 0 with the model answer on success; exit 1 with the last error otherwise.

## Acceptance
- A1: 429 on `:free` no longer kills the check immediately (retries + fallback).
- A2: Warning suppressed; retry progress goes to stderr, answer to stdout.

## Constraints
- Single file: `mcp/scripts/gemma_healthcheck.py`. Stdlib only.
