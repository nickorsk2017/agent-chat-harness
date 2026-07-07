# TASK — 2026-07-06-gemma-venv-bootstrap
owner: Engineer
immutable: true

## Requirements
- R1: `make gemma-check` fails on the host with "No module named 'langchain_core'": the
  agents get LangChain from the mcp Docker image, but the host python3 has no such deps.
  The target must work docker-free without the user manually installing anything.
- R2: Bootstrap a dedicated local virtualenv (.venv-gemma) on first run, install just the
  deps the LangChain probe needs (langchain, langchain-openai, pydantic-settings), and run
  the script through it. Idempotent + fast on subsequent runs. Overridable via PYTHON.
- R3: Do not commit the venv (gitignore it).

## Acceptance
- A1: `make -n gemma-check` shows: create venv if missing -> import-check-or-pip-install
  -> run script via the venv python. Listed in `make help`.
- A2: `python3 -m venv` works offline; script compiles; CONFIG/UP/DOWN branches pass via
  the real build_chat_model (import path `from langchain.schema import HumanMessage`).
- A3: .gitignore contains .venv-gemma/.

## Constraints
- Two files: Makefile, .gitignore. Respect the in-tree import path in the script.
