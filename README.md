# Q-Flood: Quantum-Classical Hybrid Linear Solver

Exploration of quantum computing algorithms integrated with classical scientific computing infrastructure.

---

## Overview

Q-Flood implements a quantum-classical hybrid system demonstrating the HHL algorithm (Harrow-Hassidim-Lloyd quantum linear solver) alongside classical methods within a full-stack architecture. This project explores practical applications and limitations of near-term quantum computing.

**Key Learning Goals:**
- Understand quantum algorithm implementation using Qiskit
- Explore hybrid quantum-classical computation patterns
- Practice full-stack architecture with microservices
- Investigate when quantum approaches are advantageous

---

## Architecture

### System Components

**6-Service Containerized Stack:**
- **FastAPI REST API** - Job submission and management endpoints
- **PostgreSQL + PostGIS** - Spatial data storage and job metadata
- **Celery Workers** - Asynchronous task processing
- **Redis** - Message broker for job queue
- **MinIO** - S3-compatible object storage
- **React Frontend** - Job submission and monitoring interface

### Quantum Computing Component

**HHL Algorithm Implementation:**
- Qiskit-based quantum linear solver
- AerSimulator backend for quantum circuit execution
- Demonstration scale: 4-qubit circuits solving 2×2 systems
- Automatic fallback to NumPy/SciPy for larger systems

### Classical Computing Component

**Optimized Classical Solvers:**
- NumPy linear algebra routines
- SciPy sparse matrix solvers
- Performance comparison with quantum approach

---

## Technical Implementation

### Hybrid Solver Pattern

```python
def solve_linear_system(A, b):
    """
    Attempts quantum solver first, falls back to classical
    """
    if matrix_size <= 2:
        try:
            return quantum_hhl_solve(A, b)
        except QuantumError:
            return classical_solve(A, b)
    else:
        return classical_solve(A, b)
```

### Key Features

- **Job orchestration** with status tracking
- **Async processing** using Celery task queue
- **Geospatial data support** via PostGIS extensions
- **RESTful API** with OpenAPI documentation
- **Docker Compose** deployment for reproducibility

---

## Getting Started

### Prerequisites
```bash
docker
docker-compose
```

### Start the Stack
```bash
docker-compose up
```

### Submit a Job
```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "matrix": [[2, 1], [1, 2]],
    "vector": [3, 3],
    "solver": "hybrid"
  }'
```

### Check Results
```bash
curl http://localhost:8000/api/jobs/{job_id}
```

---

## Technical Scope

### Quantum Solver Capabilities

**Current Implementation:**
- Solves 2×2 linear systems using 4-qubit HHL algorithm
- Demonstrates quantum circuit design and execution
- Validates quantum algorithm correctness on simple cases

**Practical Limitations:**
- Limited to toy-scale problems due to qubit requirements
- Classical algorithms more efficient for current hardware
- Serves as educational demonstration of quantum concepts

### Classical Solver Capabilities

**Production-Ready:**
- Handles arbitrary-size matrices efficiently
- Optimized NumPy/SciPy implementations
- Sparse matrix support for large systems
- Production reliability and performance

---

## Use Cases

### Educational
- Learning quantum algorithm implementation
- Understanding HHL algorithm mechanics
- Exploring quantum-classical hybrid patterns
- Hands-on quantum circuit programming with Qiskit

### Software Engineering
- Microservices architecture patterns
- Asynchronous task processing
- Docker containerization practices
- RESTful API design

### Research Context
- Investigating quantum advantage conditions
- Benchmarking quantum vs classical approaches
- Exploring near-term quantum computing limitations

---

## Performance Characteristics

### Quantum Solver (HHL)
- **Problem Size:** 2×2 matrices only
- **Execution Time:** ~1-2 seconds (simulation overhead)
- **Accuracy:** Comparable to classical for demonstration cases
- **Scalability:** Limited by qubit availability

### Classical Solver (NumPy)
- **Problem Size:** Arbitrary (limited by memory)
- **Execution Time:** Milliseconds for small systems, seconds for large sparse systems
- **Accuracy:** Machine precision
- **Scalability:** Production-ready for real applications

---

## Technical Stack

**Quantum Computing:**
- Qiskit - Quantum circuit programming
- AerSimulator - Quantum circuit simulation

**Backend:**
- Python 3.9+
- FastAPI - REST API framework
- SQLAlchemy - ORM for PostgreSQL
- Celery - Distributed task queue
- Redis - Message broker

**Data:**
- PostgreSQL - Relational database
- PostGIS - Geospatial extensions
- MinIO - Object storage

**Frontend:**
- React - UI framework
- Basic job submission interface

**DevOps:**
- Docker - Containerization
- Docker Compose - Multi-service orchestration

---

## Development Roadmap

**Completed:**
- ✅ HHL algorithm implementation
- ✅ Classical solver integration
- ✅ Hybrid fallback pattern
- ✅ Docker Compose stack
- ✅ FastAPI REST API
- ✅ Celery job processing
- ✅ Basic React frontend

**Future Enhancements:**
- 📋 Extended quantum algorithms (VQE, QAOA)
- 📋 Quantum circuit visualization
- 📋 Performance benchmarking dashboard
- 📋 Educational documentation and tutorials

---

## Key Insights

### When Quantum Computing Makes Sense
- Specific problem structures with exponential speedup potential
- Sufficiently large problem sizes (>>100 dimensions)
- Hardware with enough qubits and low error rates
- Problems without efficient classical algorithms

### When Classical Computing Wins
- Near-term hardware limitations (<100 qubits)
- Small-to-medium problem sizes
- Need for production reliability
- Existing optimized classical algorithms

### Hybrid Approaches
- Leverage quantum for specific subroutines
- Classical pre/post-processing
- Automatic fallback for reliability
- Best of both paradigms

---

## Documentation

Project includes:
- API documentation (OpenAPI/Swagger)
- Docker Compose configuration
- Service architecture diagrams
- Algorithm implementation notes

---

## Contributing

Issues and pull requests welcome. Focus areas:
- Additional quantum algorithms
- Performance optimizations
- Documentation improvements
- Educational content

---

## License

Personal Project - Open to collaboration

---

## Contact

**Adam Frank Bentley**
- Email: adam.f.bentley@gmail.com
- GitHub: github.com/adamfbentley

---

## References

- Harrow, A. W., Hassidim, A., & Lloyd, S. (2009). Quantum algorithm for linear systems of equations. Physical Review Letters, 103(15), 150502.
- Qiskit Documentation: https://qiskit.org/documentation/
