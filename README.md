# Q-Flood: Quantum-Classical Hybrid Flood Forecasting Framework

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-purple.svg)](https://qiskit.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

A flood modelling application that integrates **quantum computing algorithms** with classical scientific computing for geospatial analysis. Features a hybrid quantum-classical solver architecture with automatic fallback for production reliability.

> **Note**: This is an experimental project demonstrating quantum computing integration in scientific applications. The quantum solver operates at demonstration scale and is not intended for production flood forecasting.

## 🌟 Key Features

### Quantum Computing Implementation
- **Qiskit HHL Algorithm**: Quantum linear solver for flood modelling equations
- **3-Qubit Quantum Circuits**: Custom quantum gate operations (Hadamard, CNOT, rotation gates)
- **AerSimulator Integration**: Quantum circuit simulation with statevector method
- **Hybrid Architecture**: Intelligent quantum-classical fallback system for production reliability

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
                     │    └──> AerSimulator (3-qubit circuits)
                     │
                     └──> Classical Solver Service (NumPy/SciPy)
                          └──> Automatic fallback on quantum failure
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
- 3 qubits (1 ancilla, 2 for system state)
- Hadamard gates for superposition
- Controlled rotation gates for eigenvalue inversion
- CNOT gates for entanglement
- Measurement and classical post-processing

**Advantages:**
- Exponential speedup for specific problem classes
- Efficient for large sparse matrices
- Demonstrates quantum computing in real applications

**Limitations (Acknowledged):**
- Current implementation is demonstration-scale
- NISQ-era quantum computers have noise constraints
- Hybrid fallback ensures production reliability

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

This project demonstrates practical quantum computing integration in scientific applications. Related research includes:

- **HHL Algorithm**: Harrow, A. W., Hassidim, A., & Lloyd, S. (2009). "Quantum algorithm for linear systems of equations." Physical Review Letters.
- **NISQ Applications**: Preskill, J. (2018). "Quantum Computing in the NISQ era and beyond." Quantum.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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

**Note**: This is a research and demonstration project. The quantum solver is designed for educational purposes and proof-of-concept. For production flood forecasting, the hybrid fallback ensures reliable results using classical methods when needed.
