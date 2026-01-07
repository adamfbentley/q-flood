# Q-Flood Deployment Status

**Last Updated:** November 15, 2025

## Current Deployment State

### ✅ LOCAL DOCKER (FULLY OPERATIONAL)

**Status:** **WORKING** - All services healthy and stable

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

**Services Running:**
- ✅ **flood_backend** - Up 2 hours (FastAPI, 2GB memory limit)
- ✅ **flood_frontend** - Up 13 hours (React + Vite)
- ✅ **flood_celery_worker** - Up 1 hour (1.5GB memory limit)
- ✅ **flood_db** - Up 16 hours (PostgreSQL + PostGIS)
- ✅ **flood_redis** - Up 16 hours (Message broker)
- ✅ **flood_minio** - Up 16 hours (S3-compatible storage)

**Start Command:**
```bash
cd c:\Users\adamf\Desktop\pp\repositories\q-flood
docker-compose up -d
```

**Stop Command:**
```bash
docker-compose down
```

**Verified Working:**
- All 3 solver types (CLASSICAL, QUANTUM, HYBRID) ✅
- Job submission and completion ✅
- GeoJSON and PDF generation ✅
- Frontend visualization ✅
- API authentication ✅
- Memory stability (no OOM crashes) ✅

---

### ❌ CLOUD DEPLOYMENT (BROKEN - INTENTIONALLY ARCHIVED)

**Status:** **NOT DEPLOYED** - Cloud deployment removed from project scope

#### Railway Backend
- **URL:** https://web-production-2d620.up.railway.app
- **Status:** Unreachable (502 error or timeout)
- **Issue:** Geospatial dependencies (GDAL, GEOS, PostGIS) fail to build on Railway
- **Decision:** Archived all Railway configs (railway.json, Procfile, .railwayignore)

#### Vercel Frontend
- **URL:** https://q-flood.vercel.app
- **Status:** Frontend loads but cannot connect to broken Railway backend
- **Decision:** Archived vercel.json config

---

## Why Cloud Deployment Was Removed

### Technical Reasons:
1. **Geospatial Dependencies:** GDAL, GEOS, and PostGIS are extremely difficult to build on PaaS platforms like Railway
2. **Memory Requirements:** Backend needs 2GB+ RAM, Celery needs 1.5GB+ RAM (expensive on cloud)
3. **Service Dependencies:** Requires PostgreSQL+PostGIS, Redis, MinIO - complex cloud setup
4. **Quantum Simulation:** Qiskit quantum circuits need significant compute resources

### Strategic Reasons:
1. **Honest Positioning:** Q-Flood is a research/demonstration project, not a production SaaS
2. **Docker-First:** Better for portfolio to show "reproducible Docker setup" than "broken cloud deploy"
3. **Cost:** Running 6 services in cloud is expensive for a portfolio project
4. **Maintenance:** Local Docker is stable, cloud deployment requires constant fixes

### What Was Archived:
- `railway.json` - Railway deployment config
- `vercel.json` - Vercel deployment config
- `Procfile` - Railway process file
- `.railwayignore` - Railway ignore file
- `deployment/` - Cloud deployment scripts
- `k8s/` - Kubernetes configs (overkill for demo)
- `hpc/` - HPC cluster configs (academic environment specific)
- `requirements-minimal.txt` - Simplified cloud dependencies (incomplete)

All archived files moved to: `archive/` directory

---

## Deployment Philosophy

**Q-Flood is positioned as:**
- ✅ **Docker-First Research Project** - Easy to run locally with single command
- ✅ **Portfolio Demonstration** - Shows technical capability, not production ops
- ✅ **Reproducible Science** - Anyone with Docker can run it exactly as designed

**NOT positioned as:**
- ❌ Production SaaS application
- ❌ Cloud-native microservices
- ❌ Enterprise-ready platform

---

## For Recruiters/Portfolio Viewers

**To experience Q-Flood:**

1. **Prerequisites:** Docker Desktop installed
2. **Clone:** `git clone https://github.com/adamfbentley/q-flood.git`
3. **Run:** `docker-compose up -d` (starts all 6 services)
4. **Access:** http://localhost:5173
5. **Try Examples:** See `examples/` directory for runnable Python scripts

**Expected Result:** All 3 solver types (CLASSICAL, QUANTUM, HYBRID) working in ~2 seconds per job

**This demonstrates:**
- Full-stack architecture (FastAPI, React, PostgreSQL, Redis, MinIO, Celery)
- Quantum computing (real HHL algorithm with Qiskit)
- Geospatial processing (PostGIS, GeoPandas)
- Containerization and orchestration (Docker Compose)
- API design and documentation (OpenAPI/Swagger)
- Asynchronous task processing (Celery workers)

---

## Maintenance Notes

### When Docker Containers Restart:

If you need to restart the Docker stack:

```bash
# Stop all services
docker-compose down

# Start fresh (rebuilds if needed)
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend
```

### Memory Usage:

Monitor with:
```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

Expected memory usage:
- Backend: ~100-300MB (limit: 2GB)
- Celery: ~100-200MB (limit: 1.5GB)
- PostgreSQL: ~50-100MB
- Redis: ~10-20MB
- MinIO: ~50-100MB
- Frontend: ~50-100MB

**Total:** ~500MB typical, ~4GB reserved (safe headroom)

### If OOM Errors Return:

Already fixed with memory limits in `docker-compose.yml`:
```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
      reservations:
        memory: 512M
```

### API Key:

Default: `QDSvBytSu8Nhe4rpBd7uP-CiY2f-astYRxrTaT0AYM8`

Stored in database, hashed with SHA-256. See `backend/core/security.py` for implementation.

---

## Summary for Handover

**Tell new AI agents:**

1. ✅ **Local Docker works perfectly** - 6 services, stable, all solvers functional
2. ❌ **Cloud deployment intentionally removed** - Not worth fixing, archived
3. ✅ **README accurate** - Says "runs locally via Docker"
4. ✅ **No broken links** - All cloud references removed
5. ✅ **Portfolio ready** - Easy demo, professional positioning

**No action needed on deployment.** Focus on:
- CV improvements
- Other repository assessments
- Documentation quality
- Code examples and showcases

---

## Historical Context

**What happened:**
- Nov 14-15: Attempted to fix Railway deployment (~13 commits)
- Result: Railway 502 errors persist (geospatial build failures)
- Decision: Simplify to Docker-only (commit cb667ca)
- Outcome: Clean, honest, working solution

**Lesson learned:** Better to have one working deployment method than multiple broken ones.

Q-Flood's value is in the technical implementation (quantum HHL, geospatial processing, full-stack architecture), not in cloud hosting.

---

**Deployment Status: RESOLVED ✅**

Local Docker deployment is stable and documented. Cloud deployment intentionally archived. No further action required.
