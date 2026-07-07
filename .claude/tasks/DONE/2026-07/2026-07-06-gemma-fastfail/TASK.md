# TASK — 2026-07-06-gemma-fastfail
owner: Engineer
immutable: true

## Requirements
- R1: `make gemma-check` now reaches the endpoint but hangs ~181s then APITimeoutError.
  Cause: agent_core default LLM_REQUEST_TIMEOUT_S=90 x build_chat_model max_retries=1 =
  ~180s. A health-check must fail fast and explain the likely cause.
- R2: Single attempt (no retry) for the probe; shorter default timeout; on a timeout,
  emit an actionable hint (cold/overloaded model, model id not served to this key, or
  missing entitlement; suggest longer --timeout or a different --model). Keep the agents'
  LangChain wiring otherwise; do not modify shared agent code.

## Acceptance
- A1: default --timeout is 60 and sets LLM_REQUEST_TIMEOUT_S; --help reflects it.
- A2: the built model runs with max_retries=0 (probe-local, best-effort, no shared-code
  change); UP/DOWN/CONFIG branches still pass.
- A3: a timeout-type exception -> DOWN with the remediation hint appended.

## Constraints
- One file (mcp/scripts/gemma_healthcheck.py). No change to agent_core/master_orchestrator.
