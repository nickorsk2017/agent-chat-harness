# VALIDATION — 2026-07-06-gemma-langchain
validation_version: 1
result: PASS

## v1 — PASS
A1: py_compile clean; `--help` runs with stdlib only (agent imports are lazy).
A2: Exercised the REAL agent_core.llm.build_chat_model with langchain transport + the
    settings singleton stubbed: no key -> CONFIG exit 2 (genuine LLMConfigError text);
    reachable reply -> UP exit 0; RuntimeError from invoke -> DOWN exit 1; empty content
    -> DOWN exit 1. Model/base_url default to settings (google/gemma-4-31b-it, NVIDIA).
A3: Makefile `gemma-check` unchanged — `make -n` -> `python3 mcp/scripts/
    gemma_healthcheck.py`; still in `make help`.

Matches agents' wiring (build_chat_model from settings, as planner.py). The macOS
CERTIFICATE_VERIFY_FAILED is resolved because the OpenAI SDK/httpx use bundled CA certs.
One file changed; Makefile untouched.
