# EXEC — 2026-07-06-gemma-venv-bootstrap
## v1
Makefile: added GEMMA_VENV/GEMMA_PY/GEMMA_DEPS; gemma-check now (a) creates .venv-gemma via
$(PYTHON) -m venv if absent, (b) installs langchain+langchain-openai+pydantic-settings only
when the exact imports the script uses are missing, (c) runs the probe with the venv python
and forwards ARGS. .gitignore: added .venv-gemma/. Two files. Script unchanged.
