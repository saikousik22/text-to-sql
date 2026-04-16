from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    budget = Column(Float, nullable=False)
    location = Column(String(100), nullable=True)

    # Relationships
    employees = relationship("Employee", back_populates="department_rel")
    projects = relationship("Project", back_populates="department_rel")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    department = Column(String(50), ForeignKey("departments.name"), nullable=False)
    salary = Column(Float, nullable=False)
    hire_date = Column(Date, nullable=False)
    position = Column(String(100), nullable=True)

    # Relationships
    department_rel = relationship("Department", back_populates="employees")

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}')>"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    status = Column(String(20), nullable=False)  # Active, Completed, On Hold
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    budget = Column(Float, nullable=True)

    # Relationships
    department_rel = relationship("Department", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=False)
    success = Column(Integer, default=1)  # 1 = True, 0 = False
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QueryHistory(id={self.id}, question='{self.question[:30]}...')>"
