# EXEC — 2026-07-06-gemma-standalone
## v1
Rewrote mcp/scripts/gemma_healthcheck.py as a stdlib-only probe (argparse/json/os/sys/
time/urllib). Resolves GEMMA_API_KEY from env or by walking up to a .env from both CWD
and the script dir. POSTs one minimal chat/completions to the NVIDIA endpoint; maps
no-key & HTTP 401/403 -> CONFIG(2), other HTTP/URL/timeout/empty -> DOWN(1), non-empty
reply -> UP(0). Flags: --model --base-url --prompt --timeout --max-tokens --json.
Makefile: added PYTHON ?= python3; gemma-check now runs `$(PYTHON) mcp/scripts/
gemma_healthcheck.py $(ARGS)` — no docker/compose. Two files.
