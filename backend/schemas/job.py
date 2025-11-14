from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.models.job import JobStatus, SolverType # Import enums from the model
from backend.schemas.performance_log import PerformanceLogResponse # New: Import PerformanceLogResponse

# Re-export enums for schema usage
JobStatusEnum = JobStatus
SolverTypeEnum = SolverType

class JobBase(BaseModel):
    solver_type: SolverTypeEnum
    parameters: Optional[Dict[str, Any]] = None
    input_data_path: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    status: JobStatusEnum
    preprocessed_data_path: Optional[str] = None # New
    matrix_path: Optional[str] = None
    vector_path: Optional[str] = None
    solution_path: Optional[str] = None
    geojson_path: Optional[str] = None
    pdf_report_path: Optional[str] = None
    fallback_reason: Optional[str] = None
    latest_performance_metrics: Optional[Dict[str, Any]] = None # New
    performance_logs: List[PerformanceLogResponse] = [] # New: For detailed logs
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
