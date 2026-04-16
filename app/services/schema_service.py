"""
Schema Service — Introspects the SQLite database to extract table/column metadata.
This schema is injected into the LLM prompt so it knows the exact structure.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from app.schemas import ColumnInfo, TableInfo


class SchemaService:
    """Extracts and formats database schema information."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def get_all_tables(self) -> list[TableInfo]:
        """Get schema info for all tables in the database."""
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()

        tables = []
        for table_name in table_names:
            # Skip internal tables
            if table_name.startswith("_") or table_name == "query_history":
                continue

            columns = self._get_columns(inspector, table_name)
            row_count = self._get_row_count(table_name)

            tables.append(TableInfo(
                name=table_name,
                columns=columns,
                row_count=row_count
            ))

        return tables

    def _get_columns(self, inspector, table_name: str) -> list[ColumnInfo]:
        """Get column details for a specific table."""
        columns_info = inspector.get_columns(table_name)
        pk_columns = inspector.get_pk_constraint(table_name)
        pk_names = pk_columns.get("constrained_columns", [])

        columns = []
        for col in columns_info:
            columns.append(ColumnInfo(
                name=col["name"],
                type=str(col["type"]),
                nullable=col.get("nullable", True),
                primary_key=col["name"] in pk_names
            ))

        return columns

    def _get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar() or 0
        except Exception:
            return 0

    def get_schema_string(self) -> str:
        """
        Generate a human-readable schema string for the LLM prompt.
        
        Example output:
            Table: employees
            Columns:
              - id (INTEGER, PRIMARY KEY)
              - name (VARCHAR(100), NOT NULL)
              - department (VARCHAR(50))
              - salary (FLOAT)
              - hire_date (DATE)
        """
        tables = self.get_all_tables()
        schema_parts = []

        for table in tables:
            lines = [f"Table: {table.name}"]
            lines.append(f"  Row count: {table.row_count}")
            lines.append("  Columns:")

            for col in table.columns:
                constraints = []
                if col.primary_key:
                    constraints.append("PRIMARY KEY")
                if not col.nullable:
                    constraints.append("NOT NULL")

                constraint_str = f", {', '.join(constraints)}" if constraints else ""
                lines.append(f"    - {col.name} ({col.type}{constraint_str})")

            schema_parts.append("\n".join(lines))

        return "\n\n".join(schema_parts)
