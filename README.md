# Q-Flood: Quantum-Classical Hybrid Flood Forecasting Framework

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-purple.svg)](https://qiskit.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)

A flood modelling application that integrates **quantum computing algorithms** with classical scientific computing for geospatial analysis. Features a hybrid quantum-classical solver architecture with automatic fallback for production reliability.

## 🌐 Live Demo

- **API Backend**: [https://web-production-2d620.up.railway.app](https://web-production-2d620.up.railway.app)
- **API Documentation**: [https://web-production-2d620.up.railway.app/docs](https://web-production-2d620.up.railway.app/docs)
- **Frontend**: Coming soon (deploying to Vercel)

> **Project Context**: Built as an entry for the XPRIZE Quantum Applications competition, exploring practical applications of quantum computing in environmental science and disaster preparedness.

> **Note**: This is an experimental project demonstrating quantum computing integration in scientific applications. The quantum solver operates at demonstration scale and is not intended for production flood forecasting.

## 🌟 Key Features

### Quantum Computing Implementation
- **Qiskit HHL Algorithm**: Demonstration-scale quantum linear solver (2x2 matrices)
- **4-Qubit Quantum Circuits**: Custom quantum gate operations (Hadamard, CNOT, controlled rotations, QFT)
- **AerSimulator Integration**: Quantum circuit simulation with statevector method
- **Hybrid Architecture**: Automatic fallback to classical solvers for reliability and scalability

### Backend & Infrastructure
- **FastAPI REST API**: Modern async Python web framework with OpenAPI documentation
- **PostgreSQL/PostGIS**: Geospatial database for flood zone storage and spatial queries
- **Celery Task Queues**: Asynchronous job processing for quantum/classical computations
- **Redis Message Broker**: High-performance task queue management
- **MinIO Object Storage**: S3-compatible storage for large geospatial datasets
- **Docker Compose**: Fully containerised deployment with all services

### Geospatial Processing
- **GeoJSON Validation**: Comprehensive validation for flood zone geometries
- **GeoPandas Integration**: Advanced spatial data processing and analysis
- **PostGIS Spatial Queries**: Efficient geospatial database operations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI REST API                         │
│                    (API Key Authentication)                     │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ├──> PostgreSQL/PostGIS (Geospatial Data)
                │
                ├──> MinIO (S3 Object Storage)
                │
                └──> Celery Workers + Redis
                     │
                     ├──> Quantum Solver Service (Qiskit HHL)
                     │    └──> AerSimulator (4-qubit circuits, 2x2 matrices)
                     │
                     └──> Classical Solver Service (NumPy/SciPy)
                          └──> Automatic fallback for scalability
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/adamfbentley/q-flood.git
cd q-flood
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services with Docker Compose**
```bash
docker-compose up -d
```

4. **Initialize the database**
```bash
docker-compose exec api python -m app.db.init_db
```

5. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📖 Usage

### Submit a Flood modelling Job

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-api-key"

headers = {"X-API-Key": API_KEY}

# Upload GeoJSON flood zone data
flood_zone = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[...]]
            },
            "properties": {
                "name": "Wellington Harbor Basin",
                "risk_level": "high"
            }
        }
    ]
}

response = requests.post(
    f"{API_URL}/api/v1/jobs/submit",
    json={
        "flood_zone": flood_zone,
        "solver_type": "hybrid",  # "quantum", "classical", or "hybrid"
        "parameters": {
            "time_horizon": 24,
            "spatial_resolution": 100
        }
    },
    headers=headers
)

job_id = response.json()["job_id"]
print(f"Job submitted: {job_id}")
```

### Check Job Status

```python
status = requests.get(
    f"{API_URL}/api/v1/jobs/{job_id}/status",
    headers=headers
).json()

print(f"Status: {status['status']}")
# Possible states: PENDING, RUNNING, QUANTUM_RUNNING, 
#                  QUANTUM_FAILED_FALLBACK_INITIATED,
#                  FALLBACK_CLASSICAL_RUNNING, COMPLETED, FAILED
```

### Retrieve Results

```python
if status['status'] == 'COMPLETED':
    results = requests.get(
        f"{API_URL}/api/v1/jobs/{job_id}/results",
        headers=headers
    ).json()
    
    print(f"Solution: {results['solution_url']}")
    print(f"Solver used: {results['solver_type']}")
    print(f"Performance: {results['metrics']}")
