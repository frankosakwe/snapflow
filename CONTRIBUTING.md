# Contributing to SnapFlow

Thank you for your interest in contributing to SnapFlow! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/snapflow.git
   cd snapflow
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   make dev-install
   # or
   pip install -e ".[dev]"
   pip install -r requirements-dev.txt
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure they follow our coding standards

3. **Run tests**:
   ```bash
   make test
   # or
   pytest
   ```

4. **Check code quality**:
   ```bash
   make lint
   # or
   flake8 snapflow tests
   mypy snapflow
   ```

5. **Format your code**:
   ```bash
   make format
   # or
   black snapflow tests
   isort snapflow tests
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use Black for code formatting (line length: 100)
- Use isort for import sorting
- Use type hints where appropriate
- Write comprehensive docstrings

### Testing
- Write tests for all new features
- Maintain or improve code coverage
- Use pytest for testing
- Follow AAA pattern (Arrange, Act, Assert)

### Documentation
- Update README.md if adding user-facing features
- Add docstrings to all public functions and classes
- Update CHANGELOG.md following Keep a Changelog format

## Commit Message Guidelines

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat: add support for SQLite databases`

## Pull Request Process

1. Ensure all tests pass
2. Update documentation as needed
3. Add your changes to CHANGELOG.md
4. Request review from maintainers
5. Address any feedback
6. Once approved, your PR will be merged

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=snapflow

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::TestSnapshot::test_snapshot_creation
```

## Code Review Checklist

- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Code formatted with Black and isort
- [ ] Type hints added where appropriate
- [ ] No linting errors
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow conventions

## Reporting Issues

When reporting issues, please include:

- SnapFlow version
- Python version
- Operating system
- Database type and version
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

## Questions?

Feel free to open an issue for questions or join our discussions on GitHub.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
