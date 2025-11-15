#!/usr/bin/env python3
"""
Example: Quantum Flood Solver (HHL Algorithm)
==============================================

This example demonstrates the quantum solver using Qiskit's HHL algorithm.
The quantum solver operates on a 2x2 submatrix extracted from the full system.

Requirements:
- Backend running on localhost:8000
- API key configured
- Qiskit and qiskit-aer installed in backend
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

def submit_quantum_job():
    """Submit a flood simulation job using the quantum solver."""
    
    job_data = {
        "solver_type": "QUANTUM",
        "parameters": {
            "grid_resolution": 50,
            "conversion_factor": 0.1,
            "flood_threshold": 0.05
        }
    }
    
    print("🔮 Submitting quantum solver job...")
    print("   Algorithm: HHL (Harrow-Hassidim-Lloyd)")
    print("   Qubits: 4 (1 ancilla, 2 eigenvalue, 1 state)")
    print("   Matrix size: 2x2 (extracted from 50x50 grid)")
    
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
    
    print(f"\n⏳ Waiting for quantum computation...")
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
            print(f"\n✅ Quantum computation complete!")
            return job
        elif status in ["FAILED", "CANCELLED"]:
            print(f"\n❌ Job {status.lower()}")
            if job.get("fallback_reason"):
                print(f"   Reason: {job['fallback_reason']}")
            return None
        
        time.sleep(2)
    
    print(f"\n⏱️  Timeout after {timeout}s")
    return None

def display_quantum_results(job):
    """Display quantum solver results with technical details."""
    
    print("\n📊 Quantum Results:")
    print(f"   Job ID: {job['id']}")
    print(f"   Solver: {job['solver_type']}")
    print(f"   Status: {job['status']}")
    
    # Solution path indicates quantum
    if job.get("solution_path") and "quantum" in job["solution_path"]:
        print(f"\n🎯 Quantum Solution Generated:")
        print(f"   Path: {job['solution_path']}")
    
    print(f"\n🔬 Quantum Technical Details:")
    print(f"   Algorithm: HHL (Quantum Linear System Solver)")
    print(f"   Circuit Components:")
    print(f"     • State Preparation (RY gate)")
    print(f"     • Quantum Phase Estimation")
    print(f"     • Controlled Rotations (eigenvalue inversion)")
    print(f"     • Inverse QFT")
    print(f"     • Post-selection on ancilla")
    print(f"   Simulator: AerSimulator (statevector method)")
    print(f"   Shots: 1000")
    
    # Generated files
    print(f"\n📁 Generated Files:")
    if job.get("geojson_path"):
        print(f"   ✓ GeoJSON: {job['geojson_path'].split('/')[-1]}")
    if job.get("pdf_report_path"):
        print(f"   ✓ PDF Report: {job['pdf_report_path'].split('/')[-1]}")
    
    print(f"\n🌐 View quantum flood map:")
    print(f"   http://localhost:5173/jobs/{job['id']}")
    
    print(f"\n💡 Note:")
    print(f"   The quantum solver operates on a 2x2 submatrix for demonstration.")
    print(f"   Real quantum advantage requires 20+ qubits for larger systems.")
    print(f"   Current implementation: ~11% error vs classical solution.")

def main():
    """Run the quantum solver example."""
    
    print("=" * 60)
    print("Quantum Flood Solver Example (HHL Algorithm)")
    print("=" * 60)
    
    # Submit job
    job_id = submit_quantum_job()
    if not job_id:
        return
    
    # Wait for completion
    job = wait_for_completion(job_id)
    if not job:
        return
    
    # Display results
    display_quantum_results(job)
    
    print("\n" + "=" * 60)
    print("✨ Quantum solver example complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
