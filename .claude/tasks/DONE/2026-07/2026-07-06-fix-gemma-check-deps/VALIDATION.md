# VALIDATION — 2026-07-06-fix-gemma-check-deps

## v1 — PASS
- A1 PASS: `GEMMA_DEPS = langchain langchain-openai langchain-openrouter pydantic-settings`.
- A2 PASS: probe line now `import langchain_openai, langchain_openrouter, pydantic_settings; ...` — a stale `.venv-gemma` fails it and re-installs.
- A3 PASS: `git diff Makefile` confined to GEMMA_DEPS + probe (other hunks in repo diff belong to prior tasks); `make -n gemma-check` expands correctly.
- Dep name verified against PyPI: `langchain-openrouter` 0.2.3 (langchain-ai, May 2026).
- Note: live `make gemma-check` not runnable in validation sandbox (PyPI egress blocked); install path is deterministic pip.
