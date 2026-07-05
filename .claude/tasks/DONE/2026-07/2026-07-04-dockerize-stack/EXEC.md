# EXEC — 2026-07-04-dockerize-stack

## v1

### Files created (new only; no application source touched)
- `frontend/Dockerfile` — multi-stage (deps/build/runner), node:22-alpine, pnpm@10.13.1,
  `pnpm build` then `CMD pnpm start`, EXPOSE 3000.
- `frontend/.dockerignore`
- `backend/Dockerfile` — python:3.11-slim, `pip install ".[sqlite]"` (installs `_common`
  + `gateway` per hatch `packages`), `CMD uvicorn gateway.main:app :8000`, EXPOSE 8000.
- `backend/.dockerignore`
- `mcp/Dockerfile` — python:3.11-slim, installs `agent_core` first then web/doc/image
  sub-agents + `master_orchestrator`; `CMD` runs FastMCP streamable-http on 0.0.0.0:8100.
- `mcp/.dockerignore`
- `docker-compose.yml` — services mcp, backend, frontend on bridge net `agentnet`;
  ports 8100/8000/3000; env via `${VAR:-default}`; depends_on ordering; restart policies.
- `Makefile` — default `help`; targets up, up-fg, down, build, rebuild, logs, ps,
  restart, clean (all wrapping `docker compose`).
- `.env.example` — documents port + mode overrides consumed by compose.

### Key decisions realised from PLAN v1
- MCP HTTP transport selected via container CMD (`mcp.run(transport='streamable-http',
  host='0.0.0.0', port=8100)`), so `mcp/master_orchestrator/main.py` is unchanged.
- Sub-agents installed into the mcp image (not separate services) — orchestrator spawns
  them over stdio, matching the "three units" request.
- Gateway defaults to `mock` orchestrator mode -> stack runs end-to-end even before the
  http path is exercised; flip `GATEWAY_ORCHESTRATOR_MODE=http` in `.env` to route to mcp.

### One-command usage
`make up` -> `docker compose up -d --build`; `make down` to stop; `make logs` to tail.
