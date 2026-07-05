# TASK — 2026-07-04-dockerize-stack
owner: Engineer
immutable: true

## Requirements
- R1: Provide a Dockerfile for each of the three subsystems — `frontend` (Next.js),
  `backend` (FastAPI gateway), and `mcp` (master_orchestrator + sub-agents).
- R2: Provide a single `docker-compose.yml` at the repo root that builds and runs all
  three services together on one network.
- R3: Provide a root `Makefile` so the whole stack starts with one command (`make up`)
  and stops with one command (`make down`), plus build/logs/ps/clean helpers.
- R4: Do not modify existing application source. Configuration must flow through
  environment variables that already exist (GATEWAY_*, ORCHESTRATOR_*, WEB_AGENT_*).
- R5: Host ports: frontend 3000, backend gateway 8000, mcp 8100.

## Acceptance
- A1: `docker compose config` parses with no error and lists services frontend, backend, mcp.
- A2: Each Dockerfile references a valid base image, installs its subsystem's deps, and
  defines a runnable start command (frontend `next start`, backend uvicorn, mcp FastMCP).
- A3: `make up` / `make down` / `make build` / `make logs` targets exist and map to the
  corresponding `docker compose` commands; `make` with no target prints help.
- A4: Backend and mcp are wired so the gateway can reach the orchestrator at
  `http://mcp:8100/mcp` (http mode), with a safe `mock` default that runs standalone.
- A5: `.dockerignore` files keep node_modules / caches / venvs out of build contexts.

## Constraints
- No changes to application code (frontend/, backend/, mcp/ Python & TS sources).
- New files only: Dockerfiles, docker-compose.yml, Makefile, .dockerignore, .env.example.
- Frameworks stay on their pinned versions; no dependency changes.
