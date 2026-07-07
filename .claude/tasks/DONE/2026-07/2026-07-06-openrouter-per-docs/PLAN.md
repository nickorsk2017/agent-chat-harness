# PLAN — 2026-07-06-openrouter-per-docs

## v1
Decision: the docs' Python example uses the `openai` SDK against OpenRouter's
OpenAI-compatible endpoint. For the app (LangChain graph/agents) the equivalent is
`langchain_openai.ChatOpenAI(base_url=OPENROUTER_BASE_URL, ...)` — same wire
protocol, returns BaseChatModel, and `extra_body={"reasoning": {"enabled": True}}`
carries the reasoning flag. For the standalone healthcheck use the raw `openai`
SDK exactly as in the docs (it ships as a dependency of langchain-openai, so no
new dep in GEMMA_DEPS).

Changes:
1. `mcp/agent_core/llm.py`
   - import ChatOpenAI (drop langchain_openrouter).
   - DEFAULT_MODEL = env GEMMA_MODEL, default "google/gemma-4-31b-it:free".
   - key resolution: OPENROUTER_API_KEY first, then GEMMA_API_KEY (bridge kept).
   - ChatOpenAI(model, api_key, base_url=OPENROUTER_BASE_URL, temperature,
     timeout, max_retries=1, extra_body={"reasoning": {"enabled": True}}).
   - keep public surface: build_chat_model(signature unchanged, extras ignored),
     get_llm, LLMConfigError, NVIDIA_* aliases.
2. `mcp/scripts/gemma_healthcheck.py`
   - keep _load_root_dotenv + OPENROUTER/GEMMA bridge.
   - then verbatim-docs flow: OpenAI(base_url, api_key) -> call 1 (strawberry,
     reasoning enabled) -> rebuild messages preserving reasoning_details ->
     call 2 ("Are you sure?") -> print both contents. Exit 0 on success; print
     error + exit 1 otherwise. No retry machinery (Engineer chose docs-literal).
3. `mcp/agent_core/pyproject.toml` — remove "langchain-openrouter".
4. `Makefile` — GEMMA_DEPS drop langchain-openrouter; probe imports back to
   `langchain_openai, openai, pydantic_settings`.

Risk: langchain-openai's ChatOpenAI must support `extra_body` kwarg — it does
(pinned latest stable per root CLAUDE.md). Consumers pass provider/model/base_url
kwargs that build_chat_model already ignores -> A3 holds.
