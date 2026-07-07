# PLAN — 2026-07-06-gemma-standalone
## v1
Approach change: drop the langchain/in-container path. Self-contained stdlib probe.

D1. Rewrite mcp/scripts/gemma_healthcheck.py — imports limited to argparse, json, os,
    sys, time, urllib.request, urllib.error. No project imports, no third-party.
    - Constants mirror the project: DEFAULT_MODEL="google/gemma-4-31b-it",
      DEFAULT_BASE_URL="https://integrate.api.nvidia.com/v1".
    - Key resolution `_resolve_key()`: os.environ["GEMMA_API_KEY"] first; else scan for a
      `.env` walking up from CWD and from the script's own dir, parse `GEMMA_API_KEY=...`
      (strip quotes/whitespace, ignore comments). Return None if not found.
    - Probe `_post()`: POST {base_url}/chat/completions with header Authorization: Bearer,
      JSON body {model, messages:[{role:user,content:prompt}], max_tokens, temperature:0},
      urllib timeout. Read choices[0].message.content.
    - Classification:
        no key                         -> CONFIG (2)
        HTTPError 401/403              -> CONFIG (2)  (key rejected)
        HTTPError other / URLError /
          timeout / empty content       -> DOWN  (1)
        non-empty content              -> UP    (0)
    - Output: default human lines (status, model, endpoint, latency_ms, snippet/error);
      `--json` one object {status,up,model,endpoint,latency_ms,response|error}. Flags:
      --model, --base-url, --prompt, --timeout, --max-tokens, --json. Exit codes central.

D2. Makefile `gemma-check`: replace the docker recipe with a direct call:
      PYTHON ?= python3
      gemma-check: ## ...
          $(PYTHON) mcp/scripts/gemma_healthcheck.py $(ARGS)
    Keep it in `.PHONY` and the help block; ARGS still forwarded.

Files (2). A1<-D1 (stdlib only, --help), A2<-D1 (CONFIG/DOWN + .env), A3<-D2.
