# VALIDATION — 2026-07-06-gemma-healthcheck-retry

## v1 — PASS
- A1 PASS: stubbed ChatOpenRouter in-sandbox: :free 429s 3x -> falls back to paid
  variant -> prints answer, exit 0. All-fail path: 6 attempts, error to stderr, exit 1.
- A2 PASS: warnings.filterwarnings targets the exact message; diagnostics on stderr,
  answer on stdout.
- Constraint PASS: single file, stdlib only. Live OpenRouter call left to Engineer
  (no egress in sandbox).
