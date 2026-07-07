# PLAN — 2026-07-06-gemma-ssl-trust
## v1
D1. Add `import ssl` (stdlib). New `_ssl_context(insecure)`:
    - insecure -> ssl._create_unverified_context() (check_hostname off, CERT_NONE).
    - else -> try `import certifi`; ssl.create_default_context(cafile=certifi.where())
      when present, otherwise ssl.create_default_context(). Guarded import so absence of
      certifi never breaks the stdlib baseline.
D2. `_post()` gains a `context` param passed to urlopen(..., context=ctx).
D3. CLI: `--insecure` (store_true), default False; also honoured via env
    GEMMA_HEALTHCHECK_INSECURE in {1,true,yes}. When active, print a one-line stderr
    warning ("TLS verification disabled").
D4. Error handling: when the failure reason mentions CERTIFICATE_VERIFY_FAILED, append a
    hint: "local CA store missing — run Python's 'Install Certificates.command' or
    `pip install certifi`, or re-run with --insecure to bypass." Still classified DOWN.
D5. Security note: --insecure is opt-in, off by default, loudly warned. Default path is
    fully verified; certifi only supplies a trusted CA bundle, not a bypass.
Files (1): mcp/scripts/gemma_healthcheck.py. A1<-D1/D3, A2<-D1/D4, A3<-unchanged flow.
