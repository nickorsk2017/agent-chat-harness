# PLAN — 2026-07-06-gemma-healthcheck
## v1
Goal: a single, real "is Gemma up?" probe reusing the fleet's own LLM wiring, plus a
Makefile entry point. No new deps, no mock.

D1. New file `mcp/scripts/gemma_healthcheck.py` (standalone module, no package install
    needed — imports the already-installed `agent_core` + `master_orchestrator`).
    - Read config from `master_orchestrator.config.OrchestratorSettings()` so the probe
      uses the SAME provider/model/base_url/GEMMA_API_KEY the agents use (single source
      of truth; picks up `.env` via SettingsConfigDict). CLI flags override.
    - Build the model with `agent_core.llm.build_chat_model(...)`. A missing key raises
      `LLMConfigError` at build time -> catch -> CONFIG outcome (exit 2), no traceback.
    - Probe = one minimal `invoke([HumanMessage("ping ... reply OK")])` wrapped in a
      wall clock. Any exception (auth/network/timeout/HTTP) -> DOWN (exit 1). A
      non-empty reply -> UP (exit 0).
    - Output: default = human line (status, model, endpoint, latency_ms, snippet/error).
      `--json` = one object {status, up, model, endpoint, latency_ms, response|error}.
      Flags: `--model`, `--base-url`, `--prompt`, `--timeout`, `--json`.
    - Exit codes centralised: UP=0, DOWN=1, CONFIG=2.

D2. `Makefile`: add `.PHONY` target `gemma-check` (declare in the existing `.PHONY`
    line) with a `## Check whether the Gemma model is reachable` help comment so it
    shows in `make help`. Body runs the script in the mcp image via
    `$(COMPOSE) run --rm --no-deps mcp python /app/scripts/gemma_healthcheck.py $(ARGS)`.
    `--no-deps` avoids spinning up postgres; `ARGS` forwards flags. The compose `mcp`
    service already injects GEMMA_API_KEY (with a `:?` guard) so a missing key fails
    fast with a clear compose-level message too.

Files (2): mcp/scripts/gemma_healthcheck.py (new), Makefile (edit).
Acceptance mapping: A1<-D1 (compile + CONFIG path), A2<-D2 (target + help + ARGS),
A3<-D1 (--json object).
