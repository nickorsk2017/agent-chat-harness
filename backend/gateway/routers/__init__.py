"""FastAPI route handlers for the gateway."""

from gateway.routers.chat import router as chat_router

__all__ = ["chat_router"]
