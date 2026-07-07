# PLAN — 2026-07-06-gemma-langchain
## v1
Supersedes the manual-HTTP probe; return to the agents' LangChain wiring.
D1. Rewrite mcp/scripts/gemma_healthcheck.py:
    - sys.path.insert(0, <mcp dir>) computed from __file__ so `import agent_core` and
      `master_orchestrator` resolve from source without pip install.
    - Lazy imports: `from agent_core.llm import LLMConfigError, build_chat_model`,
      `from langchain_core.messages import HumanMessage`,
      `from master_orchestrator.config import settings`. Import failure -> CONFIG.
    - Build via build_chat_model(provider/model/api_key/base_url from settings) exactly
      like planner.build_planner_chain / graph. Missing key -> LLMConfigError -> CONFIG.
    - `chat.invoke([HumanMessage(prompt)])` is the up/down test; any exception -> DOWN,
      empty content -> DOWN, non-empty -> UP.
    - --timeout sets LLM_REQUEST_TIMEOUT_S before the factory import (agent_core reads it).
    - Keep --json + human output + exit-code map.
D2. Makefile: no change (already `$(PYTHON) mcp/scripts/gemma_healthcheck.py $(ARGS)`).
Files (1). SSL: handled implicitly by openai/httpx bundled certs (fixes the macOS error).
