# EXEC — 2026-07-06-gemma-healthcheck-retry

## v1
`mcp/scripts/gemma_healthcheck.py`: kept .env loader + key bridge; added
warnings filter for the Pydantic-V1/py3.14 UserWarning (R3); wrapped the invoke in
retry loop — 3 attempts with 2s/4s backoff per model, model order
[gemma-4-31b-it:free, gemma-4-31b-it] (R1/R2); answer -> stdout & exit 0, retry
progress + final error -> stderr & exit 1 (R4). Stdlib only. py_compile OK.
