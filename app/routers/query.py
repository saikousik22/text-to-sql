"""
Query Router — POST /api/query
Accepts a natural language question, generates SQL via Gemini, executes it, and returns results.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas import QueryRequest, QueryResponse
from app.services.llm_service import LLMService
from app.services.schema_service import SchemaService
from app.services.sql_service import SQLService
from app.database import engine, SessionLocal
from app.models import QueryHistory

router = APIRouter(prefix="/api", tags=["Query"])

# Initialize services
schema_service = SchemaService(engine)
sql_service = SQLService(engine)


@router.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Convert a natural language question into SQL, execute it, and return results.
    
    Steps:
    1. Extract the current database schema
    2. Send question + schema to Gemini LLM
    3. Validate the generated SQL (only SELECT allowed)
    4. Execute the SQL against SQLite
    5. Return formatted results
    """
    question = request.question
    generated_sql = ""
    
    try:
        # Step 1: Get current schema
        schema_str = schema_service.get_schema_string()
        
        if not schema_str:
            raise HTTPException(
                status_code=400,
                detail="No tables found in database. Please seed the database first via POST /api/seed"
            )

        # Step 2: Generate SQL via LLM
        llm_service = LLMService()
        generated_sql = llm_service.generate_sql(question, schema_str)

        # Step 3 & 4: Execute the query
        results = sql_service.execute_query(generated_sql)

        # Step 5: Save to history
        _save_history(question, generated_sql, success=True)

        return QueryResponse(
            question=question,
            generated_sql=generated_sql,
            results=results,
            row_count=len(results),
            success=True
        )

    except ValueError as e:
        # SQL validation failed (unsafe query)
        _save_history(question, generated_sql, success=False, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # LLM or execution error
        error_msg = f"Failed to process query: {str(e)}"
        _save_history(question, generated_sql, success=False, error=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


def _save_history(question: str, sql: str, success: bool, error: str = None):
    """Save query to history table."""
    try:
        db = SessionLocal()
        history = QueryHistory(
            question=question,
            generated_sql=sql or "N/A",
            success=1 if success else 0,
            error_message=error,
            created_at=datetime.utcnow()
        )
        db.add(history)
        db.commit()
        db.close()
    except Exception:
        pass  # Don't let history saving break the main flow
