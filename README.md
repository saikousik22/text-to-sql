# 🗃️ Text-to-SQL API

> Convert natural language questions into SQL queries using FastAPI + SQLite + Google Gemini.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get a free Gemini API key at: https://aistudio.google.com/apikey

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

### 4. Seed the database

```bash
curl -X POST http://localhost:8000/api/seed
```

### 5. Ask a question!

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me the top 5 highest paid employees"}'
```

## API Endpoints

| Method | Endpoint        | Description                                  |
|--------|-----------------|----------------------------------------------|
| GET    | `/`             | Health check & API info                      |
| POST   | `/api/query`    | Natural language → SQL → results             |
| GET    | `/api/tables`   | List all tables with schema info             |
| POST   | `/api/seed`     | Seed database with sample data               |
| GET    | `/api/history`  | View past queries and their generated SQL    |
| GET    | `/docs`         | Interactive Swagger documentation            |
| GET    | `/redoc`        | ReDoc documentation                          |

## Tech Stack

- **FastAPI** — async Python web framework
- **SQLite** — lightweight file-based database
- **SQLAlchemy** — ORM & schema introspection
- **Google Gemini** — LLM for NL → SQL conversion
- **Pydantic** — request/response validation
