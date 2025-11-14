import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    # Startup event: Initialize the database
    logger.info("Starting in development mode without full database dependencies...")
    yield
    logger.info("Application shutting down.")

app = FastAPI(
    title="Quantum Flood Forecasting Framework API",
    version="1.0.0",
    description="Backend API for managing flood simulation jobs, data ingestion, and results.",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint for basic API health check."""
    return {"message": "Welcome to the Quantum Flood Forecasting Framework API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Quantum Flood Forecasting Framework",
        "mode": "development"
    }

# Add a simple API info endpoint
@app.get("/api/v1/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Quantum Flood Forecasting Framework API",
        "version": "1.0.0",
        "description": "Hybrid quantum-classical flood forecasting application",
        "features": [
            "Geospatial data ingestion",
            "Matrix generation from flood models", 
            "Quantum HHL solver (Qiskit)",
            "Classical solver fallback",
            "GIS post-processing",
            "3D visualization support"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "note": "Full functionality requires PostgreSQL, Redis, and MinIO services"
    }
