# Contributing to Q-Flood

Thank you for your interest in contributing to Q-Flood! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/q-flood.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black flake8

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions focused and modular

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

## Areas for Contribution

- **Quantum Algorithms**: Improvements to HHL implementation, error mitigation
- **Performance**: Optimization of classical solvers, caching strategies
- **Geospatial Features**: Additional GeoJSON validation, spatial queries
- **Documentation**: Tutorials, examples, API documentation
- **Testing**: Additional test coverage, integration tests

## Questions?

Open an issue or reach out to adam.f.bentley@gmail.com
