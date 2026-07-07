# EXEC — 2026-07-06-fix-gemma-check-deps

## v1
Changed file: `Makefile` (only).
- L10 `GEMMA_DEPS`: added `langchain-openrouter` between `langchain-openai` and
  `pydantic-settings` (R2).
- L50 probe in `gemma-check`: added `langchain_openrouter` to the import list, so a
  stale `.venv-gemma` fails the probe and triggers the pip install branch (R3).
No other targets or files touched (A3). Verified by inspecting lines 8-10 and 48-52
after edit.
