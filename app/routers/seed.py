"""
Seed Router — POST /api/seed
Populates the database with sample data for testing.
"""

from datetime import date
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.schemas import SeedResponse
from app.database import engine, SessionLocal, init_db
from app.models import Department, Employee, Project, Base

router = APIRouter(prefix="/api", tags=["Seed"])


# ─── Sample Data ──────────────────────────────────────────────────

DEPARTMENTS = [
    {"name": "Engineering", "budget": 500000.00, "location": "Building A - Floor 3"},
    {"name": "Marketing", "budget": 300000.00, "location": "Building B - Floor 1"},
    {"name": "HR", "budget": 200000.00, "location": "Building A - Floor 1"},
    {"name": "Sales", "budget": 400000.00, "location": "Building C - Floor 2"},
    {"name": "Finance", "budget": 350000.00, "location": "Building A - Floor 2"},
    {"name": "Operations", "budget": 250000.00, "location": "Building D - Floor 1"},
]

EMPLOYEES = [
    {"name": "Alice Johnson", "email": "alice@company.com", "department": "Engineering", "salary": 95000, "hire_date": date(2021, 3, 15), "position": "Senior Developer"},
    {"name": "Bob Smith", "email": "bob@company.com", "department": "Marketing", "salary": 72000, "hire_date": date(2020, 7, 22), "position": "Marketing Manager"},
    {"name": "Carol Williams", "email": "carol@company.com", "department": "Engineering", "salary": 88000, "hire_date": date(2022, 1, 10), "position": "Backend Developer"},
    {"name": "David Brown", "email": "david@company.com", "department": "HR", "salary": 65000, "hire_date": date(2019, 11, 5), "position": "HR Specialist"},
    {"name": "Eva Martinez", "email": "eva@company.com", "department": "Sales", "salary": 78000, "hire_date": date(2021, 6, 18), "position": "Sales Lead"},
    {"name": "Frank Lee", "email": "frank@company.com", "department": "Engineering", "salary": 110000, "hire_date": date(2018, 2, 28), "position": "Tech Lead"},
    {"name": "Grace Kim", "email": "grace@company.com", "department": "Finance", "salary": 82000, "hire_date": date(2020, 9, 12), "position": "Financial Analyst"},
    {"name": "Henry Wilson", "email": "henry@company.com", "department": "Engineering", "salary": 92000, "hire_date": date(2022, 4, 3), "position": "Frontend Developer"},
    {"name": "Iris Chen", "email": "iris@company.com", "department": "Marketing", "salary": 68000, "hire_date": date(2023, 1, 20), "position": "Content Strategist"},
    {"name": "Jack Davis", "email": "jack@company.com", "department": "Sales", "salary": 85000, "hire_date": date(2019, 8, 14), "position": "Senior Sales Rep"},
    {"name": "Karen Taylor", "email": "karen@company.com", "department": "Operations", "salary": 70000, "hire_date": date(2021, 12, 1), "position": "Operations Coordinator"},
    {"name": "Liam Anderson", "email": "liam@company.com", "department": "Engineering", "salary": 105000, "hire_date": date(2020, 5, 25), "position": "DevOps Engineer"},
    {"name": "Mia Thomas", "email": "mia@company.com", "department": "HR", "salary": 75000, "hire_date": date(2022, 7, 8), "position": "Recruiter"},
    {"name": "Nathan White", "email": "nathan@company.com", "department": "Finance", "salary": 90000, "hire_date": date(2019, 3, 30), "position": "Senior Accountant"},
    {"name": "Olivia Harris", "email": "olivia@company.com", "department": "Marketing", "salary": 76000, "hire_date": date(2023, 5, 15), "position": "Social Media Manager"},
]

PROJECTS = [
    {"name": "Project Alpha", "department_id": 1, "status": "Active", "start_date": date(2024, 1, 1), "end_date": None, "budget": 120000},
    {"name": "Project Beta", "department_id": 2, "status": "Completed", "start_date": date(2023, 6, 15), "end_date": date(2024, 2, 28), "budget": 85000},
    {"name": "Project Gamma", "department_id": 1, "status": "Active", "start_date": date(2024, 3, 1), "end_date": None, "budget": 200000},
    {"name": "Project Delta", "department_id": 4, "status": "On Hold", "start_date": date(2023, 9, 1), "end_date": None, "budget": 95000},
    {"name": "Project Epsilon", "department_id": 5, "status": "Active", "start_date": date(2024, 2, 15), "end_date": None, "budget": 150000},
    {"name": "Project Zeta", "department_id": 3, "status": "Completed", "start_date": date(2023, 1, 10), "end_date": date(2023, 12, 20), "budget": 60000},
    {"name": "Project Eta", "department_id": 1, "status": "Active", "start_date": date(2024, 5, 1), "end_date": None, "budget": 180000},
    {"name": "Project Theta", "department_id": 6, "status": "Active", "start_date": date(2024, 4, 1), "end_date": None, "budget": 75000},
]


@router.post("/seed", response_model=SeedResponse)
async def seed_database():
    """
    Seed the database with sample employees, departments, and projects.
    WARNING: This will drop and recreate all tables!
    """
    try:
        # Drop all existing tables and recreate
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        db: Session = SessionLocal()

        # Insert departments
        for dept_data in DEPARTMENTS:
            db.add(Department(**dept_data))
        db.commit()

        # Insert employees
        for emp_data in EMPLOYEES:
            db.add(Employee(**emp_data))
        db.commit()

        # Insert projects
        for proj_data in PROJECTS:
            db.add(Project(**proj_data))
        db.commit()

        db.close()

        return SeedResponse(
            message="Database seeded successfully!",
            tables_created=["departments", "employees", "projects", "query_history"],
            records_inserted={
                "departments": len(DEPARTMENTS),
                "employees": len(EMPLOYEES),
                "projects": len(PROJECTS)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")
