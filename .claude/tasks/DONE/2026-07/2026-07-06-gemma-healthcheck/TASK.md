# TASK — 2026-07-06-gemma-healthcheck
owner: Engineer
immutable: true

## Requirements
- R1: Provide a health-check that answers one question — is the Gemma model
  (google/gemma-4-31b-it via the NVIDIA OpenAI-compatible endpoint) reachable and
  responding, or not. It must make a REAL minimal call (no mock), reusing the
  existing agent_core.llm.build_chat_model factory + OrchestratorSettings so it
  uses the same GEMMA_API_KEY / model / base_url as the running agents.
- R2: The check must be runnable from the Makefile with a single target, using the
  existing docker-compose-based tooling (deps live in the mcp image). Allow passing
  extra CLI flags through the target.
- R3: Clear, distinct outcomes with distinct exit codes: UP (0), DOWN/unreachable (1),
  misconfigured/missing key (2). Human-readable by default, with a --json mode for
  automation. Report model, endpoint, latency, and a response snippet or the error.

## Acceptance
- A1: mcp/scripts/gemma_healthcheck.py compiles (py_compile) and, run with no
  GEMMA_API_KEY, exits 2 with a clear "misconfigured" message (never a stack trace).
- A2: `make gemma-check` exists, is listed in `make help`, runs the script inside the
  mcp container, and forwards ARGS (e.g. `make gemma-check ARGS="--json"`).
- A3: --json emits a single parseable object with status/model/endpoint/latency_ms.

## Constraints
- No new dependencies (langchain-openai already ships in the mcp image).
- No mock fallback; do not weaken the existing "GEMMA_API_KEY required" contract.
