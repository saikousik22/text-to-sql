"""
Tables Router — GET /api/tables
Returns schema information for all tables in the database.
"""

from fastapi import APIRouter
from app.schemas import TablesResponse
from app.services.schema_service import SchemaService
from app.database import engine

router = APIRouter(prefix="/api", tags=["Tables"])

schema_service = SchemaService(engine)


@router.get("/tables", response_model=TablesResponse)
async def list_tables():
    """
    List all tables in the database with their column details and row counts.
    Useful for understanding the database structure before asking questions.
    """
    tables = schema_service.get_all_tables()

    return TablesResponse(
        tables=tables,
        total_tables=len(tables)
    )
