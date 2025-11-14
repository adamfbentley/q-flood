# Q-Flood Setup Guide

## Prerequisites Installation

### 1. Install Docker Desktop
1. Download from: https://www.docker.com/products/docker-desktop/
2. Run installer and restart computer
3. Verify: `docker --version` and `docker-compose --version`

### 2. Install Python 3.11+ (if not installed)
1. Download from: https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Verify: `python --version`

---

## Quick Start (Recommended)

### Option 1: Docker (Full System)

1. **Navigate to project:**
   ```powershell
   cd c:\Users\adamf\Desktop\pp\repositories\q-flood
   ```

2. **Ensure .env file exists:**
   ```powershell
   # File should already exist, but if not:
   Copy-Item .env.example .env
   ```

3. **Start all services:**
   ```powershell
   docker-compose up -d
   ```

4. **Initialize database:**
   ```powershell
   docker-compose exec backend python -m app.db.init_db
   ```

5. **Access the application:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001 (login: minioadmin/minioadmin)
   - Frontend: http://localhost:5173

6. **View logs:**
   ```powershell
   docker-compose logs -f backend
   ```

7. **Stop services:**
   ```powershell
   docker-compose down
   ```

---

### Option 2: Python Virtual Environment (Development)

**Use this for development/testing without Docker**

1. **Create virtual environment:**
   ```powershell
   cd c:\Users\adamf\Desktop\pp\repositories\q-flood
   python -m venv venv
   ```

2. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   *If you get an error about execution policy, run:*
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Install dependencies:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run simple test server (no database required):**
   ```powershell
   uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access test server:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

6. **Deactivate when done:**
   ```powershell
   deactivate
   ```

---

## Testing the Quantum Solver

### Run Unit Tests

```powershell
# With virtual environment activated:
pytest tests/test_quantum_solver_unit.py -v

# Run all tests:
pytest -v

# Run with coverage:
pytest --cov=app --cov-report=html
```

### Test Quantum Circuit Manually

Create a test file `test_hhl_manual.py`:

```python
import numpy as np
from app.services.quantum_solver import QuantumSolverService

# Initialize solver
solver = QuantumSolverService()

# Simple 2x2 test system
A = np.array([[1.5, 0.5], [0.5, 1.5]])
b = np.array([1.0, 0.0])

# Prepare matrix
A_prepared, b_norm, norm = solver._prepare_matrix(
    scipy.sparse.csr_matrix(A), b, "test-job-001"
)

# Build and view circuit
circuit = solver._build_hhl_circuit(A_prepared, b_norm, "test-job-001")
print(circuit)
print(f"Circuit depth: {circuit.depth()}")
print(f"Circuit width: {circuit.num_qubits}")
```

Run it:
```powershell
python test_hhl_manual.py
```

---

## Troubleshooting

### Docker Issues

**"Cannot connect to Docker daemon"**
- Ensure Docker Desktop is running (check system tray)
- Restart Docker Desktop

**"Port already in use"**
```powershell
# Find process using port 8000:
netstat -ano | findstr :8000
# Kill process (replace PID with actual process ID):
taskkill /PID <PID> /F
```

**"No space left on device"**
```powershell
# Clean up Docker:
docker system prune -a --volumes
```

### Python Issues

**"Python not found"**
- Reinstall Python and check "Add to PATH"
- Or use full path: `C:\Python311\python.exe`

**"Module not found"**
```powershell
# Ensure virtual environment is activated:
.\venv\Scripts\Activate.ps1
# Reinstall dependencies:
pip install -r requirements.txt
```

**"Execution policy error"**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Database Issues (Docker only)

**"Database connection failed"**
```powershell
# Check if database container is running:
docker-compose ps

# View database logs:
docker-compose logs db

# Restart database:
docker-compose restart db
```

---

## Development Workflow

### Make code changes and test:

```powershell
# 1. Start services
docker-compose up -d

# 2. Watch logs
docker-compose logs -f backend

# 3. Make changes to code in app/

# 4. Restart backend to see changes:
docker-compose restart backend

# 5. Or rebuild if you changed dependencies:
docker-compose down
docker-compose up --build -d
```

### Run specific tests:

```powershell
# Test quantum solver:
pytest tests/test_quantum_solver.py -v

# Test with specific test:
pytest tests/test_quantum_solver_unit.py::test_quantum_solver_initialization -v
```

---

## Architecture Overview

**Services:**
- **backend** (FastAPI): Main API server (port 8000)
- **celery_worker**: Background task processor
- **db** (PostgreSQL + PostGIS): Database (port 5432)
- **redis**: Message broker (port 6379)
- **minio**: Object storage (ports 9000, 9001)
- **frontend** (Vite): Web UI (port 5173)

**Data Flow:**
1. API receives job submission
2. Stores data in MinIO
3. Celery worker picks up task
4. Quantum solver processes matrix
5. Results stored in MinIO + PostgreSQL
6. Frontend displays results

---

## Next Steps After Setup

1. ✅ Verify Docker is running
2. ✅ Start services with `docker-compose up -d`
3. ✅ Check http://localhost:8000/docs
4. ✅ Run unit tests: `pytest tests/ -v`
5. ✅ Submit a test job via API docs
6. ✅ Monitor Celery logs: `docker-compose logs -f celery_worker`
7. ✅ View results in MinIO console: http://localhost:9001

---

## Useful Commands

```powershell
# View all running containers:
docker-compose ps

# View logs for specific service:
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Enter a container shell:
docker-compose exec backend bash

# Stop specific service:
docker-compose stop backend

# Restart service:
docker-compose restart backend

# Remove all containers and volumes:
docker-compose down -v

# Rebuild specific service:
docker-compose up -d --build backend
```

---

## Performance Testing

Once running, you can benchmark quantum vs classical:

```python
import time
import requests

API_URL = "http://localhost:8000"
API_KEY = "test-key"  # Use actual API key from .env

# Submit quantum job
response = requests.post(
    f"{API_URL}/api/v1/jobs/submit",
    json={
        "solver_type": "quantum",
        "matrix_size": 2,
        "flood_zone": {...}  # GeoJSON data
    },
    headers={"X-API-Key": API_KEY}
)

job_id = response.json()["job_id"]
print(f"Job submitted: {job_id}")

# Poll for completion
while True:
    status = requests.get(
        f"{API_URL}/api/v1/jobs/{job_id}/status",
        headers={"X-API-Key": API_KEY}
    ).json()
    
    if status["status"] == "COMPLETED":
        print(f"Quantum solve completed in {status['execution_time']}s")
        break
    
    time.sleep(1)
```

---

**Ready to start? Follow Option 1 (Docker) for full system or Option 2 (Python) for quick testing!**
