#!/bin/bash
#SBATCH --job-name=flood_forecast
#SBATCH --output=flood_forecast_%j.out
#SBATCH --error=flood_forecast_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8GB
#SBATCH --time=01:00:00

# This is an example SLURM job script for running the Quantum Flood Forecasting Framework backend.
# It assumes: 
# 1. Python 3.11+ is available (e.g., via module load).
# 2. Redis and PostgreSQL services are already running and accessible from the compute node.
#    (e.g., on a head node, or separate services with accessible network endpoints).
# 3. MinIO object storage is running and accessible.
# 4. The application code is available on the compute node (e.g., mounted via NFS or copied).

# Load necessary modules (adjust as per your HPC environment)
# module load python/3.11.5
# module load cuda/11.8 # If quantum solver uses GPU-accelerated simulators

# Set environment variables for the application
# HPC-SEC-001: IMPORTANT: DO NOT HARDCODE SENSITIVE INFORMATION IN PRODUCTION SCRIPTS.
# Use secure secret management solutions (e.g., HashiCorp Vault, SLURM --export, or environment-specific config files).
# The following are placeholders. You MUST replace them with secure methods.
export DATABASE_URL="${SLURM_DATABASE_URL:-postgresql+psycopg2://user:password@db_host:5432/flood_db}"
export MINIO_ENDPOINT="${SLURM_MINIO_ENDPOINT:-minio_host:9000}"
export MINIO_ACCESS_KEY="${SLURM_MINIO_ACCESS_KEY:-minioadmin}"
export MINIO_SECRET_KEY="${SLURM_MINIO_SECRET_KEY:-minioadmin}"
export MINIO_BUCKET_NAME="${SLURM_MINIO_BUCKET_NAME:-flood-data}"
export MINIO_SECURE="${SLURM_MINIO_SECURE:-True}" # Set to True for production with TLS
export API_KEY_HASH_SALT="${SLURM_API_KEY_HASH_SALT:-your_super_secret_api_key_for_hashing}"
export REDIS_URL="${SLURM_REDIS_URL:-redis://redis_host:6379/0}"

# HPC-CQ-001: Define the application directory.
# You MUST replace this with the actual path where your application code resides on the HPC system.
# This could be a shared NFS mount, or a path where the code was copied.
APP_DIR="/path/to/your/quantum-flood-forecasting-framework/app" # IMPORTANT: Update this path!
cd "$APP_DIR"

# Activate virtual environment if used
# source /path/to/your/venv/bin/activate

echo "Starting FastAPI backend with Gunicorn..."
# HPC-CQ-002: Using Gunicorn for production readiness.
# Adjust --workers based on available CPUs/resources and application needs.
# For example, (2 * CPU_CORES) + 1 is a common recommendation.
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 > ../backend_gunicorn.log 2>&1 &
BACKEND_PID=$!
echo "FastAPI backend started with PID $BACKEND_PID"

echo "Starting Celery worker..."
# Run Celery worker in the background
# Adjust concurrency based on available CPUs/resources
celery -A app.core.celery_app worker --loglevel=info --concurrency=2 > ../celery_worker.log 2>&1 &
CELERY_PID=$!
echo "Celery worker started with PID $CELERY_PID"

# Keep the job alive until processes are terminated
wait $BACKEND_PID $CELERY_PID

echo "Flood forecasting job finished."
