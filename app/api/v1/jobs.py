import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.dependencies import get_api_key
from app.models.api_key import APIKey
from app.models.job import Job, JobStatus, SolverType
from app.schemas.job import JobCreate, JobResponse, JobStatusEnum
import uuid
from app.tasks.geospatial_tasks import validate_and_preprocess_task # New: Import geospatial task
from app.tasks.quantum_tasks import quantum_solve_task
from app.core.object_storage import MinioClient
import os

router = APIRouter(tags=["Job Management"])
logger = logging.getLogger(__name__)

@router.post("/solve", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    job_create: JobCreate,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(get_api_key)
):
    """Submits a new flood simulation job and returns its ID."""
    job_id = str(uuid.uuid4())
    db_job = Job(
        id=job_id,
        status=JobStatus.PENDING,
        solver_type=job_create.solver_type,
        parameters=job_create.parameters,
        input_data_path=job_create.input_data_path
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Dispatch the initial geospatial validation and pre-processing task
    # This task will then chain to matrix generation and solver tasks.
    validate_and_preprocess_task.delay(job_id, job_create.input_data_path, job_create.parameters, job_create.solver_type)

    return db_job

@router.get("/jobs", response_model=List[JobResponse])
async def get_all_jobs(
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(get_api_key),
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return (page size)")
):
    """Retrieves a list of all flood simulation jobs with pagination."""
    # Eager load performance logs for JobResponse schema
    jobs = db.query(Job).options(relationship(Job.performance_logs)).offset(skip).limit(limit).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_details(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(get_api_key)
):
    """Retrieves detailed status and information for a specific job."""
    # Eager load performance logs for JobResponse schema
    job = db.query(Job).options(relationship(Job.performance_logs)).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job

@router.get("/results/{job_id}/{file_type}")
async def get_job_results(
    job_id: str,
    file_type: str,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(get_api_key)
):
    """Downloads the processed GIS results (GeoJSON or PDF) for a completed job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status not in [JobStatus.COMPLETED, JobStatus.FALLBACK_CLASSICAL_COMPLETED]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Job {job_id} is not yet completed. Current status: {job.status}")

    minio_client = MinioClient()
    object_path = None
    media_type = None
    filename = None

    if file_type.lower() == "geojson":
        object_path = job.geojson_path
        media_type = "application/geo+json"
        filename = f"flood_data_{job_id}.geojson"
    elif file_type.lower() == "pdf":
        object_path = job.pdf_report_path
        media_type = "application/pdf"
        filename = f"flood_report_{job_id}.pdf"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file_type. Must be 'geojson' or 'pdf'.")

    if not object_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {file_type} results found for job {job_id}.")

    try:
        # Download the file content from MinIO
        file_content = minio_client.download_file(object_path)

        # Return as a streaming response
        return Response(content=file_content, media_type=media_type, headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    except Exception as e:
        logger.error(f"[{job_id}] Failed to download {file_type} from object storage: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve {file_type} results: {e}")
