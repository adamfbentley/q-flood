from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PerformanceLog(Base):
    __tablename__ = "performance_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    step_name = Column(String, nullable=False) # e.g., 'classical_solve', 'quantum_solve'
    execution_time_seconds = Column(Float, nullable=False)
    peak_memory_mb = Column(Float, nullable=True)
    cpu_utilization_percent = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="performance_logs")

    def __repr__(self):
        return f"<PerformanceLog(id='{self.id}', job_id='{self.job_id}', step='{self.step_name}', time={self.execution_time_seconds:.2f}s)>"
