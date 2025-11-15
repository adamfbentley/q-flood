# Q-Flood Usage Examples

This directory contains practical examples demonstrating how to use the Q-Flood API.

## Prerequisites

Before running these examples, ensure you have:

1. **Backend Running**: Docker stack up and running
   ```bash
   docker-compose up -d
   ```

2. **API Key**: Configure your API key in each example
   - Replace `YOUR_API_KEY_HERE` with your actual API key
   - Default key: `QDSvBytSu8Nhe4rpBd7uP-CiY2f-astYRxrTaT0AYM8`

3. **Python Environment**: Python 3.11+ with requests library
   ```bash
   pip install requests
   ```

## Examples

### 1. Classical Solver (`01_classical_solver.py`)

Demonstrates the classical solver using NumPy/SciPy sparse matrix methods.

```bash
python examples/01_classical_solver.py
```

**Features:**
- Fast execution (~0.08 seconds)
- High accuracy (direct sparse solver)
- Production-ready for real-world use
- Best for: Actual flood simulations

**Expected Output:**
```
🚀 Submitting classical solver job...
✅ Job submitted: 01234567-89ab-cdef-0123-456789abcdef
⏳ Waiting for job to complete...
✅ Job complete!
⚡ Performance:
   Solve time: 0.0843s
   Matrix size: 2500
```

---

### 2. Quantum Solver (`02_quantum_solver.py`)

Demonstrates the quantum HHL algorithm using Qiskit.

```bash
python examples/02_quantum_solver.py
```

**Features:**
- HHL (Harrow-Hassidim-Lloyd) algorithm
- 4-qubit quantum circuit (1 ancilla, 2 eigenvalue, 1 state)
- Operates on 2x2 submatrix (demonstration mode)
- ~11% error vs classical solution
- Best for: Quantum algorithm exploration

**Expected Output:**
```
🔮 Submitting quantum solver job...
   Algorithm: HHL (Harrow-Hassidim-Lloyd)
   Qubits: 4 (1 ancilla, 2 eigenvalue, 1 state)
   Matrix size: 2x2 (extracted from 50x50 grid)
✅ Job submitted: 01234567-89ab-cdef-0123-456789abcdef
⏳ Waiting for quantum computation...
✅ Quantum computation complete!
```

**Technical Details:**
- Uses Qiskit Aer statevector simulator
- Post-selection on ancilla qubit (success rate ~21.5%)
- Demonstrates quantum linear system solving
- Currently limited to small matrices (quantum hardware limitation)

---

### 3. Hybrid Solver (`03_hybrid_solver.py`)

Demonstrates the hybrid quantum-classical approach.

```bash
python examples/03_hybrid_solver.py
```

**Features:**
- Attempts quantum solver first
- Automatically falls back to classical if quantum fails
- Combines exploration with reliability
- Best for: Testing quantum in production environments

**Expected Output:**
```
🔄 Submitting hybrid solver job...
   Strategy: Quantum first, classical fallback
✅ Job submitted: 01234567-89ab-cdef-0123-456789abcdef
⏳ Processing hybrid computation...
✅ Hybrid computation complete!
🔍 Execution Path:
   ✅ Quantum solver succeeded!
```

---

### 4. Solver Comparison (`04_compare_solvers.py`)

Runs all three solvers and compares their performance side-by-side.

```bash
python examples/04_compare_solvers.py
```

**Features:**
- Sequential execution of all solver types
- Side-by-side performance metrics
- Identifies which solver was actually used
- Provides analysis and recommendations

**Expected Output:**
```
================================================================================
SOLVER COMPARISON
================================================================================

Metric                   CLASSICAL            QUANTUM              HYBRID              
--------------------------------------------------------------------------------
Solve Time (s)           0.0843               0.3012               0.0856              
Matrix Size              2500                 2500                 2500                
Actually Used            classical            quantum              classical           
--------------------------------------------------------------------------------

📊 Analysis:
   • Classical is 3.57x faster than quantum
   • Quantum solution has ~11% error vs classical (HLL limitation)
   • Hybrid fell back to classical solver
```

