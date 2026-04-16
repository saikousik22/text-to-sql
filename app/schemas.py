from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# ─── Query Endpoint ──────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Request body for the /api/query endpoint."""
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question about the database",
        json_schema_extra={"examples": ["How many employees are in Engineering?"]}
    )


class QueryResponse(BaseModel):
    """Response body for the /api/query endpoint."""
    question: str
    generated_sql: str
    results: list[dict[str, Any]]
    row_count: int
    success: bool
    error: Optional[str] = None


# ─── Tables Endpoint ─────────────────────────────────────────────

class ColumnInfo(BaseModel):
    """Schema information for a single column."""
    name: str
    type: str
    nullable: bool
    primary_key: bool


class TableInfo(BaseModel):
    """Schema information for a single table."""
    name: str
    columns: list[ColumnInfo]
    row_count: int


class TablesResponse(BaseModel):
    """Response body for the /api/tables endpoint."""
    tables: list[TableInfo]
    total_tables: int


# ─── Seed Endpoint ───────────────────────────────────────────────

class SeedResponse(BaseModel):
    """Response body for the /api/seed endpoint."""
    message: str
    tables_created: list[str]
    records_inserted: dict[str, int]


# ─── History Endpoint ────────────────────────────────────────────

class HistoryItem(BaseModel):
    """A single query history entry."""
    id: int
    question: str
    generated_sql: str
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    """Response body for the /api/history endpoint."""
    history: list[HistoryItem]
    total: int
