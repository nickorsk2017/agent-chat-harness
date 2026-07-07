# VALIDATION — 2026-07-06-fix-gemma-check-mount
validation_version: 1
result: PASS

## v1 — PASS
A1: `make -n gemma-check ARGS="--json"` expands to a single `docker compose run --rm
    --no-deps -v "<repo>/mcp/scripts:/app/scripts:ro" mcp python
    /app/scripts/gemma_healthcheck.py --json` — current host script mounted over the
    image path, so image age is irrelevant; ARGS forwarded; --no-deps preserved.
A2: Makefile parses (make -n succeeds); `make help` still lists `gemma-check`; no other
    target touched. One file changed. LOW scope holds.
