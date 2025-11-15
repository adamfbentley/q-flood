#!/usr/bin/env python3
"""
Example: Compare All Solver Types
==================================

This example runs all three solver types (CLASSICAL, QUANTUM, HYBRID) and
compares their performance, accuracy, and characteristics side-by-side.

Requirements:
- Backend running on localhost:8000
- API key configured
"""

import requests
import json
import time
from typing import Dict, Optional

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

def submit_job(solver_type: str) -> Optional[str]:
    """Submit a flood simulation job with specified solver type."""
    
    job_data = {
        "solver_type": solver_type,
        "parameters": {
            "grid_resolution": 50,
            "conversion_factor": 0.1,
            "flood_threshold": 0.05
        }
    }
    
    print(f"📤 Submitting {solver_type} job...")
    
    response = requests.post(
        f"{API_BASE_URL}/solve",
        json=job_data,
        headers={"X-API-Key": API_KEY}
    )
    
    if response.status_code != 202:
        print(f"❌ Error: {response.status_code}")
        return None
    
    job = response.json()
    job_id = job["id"]
    print(f"✅ Job submitted: {job_id}")
    
    return job_id

def wait_for_completion(job_id: str, solver_type: str, timeout: int = 60) -> Optional[Dict]:
    """Poll the job status until completion."""
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(
            f"{API_BASE_URL}/jobs/{job_id}",
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code != 200:
            return None
        
        job = response.json()
        status = job["status"]
        
        if status == "COMPLETED":
            elapsed = time.time() - start_time
            print(f"✅ {solver_type} completed in {elapsed:.2f}s")
            return job
        elif status in ["FAILED", "CANCELLED"]:
            print(f"❌ {solver_type} {status.lower()}")
            return None
        
        time.sleep(2)
    
    print(f"⏱️  {solver_type} timeout")
    return None

def extract_metrics(job: Dict) -> Dict:
    """Extract relevant metrics from job result."""
    
    metrics = {
        "job_id": job["id"],
        "solver_type": job["solver_type"],
        "status": job["status"],
        "solve_time": None,
        "matrix_size": None,
        "non_zero_elements": None,
        "used_solver": "unknown"
    }
    
    if job.get("metrics"):
        job_metrics = job["metrics"]
        metrics["solve_time"] = job_metrics.get("solve_time")
        metrics["matrix_size"] = job_metrics.get("matrix_size")
        metrics["non_zero_elements"] = job_metrics.get("non_zero_elements")
    
    # Determine which solver was actually used
    if job.get("solution_path"):
        if "quantum" in job["solution_path"]:
            metrics["used_solver"] = "quantum"
        elif "classical" in job["solution_path"]:
            metrics["used_solver"] = "classical"
    
    if job.get("fallback_reason"):
        metrics["fallback_reason"] = job["fallback_reason"]
    
    return metrics

def display_comparison(results: Dict[str, Dict]):
    """Display side-by-side comparison of all solver results."""
    
    print("\n" + "=" * 80)
    print("SOLVER COMPARISON")
    print("=" * 80)
    
    # Header
    print(f"\n{'Metric':<25} {'CLASSICAL':<20} {'QUANTUM':<20} {'HYBRID':<20}")
    print("-" * 80)
    
    # Solver types
    solvers = ["CLASSICAL", "QUANTUM", "HYBRID"]
    
    # Solve Time
    print(f"{'Solve Time (s)':<25}", end="")
    for solver in solvers:
        if solver in results and results[solver].get("solve_time"):
            print(f"{results[solver]['solve_time']:<20.4f}", end="")
        else:
            print(f"{'N/A':<20}", end="")
    print()
    
    # Matrix Size
    print(f"{'Matrix Size':<25}", end="")
    for solver in solvers:
        if solver in results and results[solver].get("matrix_size"):
            print(f"{results[solver]['matrix_size']:<20}", end="")
        else:
            print(f"{'N/A':<20}", end="")
    print()
    
    # Non-zero Elements
    print(f"{'Non-zero Elements':<25}", end="")
    for solver in solvers:
        if solver in results and results[solver].get("non_zero_elements"):
            print(f"{results[solver]['non_zero_elements']:<20}", end="")
        else:
            print(f"{'N/A':<20}", end="")
    print()
    
    # Actually Used Solver
    print(f"{'Actually Used':<25}", end="")
    for solver in solvers:
        if solver in results:
            used = results[solver].get("used_solver", "unknown")
            print(f"{used:<20}", end="")
        else:
            print(f"{'N/A':<20}", end="")
    print()
    
    # Fallback Reason
    print(f"{'Fallback Reason':<25}", end="")
    for solver in solvers:
        if solver in results and "fallback_reason" in results[solver]:
            reason = results[solver]["fallback_reason"]
            reason_short = reason[:18] + "..." if len(reason) > 18 else reason
            print(f"{reason_short:<20}", end="")
        else:
            print(f"{'-':<20}", end="")
    print()
    
    print("-" * 80)
    
    # Analysis
    print(f"\n📊 Analysis:")
    
    # Speed comparison
    if all(s in results and results[s].get("solve_time") for s in ["CLASSICAL", "QUANTUM"]):
        classical_time = results["CLASSICAL"]["solve_time"]
        quantum_time = results["QUANTUM"]["solve_time"]
        
        if classical_time < quantum_time:
            speedup = quantum_time / classical_time
            print(f"   • Classical is {speedup:.2f}x faster than quantum")
            print(f"     (Expected: quantum overhead for small 2x2 submatrix)")
        else:
            speedup = classical_time / quantum_time
            print(f"   • Quantum is {speedup:.2f}x faster than classical")
    
    # Quantum accuracy note
    if "QUANTUM" in results and results["QUANTUM"].get("used_solver") == "quantum":
        print(f"   • Quantum solution has ~11% error vs classical (HHL limitation)")
    
    # Hybrid behavior
    if "HYBRID" in results:
        hybrid = results["HYBRID"]
        if hybrid.get("used_solver") == "quantum":
            print(f"   • Hybrid used quantum solver successfully")
        elif hybrid.get("used_solver") == "classical":
            print(f"   • Hybrid fell back to classical solver")
            if "fallback_reason" in hybrid:
                print(f"     Reason: {hybrid['fallback_reason']}")
    
    # Job URLs
    print(f"\n🌐 View Results:")
    for solver in solvers:
        if solver in results:
            job_id = results[solver]["job_id"]
            print(f"   {solver}: http://localhost:5173/jobs/{job_id}")
    
    print(f"\n💡 Key Takeaways:")
    print(f"   • Classical: Fast and accurate for production use")
    print(f"   • Quantum: Demonstrates HHL algorithm (limited to 2x2 currently)")
    print(f"   • Hybrid: Best for testing quantum with reliability fallback")
    print(f"   • Future: Quantum advantage needs 20+ qubits for larger systems")

def main():
    """Run all solvers and compare results."""
    
    print("=" * 80)
    print("COMPARE ALL SOLVER TYPES")
    print("=" * 80)
    print("\nThis will run CLASSICAL, QUANTUM, and HYBRID solvers sequentially.")
    print("Total estimated time: ~6-10 seconds\n")
    
    solvers = ["CLASSICAL", "QUANTUM", "HYBRID"]
    results = {}
    
    # Run each solver
    for solver_type in solvers:
        print(f"\n{'─' * 80}")
        print(f"Running {solver_type} solver...")
        print(f"{'─' * 80}")
        
        # Submit job
        job_id = submit_job(solver_type)
        if not job_id:
            print(f"⚠️  Skipping {solver_type} due to submission error")
            continue
        
        # Wait for completion
        job = wait_for_completion(job_id, solver_type)
        if not job:
            print(f"⚠️  {solver_type} did not complete successfully")
            continue
        
        # Extract metrics
        metrics = extract_metrics(job)
        results[solver_type] = metrics
        
        time.sleep(1)  # Brief pause between jobs
    
    # Display comparison
    if results:
        display_comparison(results)
    else:
        print("\n❌ No results to compare")
    
    print("\n" + "=" * 80)
    print("✨ Comparison complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
