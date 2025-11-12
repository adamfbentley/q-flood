#!/bin/bash
#
# SBATCH --job-name=flood_celery_worker
# SBATCH --output=celery_worker_%j.out
# SBATCH --error=celery_worker_%j.err
# SBATCH --nodes=1
# SBATCH --ntasks-per-node=1
# SBATCH --cpus-per-task=4 # Adjust based on your Celery worker pool size
# SBATCH --mem=4GB
# SBATCH --time=04:00:00 # 4 hours runtime limit
# SBATCH --partition=compute # Specify your HPC partition

# Load necessary modules (e.g., Python, Miniconda)
# These lines are examples and must be adapted to your specific HPC environment.
# Uncomment and modify as needed.
# module load python/3.11.5
# module load miniconda/latest

# Activate your Python virtual environment if you're not using a container.
# Replace '/path/to/your/venv/bin/activate' with the actual path to your virtual environment.
# source /path/to/your/venv/bin/activate

# Set environment variables for the application.
# IMPORTANT: These sensitive variables MUST be replaced with actual, securely managed values.
# DO NOT hardcode secrets directly in this script for production environments.
# Consider using environment modules, external secret management systems, or a secure injection method.
export DATABASE_URL=""
export MINIO_ENDPOINT="minio_host:9000"
export MINIO_ACCESS_KEY=""
export MINIO_SECRET_KEY=""
export MINIO_BUCKET_NAME="flood-data"
export MINIO_SECURE="True" # Ensure this is True for production/HPC
export API_KEY_HASH_SALT=""
export REDIS_URL="redis://redis_host:6379/0"

# Navigate to your application directory.
# Replace '/path/to/your/quantum-flood-forecasting-framework/app' with the actual deployment path of your application on the HPC file system.
cd /path/to/your/quantum-flood-forecasting-framework/app

# Run the Celery worker
# Use --pool=fork or --pool=prefork for production/HPC for better concurrency
# Adjust --concurrency based on --cpus-per-task and available resources
echo "Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info --pool=fork --concurrency=4

echo "Celery worker finished."
