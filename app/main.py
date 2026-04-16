"""
Text-to-SQL API — Main Application Entry Point

A FastAPI service that converts natural language questions into SQL queries,
executes them against a SQLite database, and returns formatted results.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import query, tables, seed, history


# Ensure the data directory exists
data_dir = Path(__file__).resolve().parent.parent / "data"
data_dir.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: initialize database tables
    print("[*] Starting Text-to-SQL API...")
    init_db()
    print("[+] Database initialized")
    print(f"[i] API docs available at: http://localhost:8000/docs")
    yield
    # Shutdown
    print("[*] Shutting down Text-to-SQL API...")


# ─── Create FastAPI App ──────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routers ───────────────────────────────────────────

app.include_router(query.router)
app.include_router(tables.router)
app.include_router(seed.router)
app.include_router(history.router)


# ─── Root Endpoint ───────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """Health check and API info."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "endpoints": {
            "query": "POST /api/query — Ask a natural language question",
            "tables": "GET /api/tables — View database schema",
            "seed": "POST /api/seed — Seed sample data",
            "history": "GET /api/history — View query history",
            "docs": "GET /docs — Interactive API documentation",
        }
    }
