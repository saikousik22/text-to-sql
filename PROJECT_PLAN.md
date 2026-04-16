# Text-to-SQL — Project Plan

> See the full plan in the artifacts. This file tracks build progress.

## ✅ Build Status

### Phase 1 — Foundation ✅
- [x] Project structure & dependencies (`requirements.txt`)
- [x] SQLite database setup with SQLAlchemy (`database.py`)
- [x] ORM models — Employee, Department, Project, QueryHistory (`models.py`)
- [x] Pydantic schemas for all endpoints (`schemas.py`)
- [x] Sample data seeding endpoint (`routers/seed.py`)

### Phase 2 — LLM Integration ✅
- [x] Gemini API service with prompt engineering (`services/llm_service.py`)
- [x] Schema introspection service (`services/schema_service.py`)
- [x] System prompt with safety rules (`prompts/system_prompt.txt`)
- [x] `/api/query` endpoint (`routers/query.py`)

### Phase 3 — Safety & Polish ✅
- [x] SQL validation — blocks DELETE, DROP, INSERT, UPDATE, ALTER
- [x] Error handling with proper HTTP status codes
- [x] Query history tracking (`routers/history.py`)
- [x] `/api/tables` endpoint (`routers/tables.py`)
- [x] CORS middleware
- [x] Root health check endpoint

### Phase 4 — Testing ✅
- [x] Test suite for all endpoints (`tests/test_api.py`)
- [x] SQL validation security tests
- [x] Edge case tests (empty questions, missing fields)
