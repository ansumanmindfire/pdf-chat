"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import logger, settings
from app.exceptions import (
    BaseAppException,
    app_exception_handler,
    global_exception_handler,
    http_exception_handler,
    request_validation_handler,
)

from app.database import engine
from app.models.models import Base
from app.routers import document_router, chat_router

Base.metadata.create_all(bind=engine)

logger.info("Initializing FastAPI application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, request_validation_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Register API Routers
app.include_router(document_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])


@app.get("/")
def home():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
