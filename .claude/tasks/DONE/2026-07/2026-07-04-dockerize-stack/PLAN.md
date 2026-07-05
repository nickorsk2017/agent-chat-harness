# PLAN — 2026-07-04-dockerize-stack

## v1

### Topology
Three build contexts, one compose project, one bridge network `agentnet`.

| Service  | Context     | Base image        | Start command                                             | Host:Container |
|----------|-------------|-------------------|-----------------------------------------------------------|----------------|
| frontend | ./frontend  | node:22-alpine    | `pnpm start` (after `next build`)                         | 3000:3000      |
| backend  | ./backend   | python:3.11-slim  | `uvicorn gateway.main:app --host 0.0.0.0 --port 8000`     | 8000:8000      |
| mcp      | ./mcp       | python:3.11-slim  | FastMCP `streamable-http` on 0.0.0.0:8100 (`/mcp`)         | 8100:8100      |

### Rationale
- Only three services are required (the user's frontend/backend/mcp). The MCP fleet's
  three sub-agents (web/doc/image) are NOT separate containers: `master_orchestrator`
  spawns them in-process over stdio (`python -m <agent>.main`), so they only need to be
  installed inside the `mcp` image — this keeps the compose file to the three requested
  units while preserving the parallel fan-out behaviour.
- No application source changes. The mcp HTTP transport is selected at run time by the
  container command (`mcp.run(transport="streamable-http", host, port)`) rather than
  editing `main.py`, honouring the "config not code" constraint.

### frontend/Dockerfile (multi-stage)
1. `deps`: enable corepack -> pnpm@10.13.1, `pnpm install --frozen-lockfile`.
2. `build`: copy source, `pnpm build` (Next 16 App Router).
3. `runner`: copy `.next`, `public`, `node_modules`, `package.json`; `EXPOSE 3000`;
   `CMD ["pnpm","start"]`. `NODE_ENV=production`.

### backend/Dockerfile
- `python:3.11-slim`; `pip install ./ .[sqlite]` from backend context so both `_common`
  and `gateway` import packages (hatch `packages=[...]`) plus aiosqlite land in the image.
- `EXPOSE 8000`; `CMD ["uvicorn","gateway.main:app","--host","0.0.0.0","--port","8000"]`.

### mcp/Dockerfile
- `python:3.11-slim`; install in dependency order:
  `pip install ./agent_core` then `./web_agent ./doc_analyzer ./image_analyzer
  ./master_orchestrator`. `agent_core` first because every agent depends on it.
- `EXPOSE 8100`; `CMD ["python","-c","from master_orchestrator.main import mcp;
  mcp.run(transport='streamable-http', host='0.0.0.0', port=8100)"]`.

### docker-compose.yml
- `services: frontend, backend, mcp` on network `agentnet`.
- `backend.depends_on: [mcp]`; `frontend.depends_on: [backend]` (ordering only).
- Env wiring via `${VAR:-default}` so `.env` (optional) can override:
  - backend: `GATEWAY_HOST=0.0.0.0`, `GATEWAY_PORT=8000`,
    `GATEWAY_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]`,
    `GATEWAY_ORCHESTRATOR_MODE=${GATEWAY_ORCHESTRATOR_MODE:-mock}` (safe default),
    `GATEWAY_ORCHESTRATOR_MCP_URL=http://mcp:8100/mcp` (used when mode=http).
  - frontend: `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` (host-visible).
- `restart: unless-stopped` on backend/mcp. `ports` per table above.

### Makefile (default target = help)
`help` (auto), `up` (compose up -d --build), `up-fg` (foreground), `down`,
`build`, `logs` (follow), `ps`, `restart`, `clean` (down -v --rmi local).
Uses `docker compose` v2 syntax; single `COMPOSE` variable for reuse.

### .dockerignore
- `frontend/.dockerignore`: node_modules, .next, .git, *.log.
- `backend/.dockerignore` + `mcp/.dockerignore`: __pycache__, *.pyc, .venv, .pytest_cache,
  .git, build/dist, *.db.

### .env.example (root)
Document `GATEWAY_ORCHESTRATOR_MODE` (mock|http) and port overrides for compose.

### Risk / verification
- Cannot run a full Docker build in this environment (no daemon); Validator verifies
  statically: `docker compose config` if available, else YAML/Dockerfile lint + a check
  that every referenced path (packages, lockfile, entrypoints) exists in the repo.
