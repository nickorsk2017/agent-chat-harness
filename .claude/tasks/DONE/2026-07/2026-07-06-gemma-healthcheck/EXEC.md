# EXEC — 2026-07-06-gemma-healthcheck
## v1
Per PLAN v1. Two files.

- mcp/scripts/gemma_healthcheck.py (new): standalone probe. Config via
  OrchestratorSettings() (same GEMMA_API_KEY/model/base_url as agents); model via
  agent_core.llm.build_chat_model. One HumanMessage invoke is the up/down test.
  Outcomes + exit codes: UP=0, DOWN=1, CONFIG=2. Missing key -> LLMConfigError caught
  -> CONFIG (no traceback). Any invoke exception / empty reply -> DOWN. Flags:
  --model, --base-url, --prompt, --timeout (sets LLM_REQUEST_TIMEOUT_S), --json.
  --json prints one object {status,up,model,endpoint,latency_ms,response|error}.
  Imports are lazy so --help works without deps and import failure reports CONFIG.
- Makefile (edit): added `gemma-check` to .PHONY and a target with `## Check whether
  the Gemma model is reachable` help. Runs `$(COMPOSE) run --rm --no-deps mcp python
  /app/scripts/gemma_healthcheck.py $(ARGS)`. --no-deps skips postgres; ARGS forwards
  flags; compose mcp service already injects GEMMA_API_KEY (:? guard).

Not excluded by mcp/.dockerignore, so scripts/ ships in the image at /app/scripts.
