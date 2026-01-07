# Q-Flood: Quantum-Classical Hybrid Computing Project

**Status:** Functional (local Docker deployment)  
**Repository:** https://github.com/adamfbentley/q-flood

---

## Overview

A full-stack application exploring quantum algorithms for linear systems, featuring a working implementation of the HHL (Harrow-Hassidim-Lloyd) quantum algorithm alongside classical solvers.

**Key Technologies:**
- **Quantum:** Qiskit HHL implementation with AerSimulator
- **Backend:** FastAPI, Celery, PostgreSQL + PostGIS
- **Infrastructure:** 6-service Docker Compose stack
- **Frontend:** React with job visualization

---

## What's Implemented

### Quantum Computing
- HHL algorithm implementation (270 lines, 4-qubit circuits)
- Quantum phase estimation, controlled rotations, QFT
- Comparison framework: quantum vs classical solvers

### Full-Stack Infrastructure
- FastAPI REST API with async job management
- PostgreSQL + PostGIS for geospatial data storage
- Celery workers + Redis for background processing
- MinIO S3-compatible object storage
- React frontend with real-time job status
- Docker Compose orchestration

All services are tested and run locally.

---

## Technical Context

### About HHL Algorithm

The HHL algorithm theoretically achieves exponential speedup for solving linear systems. In practice:

- **Current implementation:** 2×2 matrices (demonstration scale)
- **Limitation:** Today's quantum hardware (and simulators) can't reach the scale where quantum advantage emerges
- **Learning value:** Understanding quantum circuit design, algorithm implementation, and the gap between theoretical and practical quantum computing

This project demonstrates the *implementation* of quantum algorithms while acknowledging that practical quantum advantage for linear systems requires hardware advances that don't exist yet.

### Why Build This?

1. **Learn quantum computing:** Implementing HHL teaches QPE, controlled rotations, QFT, and measurement
2. **Full-stack practice:** 6-service architecture with modern tooling (Docker, Celery, PostGIS)
3. **Honest exploration:** Understanding when quantum computing helps (specific problems, future hardware) vs. when classical is better (most current applications)

---

## Running Locally

```bash
git clone https://github.com/adamfbentley/q-flood
cd q-flood
docker-compose up -d
```

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│   Celery    │
│  Frontend   │     │   Backend   │     │   Workers   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                    ┌──────┴──────┐     ┌──────┴──────┐
                    │ PostgreSQL  │     │    Redis    │
                    │  + PostGIS  │     │   (Broker)  │
                    └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │    MinIO    │
                    │ (S3 Storage)│
                    └─────────────┘
```

---

## What I Learned

**Quantum Computing:**
- HHL algorithm implementation from theory to code
- Quantum circuit design patterns (QPE, QFT)
- Gap between theoretical complexity and practical performance

**Software Engineering:**
- Microservices architecture with Docker Compose
- Async job processing (Celery + Redis)
- Geospatial database design (PostGIS)
- Full-stack integration (FastAPI ↔ React)

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| Quantum | Qiskit, AerSimulator |
| Backend | Python, FastAPI, Celery |
| Database | PostgreSQL, PostGIS, Redis |
| Storage | MinIO (S3-compatible) |
| Frontend | React, Vite |
| DevOps | Docker, Docker Compose |

---

## References

- Harrow, A.W., Hassidim, A., & Lloyd, S. (2009). Quantum algorithm for linear systems of equations. *Physical Review Letters*, 103(15), 150502.
- Qiskit Documentation: https://qiskit.org/

---

## Contact

**Adam Bentley**  
Email: adam.f.bentley@gmail.com  
GitHub: [@adamfbentley](https://github.com/adamfbentley)

---

## License

MIT License
