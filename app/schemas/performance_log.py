from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PerformanceLogBase(BaseModel):
    job_id: str
    step_name: str
    execution_time_seconds: float
    peak_memory_mb: Optional[float] = None
    cpu_utilization_percent: Optional[float] = None

class PerformanceLogCreate(PerformanceLogBase):
    pass

class PerformanceLogResponse(PerformanceLogBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True
