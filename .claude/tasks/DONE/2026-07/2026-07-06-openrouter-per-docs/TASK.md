# TASK — 2026-07-06-openrouter-per-docs
owner: Engineer
immutable: true

## Requirements
- R1: Align the LLM stack with the OpenRouter quickstart the Engineer supplied:
  OpenAI-compatible API at `https://openrouter.ai/api/v1`, auth via
  `OPENROUTER_API_KEY`, model `google/gemma-4-31b-it:free`, reasoning enabled
  (`{"reasoning": {"enabled": true}}`), `reasoning_details` preserved on
  conversation continuation.
- R2: `mcp/agent_core/llm.py` — the shared app-wide model must follow that scheme
  while still returning a LangChain `BaseChatModel` (all sub-agents consume it via
  `build_chat_model`/`get_llm`; public API must not change).
- R3: `mcp/scripts/gemma_healthcheck.py` — replace with the docs' Python example
  (two-call strawberry test with reasoning_details passthrough), keeping the
  root-.env key loading so `make gemma-check` works.
- R4: Drop the now-unused `langchain-openrouter` dependency everywhere it was added
  (agent_core/pyproject.toml, Makefile GEMMA_DEPS + probe).

## Acceptance
- A1: llm.py builds the model with base_url=openrouter, OPENROUTER_API_KEY (fallback
  GEMMA_API_KEY), default model `google/gemma-4-31b-it:free`, reasoning enabled.
- A2: healthcheck mirrors the docs example and prints both answers; key comes from
  env or root .env.
- A3: No consumer (providers.py/planner.py/graph.py/config.py) needs changes.
- A4: No references to `langchain_openrouter` remain in code, deps, or Makefile.
