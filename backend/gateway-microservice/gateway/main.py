"""FastAPI app factory + Uvicorn entry for the gateway-microservice."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from _common.env import get_settings
from gateway.routers import chat_router


def create_app() -> FastAPI:
    """Build and configure the gateway FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title="agent-chat API Gateway",
        version="0.1.0",
        summary="REST boundary between the frontend chat and the MCP orchestrator.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat_router)
    return app


app = create_app()


def main() -> None:
    """Uvicorn entry point (console script / ``python -m gateway.main``)."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
