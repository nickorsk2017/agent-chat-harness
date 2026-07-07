# TASK — 2026-07-06-gemma-langchain
owner: Engineer
immutable: true

## Requirements
- R1: The health-check must use LangChain the same way the agents do — build the model
  with agent_core.llm.build_chat_model from master_orchestrator.config.settings (same
  provider/model/base_url/GEMMA_API_KEY as planner.py / graph.py) and invoke it. This
  also resolves the macOS SSL error: the OpenAI SDK/httpx ship their own CA bundle.
- R2: Runs with plain python3, no Docker. No pip install required to run it: add mcp/ to
  sys.path so agent_core + master_orchestrator import from source (their third-party deps
  langchain-openai / pydantic-settings must be importable in that Python).
- R3: Outcomes/exit codes unchanged: UP=0, DOWN=1, CONFIG=2 (missing key or deps not
  importable). Human-readable + --json. Flags: --model, --base-url, --prompt, --timeout.

## Acceptance
- A1: py_compile clean; `--help` works without the agent deps present.
- A2: real agent_core.llm path — no key -> CONFIG(2, real LLMConfigError); reachable ->
  UP(0); transport error / empty -> DOWN(1).
- A3: Makefile `gemma-check` still runs `python3 mcp/scripts/gemma_healthcheck.py $(ARGS)`
  (unchanged); listed in help.

## Constraints
- Mirror the agents' LLM wiring; no new deps beyond what the agents already require.
  One file changed (mcp/scripts/gemma_healthcheck.py); Makefile unchanged.
