# Example Outputs

This directory contains sample outputs from running the example scripts. These demonstrate what you can expect when running the Q-Flood API locally.

## Files

### `classical_output.txt`
Expected console output from running `01_classical_solver.py`:
- Job submission and ID
- Status polling updates
- Performance metrics (solve time ~0.08s)
- Generated file paths
- Frontend URL for visualization

### `quantum_output.txt`
Expected console output from running `02_quantum_solver.py`:
- Quantum algorithm details (HHL, 4-qubit circuit)
- Job processing status
- Quantum technical information
- Note about 2x2 submatrix limitation
- ~11% error vs classical mention

### `comparison_output.txt`
Expected console output from running `04_compare_solvers.py`:
- Sequential execution of all three solver types
- Side-by-side performance comparison table
- Analysis showing classical is ~3.57x faster (for small matrices)
- All job URLs for visualization
- Key takeaways about each solver

## Notes

- **Job IDs**: The UUIDs shown are examples. Your actual job IDs will be different.
- **Timing**: Solve times may vary based on system performance.
- **Quantum Performance**: Classical is faster for small matrices due to quantum overhead. Quantum advantage requires 20+ qubits and larger systems.
- **Frontend URLs**: Replace localhost with your actual frontend URL if different.

## Using These Examples

When showcasing Q-Flood:

1. **For Recruiters**: Show `comparison_output.txt` to demonstrate all three solver types working
2. **For Technical Audiences**: Show `quantum_output.txt` to highlight quantum implementation details
3. **For Performance**: Show `classical_output.txt` to demonstrate production-ready speed

## Real Output

To generate your own outputs, run:

```bash
# Classical solver
python examples/01_classical_solver.py > my_classical_output.txt

# Quantum solver  
python examples/02_quantum_solver.py > my_quantum_output.txt

# Compare all
python examples/04_compare_solvers.py > my_comparison_output.txt
```

These sample outputs help set expectations and provide a reference for troubleshooting.
