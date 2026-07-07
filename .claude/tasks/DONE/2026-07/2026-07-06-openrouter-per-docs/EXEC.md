# EXEC — 2026-07-06-openrouter-per-docs

## v1
Per PLAN v1:
1. `mcp/agent_core/llm.py`: ChatOpenAI @ https://openrouter.ai/api/v1, key from
   OPENROUTER_API_KEY then GEMMA_API_KEY, DEFAULT_MODEL env GEMMA_MODEL default
   `google/gemma-4-31b-it:free`, extra_body reasoning enabled; public surface
   (build_chat_model/get_llm/LLMConfigError/aliases) unchanged.
2. `mcp/scripts/gemma_healthcheck.py`: docs-literal two-call reasoning example on
   raw openai SDK; kept root-.env loader + key bridge; errors -> stderr, exit 1.
3. `mcp/agent_core/pyproject.toml`: removed langchain-openrouter.
4. `Makefile`: GEMMA_DEPS w/o langchain-openrouter; probe imports
   langchain_openai, openai, pydantic_settings.
py_compile OK; repo-wide grep: zero langchain-openrouter references.
