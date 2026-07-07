# VALIDATION — 2026-07-06-gemma-healthcheck
validation_version: 1
result: PASS

## v1 — PASS
Verified against acceptance (real code paths; only the langchain transport + config
source were stubbed offline — agent_core.llm and the script itself ran unmodified).

A1: `python -m py_compile scripts/gemma_healthcheck.py` clean. With no GEMMA_API_KEY the
    REAL `agent_core.llm.build_chat_model` raises `LLMConfigError`, caught -> status
    CONFIG, exit 2, no traceback (also true if the agent stack can't be imported).
A2: `make gemma-check` present, added to `.PHONY`, help comment matches the `make help`
    grep so it lists; body runs the script in the mcp image via
    `docker compose run --rm --no-deps mcp ... $(ARGS)` (postgres skipped, ARGS forwarded).
A3: `--json` emits one parseable object with status/up/model/endpoint/latency_ms and
    response|error. Exit-code contract confirmed end to end:
      reachable reply  -> UP,   exit 0
      transport error  -> DOWN, exit 1
      empty reply      -> DOWN, exit 1
      missing key      -> CONFIG, exit 2
    `--model` override and `--timeout` (sets LLM_REQUEST_TIMEOUT_S) also confirmed.

No new dependencies; the GEMMA_API_KEY-required contract is preserved (no mock path).
Scope = 2 files (matches PLAN v1); MEDIUM classification holds.
