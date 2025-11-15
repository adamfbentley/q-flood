FROM python:3.11-slim-bookworm as builder

# Install system dependencies for geospatial libraries (rasterio, shapely, fiona, geopandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    libgeos-dev \
    # Clean up apt cache
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim-bookworm

# Install only runtime system dependencies if different or needed
# For geospatial libraries, the runtime often needs the same libs as build
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    libgeos-dev \
    # Clean up apt cache
    && rm -rf /var/lib/apt/lists/*

# CQ-007: Create a non-root user
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app

# Copy only installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# CQ-007: Copy application files as the non-root user
COPY --chown=appuser:appuser . .

# Switch to the non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
