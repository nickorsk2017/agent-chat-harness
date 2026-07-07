# VALIDATION — 2026-07-06-gemma-ssl-trust
validation_version: 1
result: PASS

## v1 — PASS
A1: py_compile clean; certifi imported only via a guarded in-function try (baseline stays
    stdlib-only); `--help` lists `--insecure`.
A2: `_ssl_context(False)` -> CERT_REQUIRED + check_hostname True; `_ssl_context(True)` ->
    CERT_NONE + check_hostname False; `_cert_hint` present for CERTIFICATE_VERIFY_FAILED,
    empty otherwise; `--insecure` prints the stderr warning.
A3: exit-code contract intact (DOWN=1 shown on unreachable endpoint); Makefile untouched.