```

## 🧪 Quantum Algorithm Details

### HHL Algorithm Implementation

The quantum solver implements the **Harrow-Hassidim-Lloyd (HHL) algorithm** for solving linear systems Ax = b, which is fundamental to flood modelling differential equations.

**Quantum Circuit Structure:**
- 4 qubits (1 ancilla, 2 for eigenvalue estimation, 1 for state register)
- Quantum Phase Estimation (QPE) for eigenvalue extraction
- Controlled Y-rotations for eigenvalue inversion (1/λ)
- Inverse QPE to uncompute phase estimation
- Post-selection on ancilla qubit measurement

**Current Implementation:**
- Operates on 2x2 linear systems (demonstration scale)
- Uses simplified Hamiltonian simulation via controlled-phase gates
- Executes on ideal AerSimulator (no noise modeling)
- Theoretical exponential speedup requires much larger problem sizes (N > 1000)

**Practical Limitations:**
- Current quantum hardware insufficient for production flood modeling
- 2x2 matrices: classical solver is faster (quantum overhead dominates)
- Real flood models require ~10^6 x 10^6 matrices (beyond current quantum capability)
- Hybrid architecture ensures usable results via classical fallback today

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Quantum Computing** | Qiskit, Qiskit-Aer (AerSimulator) |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy |
| **Database** | PostgreSQL 15, PostGIS 3.3 |
| **Task Processing** | Celery, Redis |
| **Storage** | MinIO (S3-compatible) |
| **Scientific Computing** | NumPy, SciPy, Numba |
| **Geospatial** | GeoPandas, GeoJSON, Shapely |
| **DevOps** | Docker, Docker Compose |
| **Testing** | pytest, pytest-asyncio |

## 📁 Project Structure

```
q-flood/
├── app/
│   ├── api/              # FastAPI routes and endpoints
│   ├── models/           # SQLAlchemy database models
│   ├── services/         # Business logic
│   │   ├── quantum_solver.py    # Qiskit HHL implementation
│   │   └── classical_solver.py  # NumPy/SciPy fallback
│   ├── tasks/            # Celery async tasks
│   │   ├── quantum_tasks.py     # Quantum job processing
│   │   └── solver_tasks.py      # Classical job processing
│   ├── schemas/          # Pydantic validation models
│   └── core/             # Configuration and utilities
├── tests/                # Test suite
├── docker-compose.yml    # Multi-container orchestration
├── Dockerfile           # API container image
└── README.md
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Test quantum solver specifically
pytest tests/test_quantum_solver.py -v
```

## 🔧 Configuration

Key environment variables (`.env`):

```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/qflood

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key

# API
API_KEY=your-secure-api-key
SECRET_KEY=your-jwt-secret

# Quantum Settings
QUANTUM_BACKEND=aer_simulator
QUANTUM_SHOTS=1000
ENABLE_QUANTUM_FALLBACK=true
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas of interest:

- Enhanced quantum algorithms (QAOA, VQE for optimisation)
- Improved quantum error mitigation
- Real quantum hardware integration (IBM Quantum, AWS Braket)
- Performance optimisation
- Additional geospatial features
- Documentation improvements

## 📚 Research & Publications

This project demonstrates quantum computing implementation in a scientific software context. The HHL algorithm is implemented at demonstration scale following:

- **HHL Algorithm**: Harrow, A. W., Hassidim, A., & Lloyd, S. (2009). "Quantum algorithm for linear systems of equations." Physical Review Letters, 103(15), 150502.
- **NISQ Era**: Preskill, J. (2018). "Quantum Computing in the NISQ era and beyond." Quantum, 2, 79.

**Note**: This implementation is for educational and demonstration purposes. Production quantum advantage for flood modeling requires quantum computers with 50+ qubits and error correction, which remain under development.

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details. This license ensures the code remains open source even when used as a network service.

## 👤 Author

**Adam Bentley**
- Physics & Mathematics, Victoria University of Wellington
- Email: adam.f.bentley@gmail.com
- GitHub: [@adamfbentley](https://github.com/adamfbentley)

## 🙏 Acknowledgments

- Qiskit development team for quantum computing framework
- FastAPI community for excellent async web framework
- PostGIS for powerful geospatial database extensions

---

## ⚠️ Important Disclaimers

**Quantum Computing Scope**: 
- The HHL implementation operates on 2x2 matrices for demonstration purposes
- Current quantum hardware (NISQ era) cannot solve production-scale flood modeling problems
- Classical solvers are faster and more practical for real flood forecasting today
- This project demonstrates quantum algorithm integration, not production quantum advantage

**Educational Purpose**: 
- Built to explore quantum computing in scientific software engineering
- Suitable for learning quantum algorithms and hybrid system architectures
- Not validated for operational flood forecasting or disaster response
- The hybrid fallback architecture ensures usable results via classical computation
