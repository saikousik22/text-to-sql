"""
SQL Service — Executes validated SQL queries against the SQLite database
and formats results as dictionaries.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine
from app.config import settings


class SQLService:
    """Executes SQL queries safely and returns formatted results."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def execute_query(self, sql: str) -> list[dict]:
        """
        Execute a SELECT query and return results as a list of dicts.
        
        Args:
            sql: A validated SQL SELECT query string.
            
        Returns:
            List of dictionaries, each representing a row.
            
        Raises:
            Exception: If the query fails to execute.
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))

            # Get column names from the result
            columns = list(result.keys())

            # Convert rows to list of dicts
            rows = []
            for row in result.fetchmany(settings.MAX_QUERY_RESULTS):
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert non-serializable types to strings
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        value = str(value)
                    row_dict[col] = value
                rows.append(row_dict)

            return rows

    def execute_raw(self, sql: str) -> None:
        """
        Execute a raw SQL statement (for seeding/setup only).
        Not exposed via API.
        """
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
