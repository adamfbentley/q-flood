import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.core.database import init_db
from backend.api.v1 import jobs, ingestion, admin
from backend.core.celery_app import celery_app # Import celery_app (required for Celery to discover tasks)

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    # Startup event: Initialize the database
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        logger.warning("Running in development mode without database connection")
    yield
    logger.info("Application shutting down.")

app = FastAPI(
    title="Quantum Flood Forecasting Framework API",
    version="1.0.0",
    description="Backend API for managing flood simulation jobs, data ingestion, and results.",
    lifespan=lifespan
)

# Include API routers
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint for basic API health check."""
    return {"message": "Welcome to the Quantum Flood Forecasting Framework API"}
