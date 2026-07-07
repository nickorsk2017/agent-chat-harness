# EXEC — 2026-07-06-gemma-ssl-trust
## v1
Added `import ssl`. New `_ssl_context(insecure)`: verified by default, using certifi's CA
bundle when importable (guarded import — stdlib baseline unaffected if absent), else the
interpreter default; `--insecure` -> unverified context. `_post()` takes the context and
passes it to urlopen. CLI `--insecure` (also env GEMMA_HEALTHCHECK_INSECURE) prints a
stderr warning when active. On CERTIFICATE_VERIFY_FAILED the DOWN error appends a
remediation hint (Install Certificates.command / pip install certifi / --insecure). One
file. Exit-code contract and Makefile unchanged.
