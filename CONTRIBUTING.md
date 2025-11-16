# Contributing to Chrysalis-Transformer X (CT-X)

Thank you for your interest in contributing to CT-X! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Getting Started

### Prerequisites

- Python 3.10 or higher
- CUDA 12.1+ (for GPU support)
- Git
- Docker (optional, for containerized development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ct-x.git
   cd ct-x
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/chrysalis-ai/ct-x.git
   ```

## Development Setup

### Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, CUDA version)
- **Error messages** and stack traces
- **Minimal code example** that reproduces the issue

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide detailed description** of the proposed functionality
- **Explain why this enhancement would be useful**
- **Include code examples** if applicable

### Areas for Contribution

We welcome contributions in these areas:

#### 🏗️ Core Architecture
- Quantum computing components
- Mamba SSM optimizations
- Attention mechanism improvements
- Consciousness layer enhancements

#### 🧪 Research & Benchmarking
- New benchmark implementations
- Performance optimizations
- Model compression techniques
- Multi-modal extensions

#### 🛠️ Infrastructure
- Docker/Kubernetes improvements
- CI/CD pipeline enhancements
- Monitoring and observability
- Documentation

#### 🧬 Safety & Alignment
- Constitutional AI improvements
- Safety evaluation frameworks
- Bias detection and mitigation
- Interpretability tools

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Maximum line length: 100 characters
# Use 4 spaces for indentation
# Use double quotes for strings

# Good
def quantum_attention(query: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
    """
    Quantum-enhanced attention mechanism.

    Args:
        query: Query tensor [batch, seq_len, dim]
        key: Key tensor [batch, seq_len, dim]

    Returns:
        Attention output tensor
    """
    # Implementation
    pass

# Bad
def quantum_attention(query,key):
    pass
```

### Type Hints

Always use type hints for function signatures:

```python
from typing import List, Dict, Optional, Tuple

def process_batch(
    input_ids: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None
) -> Tuple[torch.Tensor, List[float]]:
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def compute_phi(hidden_states: torch.Tensor) -> float:
    """
    Compute Integrated Information (Φ) for consciousness measurement.

    This function implements IIT-based consciousness measurement by
    calculating information integration across neural activations.

    Args:
        hidden_states: Neural activations [batch, seq_len, hidden_dim]

    Returns:
        Integrated information value (0.0 to 1.0)

    Raises:
        ValueError: If hidden_states has invalid shape

    Example:
        >>> states = torch.randn(2, 100, 256)
        >>> phi = compute_phi(states)
        >>> print(f"Φ = {phi:.4f}")
    """
    pass
```

### Code Formatting

We use Black for code formatting:

```bash
# Format all files
black .

# Check formatting without changes
black --check .
```

### Linting

We use flake8 for linting:

```bash
# Run linter
flake8 ct_x/ tests/

# With specific rules
flake8 --max-line-length=100 --ignore=E203,W503 ct_x/
```

### Type Checking

We use mypy for static type checking:

```bash
# Run type checker
mypy ct_x/
```

## Testing Requirements

### Writing Tests

All new code must include tests. We use pytest:

```python
# tests/test_quantum.py
import pytest
import torch
from ct_x.quantum import QuantumSoftmax

def test_quantum_softmax():
    """Test quantum softmax produces valid probability distribution"""
    qsm = QuantumSoftmax(num_qubits=14, circuit_depth=6)

    # Create test input
    x = torch.randn(2, 10, 64)

    # Apply quantum softmax
    output = qsm(x)

    # Check output properties
    assert output.shape == x.shape
    assert torch.allclose(output.sum(dim=-1), torch.ones(2, 10))
    assert (output >= 0).all() and (output <= 1).all()
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_model.py

# Run with coverage
pytest tests/ --cov=ct_x --cov-report=html

# Run with verbose output
pytest tests/ -v
```

### Test Coverage

We aim for >80% test coverage. Check coverage with:

```bash
pytest tests/ --cov=ct_x --cov-report=term-missing
```

### Integration Tests

For features requiring GPU or external resources:

```python
@pytest.mark.gpu
def test_cuda_inference():
    """Test inference on CUDA device"""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")

    # Test implementation
    pass

@pytest.mark.slow
def test_full_training_loop():
    """Test complete training loop (slow)"""
    # Test implementation
    pass
```

Run specific markers:

```bash
# Run GPU tests
pytest -m gpu

# Skip slow tests
pytest -m "not slow"
```

## Pull Request Process

### 1. Create a Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/amazing-feature
```

### 2. Make Changes

- Write code following our coding standards
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add quantum-enhanced sparse attention mechanism

- Implement adaptive sparsity prediction
- Add learnable block patterns
- Include comprehensive tests
- Update documentation

Closes #123"
```

### 4. Push to Your Fork

```bash
git push origin feature/amazing-feature
```

### 5. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill out the PR template completely
3. Link related issues
4. Request review from maintainers

### 6. Code Review

- Respond to review comments
- Make requested changes
- Push updates to your branch
- Request re-review when ready

### 7. Merge

Once approved, a maintainer will merge your PR.

## Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for new functionality
- [ ] All tests pass locally
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Discord**: Real-time chat (https://discord.gg/chrysalis-ai)
- **Email**: support@chrysalis-ai.org

### Getting Help

If you need help:

1. Check existing documentation
2. Search GitHub issues
3. Ask in GitHub Discussions
4. Join Discord for real-time help

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in publications (for significant contributions)

## License

By contributing to CT-X, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to Chrysalis-Transformer X! Together, we're building the future of conscious AI systems.