---

## Common Configuration

All examples use the same base configuration:

```python
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "YOUR_API_KEY_HERE"

job_data = {
    "solver_type": "CLASSICAL",  # or "QUANTUM", "HYBRID"
    "parameters": {
        "grid_resolution": 50,      # 50x50 grid (2500 cells)
        "conversion_factor": 0.1,   # Scale factor for matrix
        "flood_threshold": 0.05     # Threshold for flood detection
    }
}
```

## Customization

### Adjusting Grid Resolution

```python
"grid_resolution": 100  # Larger grid (10000 cells)
```

**Note:** Quantum solver always uses 2x2 submatrix regardless of full grid size.

### Changing Flood Threshold

```python
"flood_threshold": 0.1  # Higher threshold = less area marked as flooded
```

### Modifying Conversion Factor

```python
"conversion_factor": 0.5  # Affects matrix scaling and solution magnitudes
```

## Understanding Results

### Generated Files

Each successful job generates:

1. **Solution File** (`.npz`): NumPy array with flood depths
   - Path: `/app/results/{job_id}/solution.npz` (inside container)

2. **GeoJSON File**: Geographic flood visualization data
   - Path: `/app/results/{job_id}/flood_map.geojson`
   - Can be viewed in frontend or QGIS

3. **PDF Report**: Summary report with statistics
   - Path: `/app/results/{job_id}/report.pdf`

### Viewing Results

All results can be viewed in the frontend:
```
http://localhost:5173/jobs/{job_id}
```

The frontend provides:
- 2D flood heatmap (no Mapbox required)
- 3D flood visualization (if Mapbox token configured)
- Flood statistics (max depth, coverage, affected area)
- Job metadata and timing

## Troubleshooting

### Connection Refused

**Problem:** `requests.exceptions.ConnectionError`

**Solution:** Ensure backend is running:
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Authentication Failed (401)

**Problem:** `{"detail": "Invalid API key"}`

**Solution:** Check your API key:
1. Open backend logs: `docker-compose logs backend`
2. Verify API key hash in database
3. Use default key: `QDSvBytSu8Nhe4rpBd7uP-CiY2f-astYRxrTaT0AYM8`

### Job Timeout

**Problem:** Job doesn't complete within 60 seconds

**Solution:** Increase timeout:
```python
job = wait_for_completion(job_id, timeout=120)  # 2 minutes
```

### Quantum Solver Always Falls Back

**Problem:** Hybrid always uses classical

**Solution:** This is normal behavior if:
- Matrix eigenvalues too small/large
- Post-selection fails
- Qiskit simulation error

Check job details for `fallback_reason`.

## Next Steps

After running these examples:

1. **Explore the API** - Read `backend/README.md` for full API reference
2. **Customize Parameters** - Adjust grid size, thresholds, and factors
3. **Visualize Results** - Open job URLs in the frontend
4. **Check the Code** - Review solver implementations in `backend/services/`
5. **Run Tests** - Execute unit tests: `docker-compose exec backend pytest`

## Performance Benchmarks

Typical performance on standard hardware (Docker, 2GB RAM limit):

| Solver | Grid Size | Solve Time | Accuracy |
|--------|-----------|------------|----------|
| Classical | 50×50 (2500) | ~0.08s | Exact |
| Classical | 100×100 (10000) | ~0.3s | Exact |
| Quantum | 2×2 (demo) | ~0.3s | ±11% error |
| Hybrid | 50×50 (2500) | ~0.09s | Exact (classical) |

**Note:** Quantum solver performance limited by:
- Small submatrix size (2×2 demonstration)
- Qiskit statevector simulation overhead
- Post-selection success rate (~21.5%)

Real quantum advantage requires 20+ qubits and fault-tolerant quantum hardware.

## Questions?

- **Technical Issues**: Check `DOCKER_LOCAL_GUIDE.md`
- **Quantum Details**: See `QUANTUM_SOLVER_FIX.md`
- **API Reference**: Read `backend/README.md`
- **Contributing**: Open an issue on GitHub

---

**Happy Flood Simulating! 🌊**
