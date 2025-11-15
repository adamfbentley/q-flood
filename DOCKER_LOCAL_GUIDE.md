# Running Q-Flood Locally with Docker

This guide explains how to run the **complete Q-Flood application** locally with all services using Docker Compose.

## 🎯 Why Docker?

Q-Flood uses Docker for:
- ✅ **Reproducibility**: Works the same on any system
- ✅ **Complete Stack**: All 6 services (PostgreSQL, Redis, MinIO, Celery, Backend, Frontend)
- ✅ **Easy Setup**: Single `docker-compose up` command
- ✅ **Full Features**: Job processing, quantum/classical solvers, geospatial analysis
- ✅ **Isolation**: No conflicts with your local Python/Node installations

---

## 📋 Prerequisites

1. **Docker Desktop** installed and running
   - Windows: https://www.docker.com/products/docker-desktop/
   - Check: `docker --version` should show version 20.10+

2. **Docker files exist locally** (not in git)
   - `Dockerfile`
   - `docker-compose.yml`
   - Both files are ignored by git to keep deployment simple

---

## 🚀 Quick Start

### Step 1: Ensure Docker Desktop is Running
```powershell
# Check Docker is running
docker ps

# Should show: "CONTAINER ID   IMAGE   ..."
# If error: Start Docker Desktop application
```

### Step 2: Start All Services
```powershell
cd c:\Users\adamf\Desktop\pp\repositories\q-flood

# Build and start all services (first time takes 5-10 minutes)
docker-compose up --build -d

# Check status
docker-compose ps
```

### Step 3: Wait for Services to Initialize
```powershell
# Watch logs until you see "Application startup complete"
docker-compose logs -f backend

# Press Ctrl+C to stop watching logs
```

### Step 4: Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (login: minioadmin/minioadmin)

---

## 📦 What Gets Started

| Service | Port | Description |
|---------|------|-------------|
| **PostgreSQL** | 5432 | Database with PostGIS extension |
| **Redis** | 6379 | Message broker for Celery |
| **MinIO** | 9000, 9001 | S3-compatible object storage |
| **Backend API** | 8000 | FastAPI with quantum/classical solvers |
| **Celery Worker** | - | Background job processor |
| **Frontend** | 5173 | React UI with map visualization |

---

## 🧪 Testing the Full Application

### 1. Check Backend Health
```powershell
# Should return: {"message": "Welcome to Q-Flood API"}
curl http://localhost:8000
```

### 2. View API Documentation
Open in browser: http://localhost:8000/docs

### 3. Create a Test Job
Use the API docs at `/docs` or create a script:

```python
import requests

job = requests.post("http://localhost:8000/api/v1/jobs/", json={
    "name": "Test Quantum Job",
    "solver_type": "quantum",
    "geojson": {
        "type": "FeatureCollection",
        "features": [...]
    }
})

print(job.json())
```

### 4. View Job Processing
```powershell
# Watch Celery worker logs
docker-compose logs -f celery_worker

# Watch backend logs
docker-compose logs -f backend
```

---

## 🛠️ Common Commands

### Start Services
```powershell
docker-compose up -d          # Start in background
docker-compose up             # Start with logs visible
```

### Stop Services
```powershell
docker-compose down           # Stop all services
docker-compose down -v        # Stop and remove volumes (clean database)
```

### View Logs
```powershell
docker-compose logs           # All services
docker-compose logs backend   # Specific service
docker-compose logs -f        # Follow (live)
```

### Restart a Service
```powershell
docker-compose restart backend
docker-compose restart celery_worker
```

### Rebuild After Code Changes
```powershell
docker-compose up --build -d
```

---

## 🔧 Troubleshooting

### Docker Desktop Not Running
```
Error: Cannot connect to the Docker daemon
```
**Solution:** Start Docker Desktop application

### Port Already in Use
```
Error: port is already allocated
```
**Solution:** Stop conflicting service or change port in `docker-compose.yml`

### Services Keep Restarting
```powershell
# Check what's wrong
docker-compose logs backend
docker-compose logs celery_worker
```

### Database Connection Issues
```powershell
# Reset database
docker-compose down -v
docker-compose up -d
```

### Need Fresh Start
```powershell
# Nuclear option: remove everything and start fresh
docker-compose down -v
docker system prune -a
docker-compose up --build -d
```

---

## 🆚 Local vs Deployed Versions

| Feature | Local (Docker) | Deployed (Railway/Vercel) |
|---------|----------------|---------------------------|
| **Frontend UI** | ✅ Full | ✅ Full |
| **Backend API** | ✅ Full | ✅ Full |
| **Quantum Solver** | ✅ Works | ✅ Works |
| **Classical Solver** | ✅ Works | ✅ Works |
| **Background Jobs** | ✅ Works (Celery) | ❌ No Celery |
| **File Storage** | ✅ Works (MinIO) | ❌ No MinIO |
| **Database** | ✅ PostgreSQL + PostGIS | ✅ SQLite |
| **Geospatial Features** | ✅ Full | ⚠️ Limited |
| **Cost** | Free (local) | Free (tier limits) |
| **Internet Required** | ❌ No | ✅ Yes |

---

## 📝 Development Workflow

1. **Make code changes** in `backend/` or `frontend/`
2. **Rebuild and restart**:
   ```powershell
   docker-compose up --build -d
   ```
3. **Test changes** at http://localhost:5173
4. **View logs** if something breaks:
   ```powershell
   docker-compose logs -f
   ```

---

## 🎯 When to Use Which Version

### Use **Local Docker** when:
- ✅ Developing new features
- ✅ Testing full job processing
- ✅ Need file uploads
- ✅ Testing geospatial features
- ✅ Debugging background tasks

### Use **Deployed Version** when:
- ✅ Showing to recruiters/employers
- ✅ Adding to CV/portfolio
- ✅ Quick demos
- ✅ Testing frontend UI only

---

## 🔐 Environment Variables

The `.env` file contains Docker service names:
- `DATABASE_URL=postgresql://user:password@db:5432/flood_db`
- `REDIS_URL=redis://redis:6379/0`
- `MINIO_ENDPOINT=minio:9000`

These work because Docker Compose creates a network where services can find each other by name.

---

## 📚 Next Steps

1. ✅ Start Docker Desktop
2. ✅ Run `docker-compose up -d`
3. ✅ Wait for services to start
4. ✅ Open http://localhost:5173
5. ✅ Test creating a job
6. ✅ Check Celery processes it
7. 🎉 Full Q-flood working locally!

---

## ❓ Questions?

Check the main README.md for general info, or:
- View logs: `docker-compose logs -f`
- Check service status: `docker-compose ps`
- Restart everything: `docker-compose restart`

You now have Q-Flood running locally with all quantum and classical solvers operational!