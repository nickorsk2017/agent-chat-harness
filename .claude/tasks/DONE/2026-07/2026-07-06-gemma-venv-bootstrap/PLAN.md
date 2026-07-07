# PLAN — 2026-07-06-gemma-venv-bootstrap
## v1
D1. Makefile vars: GEMMA_VENV ?= .venv-gemma; GEMMA_PY = $(GEMMA_VENV)/bin/python;
    GEMMA_DEPS = langchain langchain-openai pydantic-settings.
D2. gemma-check recipe (3 quiet steps):
    (a) test -x $(GEMMA_PY) || $(PYTHON) -m venv $(GEMMA_VENV)
    (b) $(GEMMA_PY) -c 'import langchain_openai, pydantic_settings; from langchain.schema
        import HumanMessage' 2>/dev/null || $(GEMMA_PY) -m pip install -q ... $(GEMMA_DEPS)
    (c) $(GEMMA_PY) mcp/scripts/gemma_healthcheck.py $(ARGS)
    Import check mirrors exactly what the script imports so a partial venv self-heals.
D3. .gitignore += .venv-gemma/.
Files (2). langchain (full) included because the script imports langchain.schema.
