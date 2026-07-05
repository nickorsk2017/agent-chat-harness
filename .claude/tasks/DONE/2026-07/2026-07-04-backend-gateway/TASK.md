# TASK — 2026-07-04-backend-gateway
owner: Engineer
immutable: true

## Requirements
- R1: Create the `backend/` subsystem in Python using FastAPI + Pydantic (all latest
  stable versions), following the mandated Folder Map:
  - `backend/_common/db/`      — base models, session factory (shared).
  - `backend/_common/schemas/` — shared Pydantic schemas (response envelope).
  - `backend/_common/env/`     — environment variable definitions (settings).
  - `backend/gateway-microservice/` — one bounded context (the API Gateway), with:
    - `routers/`  — FastAPI route handlers.
    - `services/` — business logic.
    - `models/`   — SQLAlchemy ORM models.
    - `schemas/`  — Pydantic request/response schemas.
    - `main.py`   — FastAPI app factory + Uvicorn entry.
- R2: The gateway MUST call the master_orchestrator MCP agent's `orchestrate` tool
  and return the merged answer to the frontend. Transport: MCP over HTTP (the gateway
  is an MCP *client* of the orchestrator's HTTP/SSE MCP server; URL from env/config).
- R3: Expose a chat REST endpoint the frontend calls when a user sends a message; the
  endpoint accepts a prompt and returns the orchestrator's answer.
- R4: Every REST response uses this exact envelope shape (T = endpoint payload type):
  `{ status: "Success" | "Failed", data?: T, error_text?: string }`.
  (Spec wrote "Faild"; corrected to "Failed" per Engineer decision — recorded here so
  frontend and backend agree on the wire literal.)
- R5: The frontend contract stays compatible with the existing
  `SendMessageRequest { prompt }` -> `SendMessageResponse { reply }` shape so
  `frontend/services/chatService.ts` can adopt the real gateway without changing its
  caller signature. (Frontend wiring itself is a SEPARATE task — out of scope here.)
- R6: Follow the harness and subsystem rules. Backend gets its own `backend/CLAUDE.md`
  (root CLAUDE.md references one) consistent with the mcp/ conventions:
  contracts-first, thin routers, config not constants, fail-soft, mock-swappable.

## Acceptance
- A1: Folder Map from R1 exists exactly under `backend/`; each package importable.
- A2: `backend/_common/schemas/` defines a generic `ApiResponse[T]` envelope with
  `status` (Success|Failed), optional `data`, optional `error_text`, plus `ok()` /
  `fail()` constructors. Every router response is this envelope.
- A3: A `POST` chat endpoint accepts `{ "prompt": str }` and returns
  `ApiResponse[ChatReply]` where `ChatReply` carries `reply: str` (the orchestrator's
  merged `answer`). On orchestrator/client error the endpoint returns
  `status="Failed"` + `error_text`, HTTP 200 (fail-soft envelope), never a raw 500.
- A4: An orchestrator client service reaches the orchestrator via an MCP HTTP client,
  calls the `orchestrate` tool with `{prompt, context}`, and maps its
  `AgentResponse[OrchestrationResult]` -> `ChatReply`. The client is behind an
  interface with a mock implementation selected by config, so the gateway runs and is
  testable with zero external processes (mock by default).
- A5: `main.py` is an app factory (`create_app()`) returning a configured `FastAPI`
  app (CORS for the frontend origin, router mounted) + a Uvicorn `main()` entry.
- A6: Settings come from `backend/_common/env/` (pydantic-settings, env-backed):
  orchestrator MCP URL, orchestrator client mode (mock|http), CORS origins, DB URL.
  No hardcoded secrets.
- A7: The app imports and a request to the chat endpoint returns a valid
  `status="Success"` envelope with a non-empty `reply` in mock mode (Validator runs it).
- A8: `backend/CLAUDE.md` documents the subsystem layer boundaries and defers to the
  harness and root CLAUDE.md (precedence stated).

## Constraints
- Latest stable versions of FastAPI, Pydantic v2, pydantic-settings, SQLAlchemy 2.x,
  fastmcp (MCP client), uvicorn. Pin them in `backend/pyproject.toml` (or requirements).
- Async-first; fully type-hinted. Routers thin — business logic in `services/`.
- Contracts first: define `schemas/` before routers. Never pass raw dicts across
  boundaries; tools/services accept and return Pydantic models.
- Fail soft: no exception crosses the HTTP boundary as an unstructured 500; wrap in the
  envelope. DB is scaffolded (session factory + base + one ORM model for message log)
  but the chat path must not require a live DB to answer in mock mode.
- Do NOT modify `mcp/` or `frontend/` in this task. Integration with the orchestrator
  is via its existing HTTP MCP server + `orchestrate` tool contract only.
- Precedence on conflict: `.claude/` harness > root CLAUDE.md > `backend/CLAUDE.md`.
