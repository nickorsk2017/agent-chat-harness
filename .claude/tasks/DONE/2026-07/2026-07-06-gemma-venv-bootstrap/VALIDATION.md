# VALIDATION — 2026-07-06-gemma-venv-bootstrap
validation_version: 1
result: PASS

## v1 — PASS
A1: `make -n gemma-check` expands to venv-create-if-missing -> import-check || pip install
    (langchain langchain-openai pydantic-settings) -> `.venv-gemma/bin/python mcp/scripts/
    gemma_healthcheck.py`; still in `make help`.
A2: `python3 -m venv` verified offline; py_compile clean; CONFIG (exit 2, real
    LLMConfigError) / UP (exit 0) / DOWN (exit 1) confirmed through the real
    build_chat_model with the `langchain.schema` HumanMessage path stubbed.
A3: .gitignore contains `.venv-gemma/`.

Note: pip install itself needs network at first run on the host (expected); not
exercisable in the offline build sandbox, but the venv + expansion + branch logic are.
Two files changed.
