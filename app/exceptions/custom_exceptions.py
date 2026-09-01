"""Custom domain exception classes for PDF Chat Application."""

from typing import Optional, Any


class BaseAppException(Exception):
    """Base domain exception for the application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details


class DocumentNotFoundException(BaseAppException):
    """Raised when a requested document ID does not exist in the database."""

    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document with ID '{document_id}' was not found.",
            status_code=404,
            error_code="DOCUMENT_NOT_FOUND",
        )


class SessionNotFoundException(BaseAppException):
    """Raised when a requested chat session ID does not exist in the database."""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Chat session with ID '{session_id}' was not found.",
            status_code=404,
            error_code="SESSION_NOT_FOUND",
        )


class InvalidFileException(BaseAppException):
    """Raised when an uploaded file fails validation (e.g. non-PDF format or empty)."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid file upload: {reason}",
            status_code=400,
            error_code="INVALID_FILE_UPLOAD",
        )


class PDFProcessingException(BaseAppException):
    """Raised when parsing or text chunking of a PDF fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Failed to process PDF document: {detail}",
            status_code=422,
            error_code="PDF_PROCESSING_ERROR",
        )


class RAGGenerationException(BaseAppException):
    """Raised when the LLM answer generation chain fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"RAG answer generation failed: {detail}",
            status_code=500,
            error_code="RAG_GENERATION_ERROR",
        )
