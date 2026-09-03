# PDF-Chat

Retrieval-Augmented Generation (RAG) backend REST API using **FastAPI**, **LangChain**, **FAISS**, **SQLite**, and **Google Gemini**.

---

## Quick Start

### 1. Install Dependencies
```powershell
poetry install
```

### 2. Configure Environment
Create a `.env` file from `.env.example`:
```env
GOOGLE_API_KEY="your_google_gemini_api_key_here"
ENVIRONMENT="DEVELOPMENT"
LOG_DIR="logs"
```

### 3. Run Development Server
```powershell
poetry run uvicorn app.main:app --reload
```
- **Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## REST API Endpoints (2 Core Endpoints)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/v1/upload` | Upload PDF, parse chunks, index FAISS, and auto-initialize `session_id` |
| **POST** | `/api/v1/chat/` | Ask question with `session_id`, retrieve context & history, return AI answer + page citations |

---

## Architecture Overview

```text
app/
├── main.py              # FastAPI Application Entry Point
├── config/              # Environment Settings & Logging Setup
├── constants/           # System Constants
├── database/            # SQLAlchemy Engine & SessionLocal
├── exceptions/          # Custom Exceptions & Global Exception Handlers
├── models/              # Database Models
├── repositories/        # Database CRUD Layer
├── routers/             # REST Endpoints (Document Upload & Chat)
├── schemas/             # Pydantic Request/Response Validation Schemas
└── services/            # Core Services (PDF Parsing, FAISS, RAG Chain)
```
