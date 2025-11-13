"""
Tests for quantum solver implementation
"""
import pytest
from app.services.quantum_solver import QuantumSolver


def test_quantum_solver_initialization():
    """Test quantum solver can be initialized with valid parameters"""
    solver = QuantumSolver(n_qubits=3)
    assert solver.n_qubits == 3
    assert solver.backend is not None


def test_quantum_circuit_creation():
    """Test quantum circuit is created with correct structure"""
    solver = QuantumSolver(n_qubits=3)
    circuit = solver.create_hhl_circuit([1.0, 0.0], [[2.0, 0.0], [0.0, 2.0]])
    
    assert circuit is not None
    assert circuit.num_qubits == 3


def test_fallback_to_classical():
    """Test system falls back to classical when quantum fails"""
    solver = QuantumSolver(n_qubits=3, enable_fallback=True)
    
    # Test with invalid input that should trigger fallback
    result = solver.solve(matrix=None, vector=[1.0, 2.0])
    assert result['solver_type'] == 'classical'
    assert 'fallback_reason' in result


@pytest.mark.integration
def test_full_quantum_solve():
    """Integration test for complete quantum solve process"""
    solver = QuantumSolver(n_qubits=3, shots=1000)
    
    # Simple 2x2 system
    A = [[2.0, 0.0], [0.0, 2.0]]
    b = [1.0, 1.0]
    
    result = solver.solve(matrix=A, vector=b)
    
    assert 'solution' in result
    assert 'execution_time' in result
    assert result['solver_type'] in ['quantum', 'classical']
