"""Exceptions package providing custom exception classes and global FastAPI handlers."""

from app.exceptions.custom_exceptions import (
    BaseAppException,
    DocumentNotFoundException,
    SessionNotFoundException,
    InvalidFileException,
    PDFProcessingException,
    RAGGenerationException,
)
from app.exceptions.handlers import (
    app_exception_handler,
    global_exception_handler,
    http_exception_handler,
    request_validation_handler,
)

__all__ = [
    "BaseAppException",
    "DocumentNotFoundException",
    "SessionNotFoundException",
    "InvalidFileException",
    "PDFProcessingException",
    "RAGGenerationException",
    "app_exception_handler",
    "global_exception_handler",
    "http_exception_handler",
    "request_validation_handler",
]
