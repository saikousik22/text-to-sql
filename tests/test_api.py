"""
Tests for the query endpoint and SQL validation.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base, SessionLocal
from app.routers.seed import DEPARTMENTS, EMPLOYEES, PROJECTS
from app.models import Department, Employee, Project


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Set up a fresh database for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed data
    db = SessionLocal()
    for dept_data in DEPARTMENTS:
        db.add(Department(**dept_data))
    db.commit()
    for emp_data in EMPLOYEES:
        db.add(Employee(**emp_data))
    db.commit()
    for proj_data in PROJECTS:
        db.add(Project(**proj_data))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


class TestSeedEndpoint:
    """Tests for POST /api/seed."""

    def test_seed_returns_success(self):
        response = client.post("/api/seed")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Database seeded successfully!"
        assert "employees" in data["tables_created"]
        assert data["records_inserted"]["employees"] == len(EMPLOYEES)

    def test_seed_is_idempotent(self):
        """Seeding twice should still work (drops and recreates)."""
        client.post("/api/seed")
        response = client.post("/api/seed")
        assert response.status_code == 200


class TestTablesEndpoint:
    """Tests for GET /api/tables."""

    def test_list_tables(self):
        response = client.get("/api/tables")
        assert response.status_code == 200
        data = response.json()
        assert data["total_tables"] >= 3
        table_names = [t["name"] for t in data["tables"]]
        assert "employees" in table_names
        assert "departments" in table_names
        assert "projects" in table_names

    def test_table_has_columns(self):
        response = client.get("/api/tables")
        data = response.json()
        emp_table = next(t for t in data["tables"] if t["name"] == "employees")
        col_names = [c["name"] for c in emp_table["columns"]]
        assert "name" in col_names
        assert "salary" in col_names
        assert "department" in col_names

    def test_table_has_row_count(self):
        response = client.get("/api/tables")
        data = response.json()
        emp_table = next(t for t in data["tables"] if t["name"] == "employees")
        assert emp_table["row_count"] == len(EMPLOYEES)


class TestHistoryEndpoint:
    """Tests for GET /api/history."""

    def test_empty_history(self):
        response = client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["history"] == []

    def test_history_limit_param(self):
        response = client.get("/api/history?limit=5")
        assert response.status_code == 200


class TestQueryValidation:
    """Tests for query request validation."""

    def test_empty_question_rejected(self):
        response = client.post("/api/query", json={"question": "ab"})
        assert response.status_code == 422  # Validation error (min 3 chars)

    def test_missing_question_rejected(self):
        response = client.post("/api/query", json={})
        assert response.status_code == 422


class TestRootEndpoint:
    """Tests for the root health check."""

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Text-to-SQL API"
        assert "endpoints" in data


class TestSQLValidation:
    """Tests for SQL safety validation in LLM service."""

    def test_blocks_delete(self):
        from app.services.llm_service import LLMService
        svc = LLMService.__new__(LLMService)  # Skip __init__
        with pytest.raises(ValueError, match="DELETE"):
            svc._validate_sql("DELETE FROM employees;")

    def test_blocks_drop(self):
        from app.services.llm_service import LLMService
        svc = LLMService.__new__(LLMService)
        with pytest.raises(ValueError, match="DROP"):
            svc._validate_sql("DROP TABLE employees;")

    def test_blocks_insert(self):
        from app.services.llm_service import LLMService
        svc = LLMService.__new__(LLMService)
        with pytest.raises(ValueError, match="INSERT"):
            svc._validate_sql("INSERT INTO employees VALUES (1, 'x');")

    def test_allows_select(self):
        from app.services.llm_service import LLMService
        svc = LLMService.__new__(LLMService)
        # Should not raise
        svc._validate_sql("SELECT * FROM employees;")

    def test_blocks_non_select(self):
        from app.services.llm_service import LLMService
        svc = LLMService.__new__(LLMService)
        with pytest.raises(ValueError):
            svc._validate_sql("PRAGMA table_info(employees);")
