# EXEC — 2026-07-04-backend-gateway

exec_version: 1

## Summary
Built the `backend/` subsystem per PLAN S1–S6. Mandated Folder Map created; the
hyphenated microservice dir holds an importable `gateway/` package (RK-4). REST chat
endpoint calls the master_orchestrator `orchestrate` MCP tool via an HTTP MCP client
(mock-by-default, http opt-in) and returns the shared `ApiResponse` envelope. All
modules compile; core logic verified with dependency-free tests (PyPI blocked in sandbox,
so no live TestClient — see Notes).

## Changed files (created)
_common (P1–P3, S2):
- _common/__init__.py
- _common/schemas/{__init__.py, response.py}   -> ApiResponse[T] {status:Success|Failed, data?, error_text?}, ok()/fail() (A2,R4)
- _common/env/{__init__.py, settings.py}        -> pydantic-settings: orchestrator url/mode/tool/timeout, CORS, DB url (A6)
- _common/db/{__init__.py, base.py, session.py}  -> SQLAlchemy 2.x DeclarativeBase + async session factory (scaffold)
gateway (P4–P9, S3–S5):
- gateway-microservice/gateway/__init__.py
- gateway-microservice/gateway/schemas/{__init__.py, chat.py}   -> ChatRequest{prompt,context}, ChatReply{reply,subtasks} (A3,R5)
- gateway-microservice/gateway/models/{__init__.py, message.py}  -> MessageLog ORM (P5)
- gateway-microservice/gateway/services/orchestrator_client.py   -> OrchestratorClient Protocol + HttpMcpOrchestratorClient + MockOrchestratorClient + factory (R2,A4)
- gateway-microservice/gateway/services/chat_service.py          -> ChatService.reply -> ChatReply; GatewayError (A3)
- gateway-microservice/gateway/services/__init__.py
- gateway-microservice/gateway/routers/{__init__.py, chat.py}    -> POST /api/chat + GET /api/health, envelope + fail-soft (A3)
- gateway-microservice/gateway/main.py                           -> create_app() factory + CORS + uvicorn main() (A5)
packaging/docs (P10,P11,S1,S6):
- backend/pyproject.toml   -> fastapi>=0.139.0, pydantic>=2, pydantic-settings>=2, sqlalchemy>=2, fastmcp>=2, uvicorn, httpx (latest)
- backend/.env.example
- backend/CLAUDE.md        -> layer boundaries + precedence (A8,R6)

## Integration decisions (from Engineer clarification)
- Orchestrator transport = MCP over HTTP (`Client(url)`, tool `orchestrate`, arg
  `{"request":{prompt,context}}`, read structured_content) — mirrors the proven
  mcp/master_orchestrator/tools/subagent_client.py pattern (RK-1).
- Envelope status literal corrected `Faild`->`Failed` (TASK R4).
- Scope: gateway only; frontend wiring is a separate task (R5 keeps FE contract stable).

## Verification (dependency-free; PyPI blocked in sandbox)
- `py_compile` on all 18 modules: PASS.
- Logic test (stubbed pydantic): envelope success/error/empty/malformed/string mapping,
  mock client non-empty answer, factory mock|http selection — 8/8 PASS.
- Source-contract test: Success|Failed literals, {status,data?,error_text?} fields,
  POST /api/chat + fail-soft catch-all, create_app()+CORS+uvicorn — PASS.

## Notes
- No live server run: fastapi/pydantic are not installed and PyPI is 403 in this sandbox.
  Left for Validator/user to run `pip install -e backend[dev]` + uvicorn where PyPI is
  reachable. Logic paths that don't need third-party deps are proven above.
- DB scaffolded but off the mock chat path (constraint honored).
