# VALIDATION — 2026-07-06-gemma-standalone
validation_version: 1
result: PASS

## v1 — PASS
A1: py_compile clean; AST import audit shows only stdlib (argparse, json, os, sys, time,
    urllib) — non-stdlib: NONE; `--help` works standalone.
A2: isolated run with no key/.env -> CONFIG, exit 2, no traceback; unreachable endpoint
    -> DOWN, exit 1; `_resolve_key()` reads GEMMA_API_KEY from the repo .env when the env
    var is unset. A live call to the real endpoint returns DOWN here only because the
    build sandbox blocks egress (403 tunnel) — not a script fault; UP path exercised via
    the OpenAI-shaped response parser.
A3: `make -n gemma-check` expands to `python3 mcp/scripts/gemma_healthcheck.py --json`
    (no docker); target listed in `make help`; ARGS forwarded.

Standard library only; no Docker; no third-party deps. Two files (script rewrite +
Makefile), matches PLAN v1.
