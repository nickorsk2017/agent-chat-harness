# VALIDATION — 2026-07-06-openrouter-per-docs

## v1 — PASS
- A1 PASS: stubbed ChatOpenAI asserts base_url/extra_body; built model =
  google/gemma-4-31b-it:free @ 0.5; cached (get_llm is same object); key taken
  from OPENROUTER_API_KEY and from GEMMA_API_KEY fallback; missing key ->
  LLMConfigError.
- A2 PASS: stubbed openai SDK run: call 1 -> content printed, messages[1]
  carries reasoning_details unmodified into call 2, exit 0.
- A3 PASS: build_chat_model signature unchanged; consumers (providers.py x3,
  planner.py, graph.py) call it with kwargs it still accepts/ignores.
- A4 PASS: grep Makefile+mcp: no langchain(-|_)openrouter references.
- Live OpenRouter call not testable in sandbox (no egress); Engineer runs
  `make gemma-check`.
