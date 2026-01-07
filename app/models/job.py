import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped
from typing import List
from app.core.database import Base
import uuid

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    VALIDATION_FAILED = "VALIDATION_FAILED" # New status for validation failure
    PREPROCESSING_FAILED = "PREPROCESSING_FAILED" # New status for preprocessing failure
    QUANTUM_FAILED_FALLBACK_INITIATED = "QUANTUM_FAILED_FALLBACK_INITIATED" # New status for fallback
    FALLBACK_CLASSICAL_RUNNING = "FALLBACK_CLASSICAL_RUNNING" # New status for fallback
    FALLBACK_CLASSICAL_COMPLETED = "FALLBACK_CLASSICAL_COMPLETED" # New status for fallback
    FALLBACK_CLASSICAL_FAILED = "FALLBACK_CLASSICAL_FAILED" # New status for fallback

class SolverType(str, enum.Enum):
    CLASSICAL = "CLASSICAL"
    QUANTUM = "QUANTUM"
    HYBRID = "HYBRID" # New solver type

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    solver_type = Column(Enum(SolverType), nullable=False)
    parameters = Column(JSON, nullable=True) # Input parameters for the solver
    input_data_path = Column(String, nullable=True) # Path to raw input data in object storage
    preprocessed_data_path = Column(String, nullable=True) # New: Path to pre-processed data in object storage
    matrix_path = Column(String, nullable=True) # Path to generated sparse matrix A in object storage
    vector_path = Column(String, nullable=True) # Path to generated vector b in object storage
    solution_path = Column(String, nullable=True) # Path to raw solver output (solution vector x) in object storage
    geojson_path = Column(String, nullable=True) # New: Path to processed GeoJSON output
    pdf_report_path = Column(String, nullable=True) # New: Path to generated PDF report
    fallback_reason = Column(String, nullable=True) # New: Reason for fallback if applicable
    latest_performance_metrics = Column(JSON, nullable=True) # New: Summary of latest performance metrics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    performance_logs: Mapped[List["PerformanceLog"]] = relationship("PerformanceLog", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job(id='{self.id}', status='{self.status}', solver_type='{self.solver_type}')>"
