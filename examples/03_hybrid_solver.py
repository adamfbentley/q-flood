#!/usr/bin/env python3
"""
Example: Hybrid Quantum-Classical Solver
=========================================

This example demonstrates the hybrid solver which attempts quantum computation
first and falls back to classical methods if quantum fails.

Requirements:
- Backend running on localhost:8000
- API key configured
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

def submit_hybrid_job():
    """Submit a flood simulation job using the hybrid solver."""
    
    job_data = {
        "solver_type": "HYBRID",
        "parameters": {
            "grid_resolution": 50,
            "conversion_factor": 0.1,
            "flood_threshold": 0.05
        }
    }
    
    print("🔄 Submitting hybrid solver job...")
    print("   Strategy: Quantum first, classical fallback")
    print("   Quantum attempt: HHL algorithm (2x2 submatrix)")
    print("   Fallback: NumPy/SciPy sparse solvers")
    
    response = requests.post(
        f"{API_BASE_URL}/solve",
        json=job_data,
        headers={"X-API-Key": API_KEY}
    )
    
    if response.status_code != 202:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None
    
    job = response.json()
    job_id = job["id"]
    print(f"✅ Job submitted: {job_id}")
    
    return job_id

def wait_for_completion(job_id, timeout=60):
    """Poll the job status until completion."""
    
    print(f"\n⏳ Processing hybrid computation...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(
            f"{API_BASE_URL}/jobs/{job_id}",
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code != 200:
            print(f"❌ Error checking status: {response.status_code}")
            return None
        
        job = response.json()
        status = job["status"]
        
        print(f"   Status: {status}", end="\r")
        
        if status == "COMPLETED":
            print(f"\n✅ Hybrid computation complete!")
            return job
        elif status in ["FAILED", "CANCELLED"]:
            print(f"\n❌ Job {status.lower()}")
            return None
        
        time.sleep(2)
    
    print(f"\n⏱️  Timeout after {timeout}s")
    return None

def display_hybrid_results(job):
    """Display hybrid solver results showing which method was used."""
    
    print("\n📊 Hybrid Results:")
    print(f"   Job ID: {job['id']}")
    print(f"   Solver: {job['solver_type']}")
    print(f"   Status: {job['status']}")
    
    # Determine which solver was actually used
    used_quantum = False
    used_classical = False
    
    if job.get("solution_path"):
        if "quantum" in job["solution_path"]:
            used_quantum = True
        elif "classical" in job["solution_path"]:
            used_classical = True
    
    if job.get("fallback_reason"):
        used_classical = True
    
    print(f"\n🔍 Execution Path:")
    
    if used_quantum:
        print(f"   ✅ Quantum solver succeeded!")
        print(f"   Algorithm: HHL on 2x2 submatrix")
        print(f"   Path: {job['solution_path']}")
    elif used_classical:
        print(f"   ⚡ Classical fallback used")
        if job.get("fallback_reason"):
            print(f"   Reason: {job['fallback_reason']}")
        print(f"   Method: NumPy/SciPy sparse solvers")
        if job.get("solution_path"):
            print(f"   Path: {job['solution_path']}")
    else:
        print(f"   ℹ️  Unable to determine solver path")
    
    # Performance metrics
    if job.get("metrics"):
        metrics = job["metrics"]
        print(f"\n⚡ Performance:")
        if "solve_time" in metrics:
            print(f"   Solve time: {metrics['solve_time']:.4f}s")
        if "matrix_size" in metrics:
            print(f"   Matrix size: {metrics['matrix_size']}")
        if "non_zero_elements" in metrics:
            print(f"   Non-zero elements: {metrics['non_zero_elements']}")
    
    # Generated files
    print(f"\n📁 Generated Files:")
    if job.get("geojson_path"):
        print(f"   ✓ GeoJSON: {job['geojson_path'].split('/')[-1]}")
    if job.get("pdf_report_path"):
        print(f"   ✓ PDF Report: {job['pdf_report_path'].split('/')[-1]}")
    
    print(f"\n🌐 View flood map:")
    print(f"   http://localhost:5173/jobs/{job['id']}")
    
    print(f"\n💡 Hybrid Solver Benefits:")
    print(f"   • Attempts quantum computation for potential speedup")
    print(f"   • Automatically falls back to classical if quantum fails")
    print(f"   • Best of both worlds: exploration + reliability")
    print(f"   • Useful for testing quantum algorithms in production")

def main():
    """Run the hybrid solver example."""
    
    print("=" * 60)
    print("Hybrid Quantum-Classical Solver Example")
    print("=" * 60)
    
    # Submit job
    job_id = submit_hybrid_job()
    if not job_id:
        return
    
    # Wait for completion
    job = wait_for_completion(job_id)
    if not job:
        return
    
    # Display results
    display_hybrid_results(job)
    
    print("\n" + "=" * 60)
    print("✨ Hybrid solver example complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
