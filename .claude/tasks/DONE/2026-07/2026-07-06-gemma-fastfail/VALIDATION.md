# VALIDATION — 2026-07-06-gemma-fastfail
validation_version: 1
result: PASS

## v1 — PASS
A1: `--help` shows `--timeout ... default 60`; default 60.0 sets LLM_REQUEST_TIMEOUT_S.
A2: stubbed ChatOpenAI asserts max_retries==0 at invoke — UP(0) passes with the assertion,
    confirming the probe disabled retry; CONFIG(2)/DOWN(1) branches unaffected.
A3: an APITimeoutError-shaped exception -> DOWN(1) with the appended remediation hint
    ("no completion within 60s ... try a longer --timeout or a different --model").
py_compile clean. One file; no shared agent-code change.
