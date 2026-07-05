# CLAUDE.md — Backend (FastAPI / Pydantic gateway + microservices)

Rules for the `backend/` subsystem. These are **in addition to**, never instead of, the
harness in [`.claude/CLAUDE.md`](../.claude/CLAUDE.md) and the root
[`CLAUDE.md`](../CLAUDE.md). All work still goes through the execution harness as a task.

**Precedence on conflict:** `.claude/` harness > root `CLAUDE.md` > this file.

## Folder Map
```
backend/
├── _common/                    # Shared across all microservices
│   ├── db/                     # DeclarativeBase + async session factory
│   ├── schemas/                # Shared Pydantic schemas (ApiResponse envelope)
│   └── env/                    # Environment variable definitions (pydantic-settings)
└── {name}-microservice/        # One folder per bounded context
    └── {name}/                 # Importable package (dir names can't be Python modules)
        ├── routers/            # FastAPI route handlers (thin)
        ├── services/           # Business logic
        ├── models/             # SQLAlchemy ORM models
        ├── schemas/            # Pydantic request/response schemas
        └── main.py             # FastAPI app factory + Uvicorn entry
```
The microservice directory keeps the mandated hyphenated name; its importable code lives
in a nested underscore package (e.g. `gateway-microservice/gateway/`) because Python
module names can't contain hyphens.

## Layers (respect boundaries)
- `routers/` — HTTP only. Validate input, call a service, return an `ApiResponse`
  envelope. No business logic, no MCP/DB calls inline.
- `services/` — business logic. The orchestrator MCP client and request mapping live
  here. Services accept and return Pydantic models, never raw dicts.
- `models/` — SQLAlchemy 2.x ORM models on the shared `_common.db.Base`.
- `schemas/` — Pydantic request/response contracts.
- `_common/` — shared envelope (`ApiResponse[T]`), settings, db primitives. No service
  may import another microservice; they share only `_common`.

## Rules
1. **Contracts first.** Define `schemas/` before routers. Cross-boundary data is always a
   Pydantic model.
2. **Thin routers.** Endpoints validate + delegate + envelope. Logic lives in `services/`.
3. **One envelope.** Every REST response is `ApiResponse[T]`:
   `{ status: "Success" | "Failed", data?: T, error_text?: string }`.
4. **Config, not constants.** URLs, modes, timeouts, origins, DB URL come from
   `_common/env` (env-backed). No hardcoded secrets.
5. **Fail soft.** No exception crosses the HTTP boundary as an unstructured 500 — wrap it
   in `ApiResponse.fail(...)` at HTTP 200.
6. **Mock by default.** External integrations (the orchestrator MCP client) sit behind an
   interface with a mock implementation selected by config, so the backend runs with zero
   external processes. Swap to real via `GATEWAY_ORCHESTRATOR_MODE=http`.
7. **MCP boundary.** The gateway is an MCP *client* of `master_orchestrator`; it calls the
   `orchestrate` tool and maps the returned envelope. It never imports `mcp/` packages.

## Stack conventions
- Python ≥ 3.11, async-first, fully type-hinted.
- FastAPI (latest), Pydantic v2, pydantic-settings, SQLAlchemy 2.x, fastmcp (MCP client),
  uvicorn — pinned in `pyproject.toml`.

## Running
```
cd backend
pip install -e .[dev]
GATEWAY_ORCHESTRATOR_MODE=mock uvicorn gateway.main:app --app-dir gateway-microservice
# POST http://localhost:8000/api/chat  {"prompt":"hello"}
```
