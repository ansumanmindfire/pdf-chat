"""Routers package containing API endpoints for documents and chat."""

from app.routers.document_router import router as document_router
from app.routers.chat_router import router as chat_router

__all__ = ["document_router", "chat_router"]
