# TASK — 2026-07-06-gemma-standalone
owner: Engineer
immutable: true

## Requirements
- R1: The Gemma health-check must run with plain `python3`, WITHOUT Docker and WITHOUT
  any third-party dependency (no langchain / pydantic / pip install). Standard library
  only. Its single purpose: is the Gemma hosting (NVIDIA OpenAI-compatible endpoint)
  reachable and answering, or not.
- R2: It must resolve GEMMA_API_KEY itself: from the environment, else by reading the
  repo `.env` (search cwd and the script's parent dirs). Defaults match the project:
  model google/gemma-4-31b-it, base_url https://integrate.api.nvidia.com/v1. CLI flags
  override.
- R3: One real minimal POST to {base_url}/chat/completions. Outcomes + exit codes:
  UP=0, DOWN=1 (unreachable / timeout / 5xx / empty), CONFIG=2 (no key / 401 / 403).
  Human-readable by default; `--json` emits one object. Never dump a raw traceback.
- R4: `make gemma-check` invokes it directly with python3 (no docker/compose), still in
  `make help`, still forwards ARGS.

## Acceptance
- A1: py_compile clean; `python3 mcp/scripts/gemma_healthcheck.py --help` works with the
  stdlib only (no external imports anywhere in the module).
- A2: With no key resolvable -> CONFIG, exit 2, no traceback. With a bad endpoint ->
  DOWN, exit 1. .env parsing picks up GEMMA_API_KEY when env var is unset.
- A3: `make gemma-check` runs `python3 .../gemma_healthcheck.py $(ARGS)`; listed in help.

## Constraints
- Standard library only. Two files: mcp/scripts/gemma_healthcheck.py (rewrite), Makefile.
