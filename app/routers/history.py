"""
History Router — GET /api/history
Returns the recent query history.
"""

from fastapi import APIRouter, Query
from sqlalchemy import desc

from app.schemas import HistoryResponse, HistoryItem
from app.database import SessionLocal
from app.models import QueryHistory

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(default=20, ge=1, le=100, description="Number of history items to return"),
    success_only: bool = Query(default=False, description="Filter to only successful queries")
):
    """
    Get the recent query history, ordered by most recent first.
    """
    db = SessionLocal()

    try:
        query = db.query(QueryHistory).order_by(desc(QueryHistory.created_at))

        if success_only:
            query = query.filter(QueryHistory.success == 1)

        records = query.limit(limit).all()

        items = [
            HistoryItem(
                id=r.id,
                question=r.question,
                generated_sql=r.generated_sql,
                success=bool(r.success),
                error_message=r.error_message,
                created_at=r.created_at
            )
            for r in records
        ]

        return HistoryResponse(
            history=items,
            total=len(items)
        )

    finally:
        db.close()
