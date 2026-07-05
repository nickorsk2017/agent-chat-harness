# PLAN — 2026-07-04-backend-gateway

plan_version: 1

## Architecture (one gateway bounded context, MCP-client boundary)
Frontend --HTTP/JSON--> gateway-microservice --MCP(HTTP client)--> master_orchestrator.orchestrate --> merged answer.
The gateway owns the REST + envelope surface (R3,R4); the orchestrator owns domain
fan-out. Gateway never does domain work — it validates, delegates to a service, maps the
orchestrator envelope into the REST envelope. Mirrors mcp/ layering (thin tools, contracts
first, config not constants, fail-soft, mock by default).

## Module / file map (targets)
Shared — `backend/_common/` (satisfies R1 shared block, A2, A6):
- P1 `_common/schemas/response.py`  -> generic `ApiResponse[T]` envelope: status
      Success|Failed, optional data, optional error_text, `ok()`/`fail()` (R4,A2).
- P2 `_common/env/settings.py`      -> pydantic-settings BaseSettings: orchestrator MCP
      url, client mode (mock|http), CORS origins, DB url, timeout (R2,A6). No secrets.
- P3 `_common/db/base.py`,`session.py` -> SQLAlchemy 2.x DeclarativeBase + async session
      factory (A_scaffold). Not required on the mock chat path (constraint: no live DB).
Gateway — `backend/gateway-microservice/` (R1 microservice block):
- P4 `schemas/chat.py`   -> `ChatRequest{prompt}`, `ChatReply{reply, subtasks?}` (A3,R5).
- P5 `models/message.py` -> ORM `MessageLog` (id, role, content, created_at) (R1 models).
- P6 `services/orchestrator_client.py` -> `OrchestratorClient` Protocol +
      `HttpMcpOrchestratorClient` (fastmcp Client on settings.url, calls tool
      `orchestrate` with `{"request": {prompt, context}}`, parses structured_content to
      OrchestrationResult.answer) + `MockOrchestratorClient`. Factory picks by mode (R2,A4).
- P7 `services/chat_service.py` -> `ChatService.reply(prompt)`: call client, map
      AgentResponse[OrchestrationResult] -> ChatReply; on non-ok/exception raise a typed
      GatewayError carrying a message (fail-soft handled at router) (A3,A4).
- P8 `routers/chat.py`   -> `POST /api/chat` thin handler: build ChatRequest, call
      ChatService, return `ApiResponse.ok(ChatReply)`; on GatewayError/Exception return
      `ApiResponse.fail(error_text=...)` HTTP 200 (A3,A4). Also `GET /api/health`.
- P9 `main.py`           -> `create_app()` app factory: CORS (settings origins), mount
      router, lifespan (dependency wiring). `main()` uvicorn entry (A5).
Packaging / docs:
- P10 `backend/pyproject.toml` (or requirements.txt) pin latest stable: fastapi 0.139.x,
      pydantic 2.x, pydantic-settings 2.x, sqlalchemy 2.x, fastmcp 2.x, uvicorn, httpx
      (constraint: latest versions).
- P11 `backend/CLAUDE.md` — layer boundaries + precedence note (A8,R6).
- P12 `__init__.py` in every package dir so all are importable (A1); `_common` and the
      microservice import roots resolve (note hyphen: dir `gateway-microservice`, so the
      importable package lives at `gateway-microservice/gateway/` OR the app is run by
      path — see risk RK-4, resolved in S).

## Dependency-injection & contracts
- FastAPI `Depends` provides `ChatService` (built from the config-selected client) so the
  handler stays thin and the client is swappable in tests (A4).
- All boundaries pass Pydantic models, never raw dicts (constraint).

## Sequencing
S1 P10 deps + P12 package init (scaffold importable tree, A1).
S2 Contracts first: P1 envelope, P4 chat schemas, P2 settings, P3 db (A2,A6).
S3 P6 orchestrator client (Protocol + Http + Mock + factory) — the R2/A4 core.
S4 P7 chat service maps orchestrator->ChatReply; P5 ORM model.
S5 P8 router (envelope + fail-soft) ; P9 app factory + CORS + uvicorn (A5).
S6 P11 backend/CLAUDE.md.
Order: contracts (S2) precede consumers (S3-S5) per "contracts first".

## Risks
- RK-1 fastmcp HTTP client API/tool-arg shape. Mitigation: reuse the proven repo pattern
  from master_orchestrator/tools/subagent_client.py — `Client(url)`,
  `call_tool("orchestrate", {"request": {...}})`, read `structured_content`/`data`.
- RK-2 Orchestrator offline in dev/test. Mitigation: mock client is DEFAULT mode (A4,A7)
  so gateway runs green with zero external processes; http mode is opt-in via env.
- RK-3 Exceptions leaking as 500. Mitigation: service raises typed GatewayError; router
  wraps all failures in `ApiResponse.fail` at HTTP 200 (A3, fail-soft constraint).
- RK-4 Hyphenated dir `gateway-microservice` isn't a valid Python module name. Mitigation:
  the folder is a project directory (matches mandated Folder Map literally) containing an
  importable package `gateway/`; app referenced as `gateway.main:create_app`. `_common`
  is importable directly. Validator runs from `backend/` on `sys.path`.
- RK-5 SQLAlchemy on the hot path. Mitigation: DB scaffolded but chat mock path never
  touches a session (constraint); MessageLog persistence is best-effort/optional.

## Out of scope (separate tasks)
Frontend wiring of chatService.ts (R5 keeps contract compatible but does not change FE),
real sub-agent behavior, auth, rate limiting, migrations/alembic, streaming responses.
