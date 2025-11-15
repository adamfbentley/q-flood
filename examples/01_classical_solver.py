#!/usr/bin/env python3
"""
Example: Classical Flood Solver
================================

This example demonstrates submitting a job using the classical solver,
which uses NumPy/SciPy sparse matrix solvers for fast, accurate results.

Requirements:
- Backend running on localhost:8000
- API key configured (see README.md)
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

def submit_classical_job():
    """Submit a flood simulation job using the classical solver."""
    
    # Job configuration
    job_data = {
        "solver_type": "CLASSICAL",
        "parameters": {
            "grid_resolution": 50,      # 50x50 grid = 2500 cells
            "conversion_factor": 0.1,   # Converts solution to meters
            "flood_threshold": 0.05     # 5cm threshold for "flooded"
        }
    }
    
    # Submit the job
    print("🚀 Submitting classical solver job...")
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
    print(f"   Status: {job['status']}")
    
    return job_id

def wait_for_completion(job_id, timeout=60):
    """Poll the job status until completion or timeout."""
    
    print(f"\n⏳ Waiting for job to complete...")
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
            print(f"\n✅ Job completed!")
            return job
        elif status in ["FAILED", "CANCELLED"]:
            print(f"\n❌ Job {status.lower()}")
            if job.get("fallback_reason"):
                print(f"   Reason: {job['fallback_reason']}")
            return None
        
        time.sleep(2)
    
    print(f"\n⏱️  Timeout after {timeout}s")
    return None

def display_results(job):
    """Display job results and statistics."""
    
    print("\n📊 Results:")
    print(f"   Job ID: {job['id']}")
    print(f"   Solver: {job['solver_type']}")
    print(f"   Status: {job['status']}")
    
    # Performance metrics
    if job.get("latest_performance_metrics"):
        metrics = job["latest_performance_metrics"]
        print(f"\n⚡ Performance:")
        print(f"   Execution time: {metrics['execution_time_seconds']:.3f}s")
        print(f"   CPU utilization: {metrics['cpu_utilization_percent']:.1f}%")
    
    # Generated files
    print(f"\n📁 Generated Files:")
    if job.get("matrix_path"):
        print(f"   ✓ Matrix: {job['matrix_path'].split('/')[-1]}")
    if job.get("solution_path"):
        print(f"   ✓ Solution: {job['solution_path'].split('/')[-1]}")
    if job.get("geojson_path"):
        print(f"   ✓ GeoJSON: {job['geojson_path'].split('/')[-1]}")
    if job.get("pdf_report_path"):
        print(f"   ✓ PDF Report: {job['pdf_report_path'].split('/')[-1]}")
    
    print(f"\n🌐 View results:")
    print(f"   http://localhost:5173/jobs/{job['id']}")

def main():
    """Run the classical solver example."""
    
    print("=" * 60)
    print("Classical Flood Solver Example")
    print("=" * 60)
    
    # Submit job
    job_id = submit_classical_job()
    if not job_id:
        return
    
    # Wait for completion
    job = wait_for_completion(job_id)
    if not job:
        return
    
    # Display results
    display_results(job)
    
    print("\n" + "=" * 60)
    print("✨ Classical solver example complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
