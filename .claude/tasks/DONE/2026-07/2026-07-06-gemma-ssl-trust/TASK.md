# TASK — 2026-07-06-gemma-ssl-trust
owner: Engineer
immutable: true

## Requirements
- R1: On macOS the real call fails with `SSL: CERTIFICATE_VERIFY_FAILED ... unable to get
  local issuer certificate`. The endpoint is reachable (TLS handshake happens); the local
  Python (python.org build) just has no CA bundle. The check must handle this without
  requiring the user to change their Python install.
- R2: Verification stays ON by default and secure. If `certifi` is importable, use its CA
  bundle automatically (still stdlib-only baseline — certifi is optional, not required).
- R3: On a certificate-verify failure, the DOWN message must include an actionable hint
  (macOS "Install Certificates.command" / `pip install certifi`) instead of a bare error.
- R4: Provide an explicit opt-in escape hatch `--insecure` (also env
  GEMMA_HEALTHCHECK_INSECURE=1) that disables TLS verification so the user can confirm the
  hosting is up right now. It is OFF by default and prints a visible warning when used.

## Acceptance
- A1: py_compile clean; module still imports with the standard library alone (certifi used
  only if present, via a guarded import); `--help` shows `--insecure`.
- A2: `--insecure` builds an unverified context (no CERT verify); default builds a verified
  context (certifi bundle when available). A simulated cert-verify error yields a DOWN
  message containing the remediation hint.
- A3: Exit-code contract unchanged (UP=0, DOWN=1, CONFIG=2); Makefile untouched.

## Constraints
- Standard library only for the baseline; `certifi` is an optional runtime enhancement.
  One file changed (mcp/scripts/gemma_healthcheck.py).
