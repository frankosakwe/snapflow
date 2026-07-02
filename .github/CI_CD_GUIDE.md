# CI/CD Pipeline Guide

This document describes the comprehensive CI/CD pipeline for SnapFlow.

## 🔄 Workflows Overview

### 1. Main CI/CD Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Weekly schedule (Mondays at 00:00 UTC)
- Tagged releases (`v*`)

**Jobs:**

#### a. Code Quality
- **Black** formatting check
- **isort** import sorting check
- **Flake8** linting
- **MyPy** type checking
- **Pylint** advanced linting
- **Bandit** security scanning
- **Safety** dependency vulnerability check

#### b. Tests
- Runs on Ubuntu, Windows, and macOS
- Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
- Code coverage reporting to Codecov
- Uploads test results as artifacts

#### c. Build
- Builds source and wheel distributions
- Validates package with `twine check`
- Uploads artifacts for release

#### d. Documentation
- Validates README rendering
- Checks markdown links

#### e. Security Audit
- Trivy vulnerability scanner
- Uploads results to GitHub Security

#### f. Release (on tags only)
- Publishes to PyPI
- Creates GitHub release with notes

#### g. Performance Benchmarking
- Runs on pull requests
- Executes performance tests

#### h. Notification
- Reports overall build status

---

### 2. Pull Request Checks (`pr-checks.yml`)

**Triggers:**
- Pull request opened/updated

**Jobs:**
- **PR Info**: Displays PR metadata
- **Size Label**: Auto-labels PR by size (XS/S/M/L/XL)
- **Title Check**: Validates semantic PR titles
- **Conflict Check**: Detects merge conflicts
- **Changes Detection**: Identifies changed file types
- **Quick Test**: Fast test on Python 3.11
- **Coverage Comment**: Posts coverage report as PR comment

---

### 3. Dependency Updates (`dependency-update.yml`)

**Triggers:**
- Weekly schedule (Mondays at 09:00 UTC)
- Manual trigger

**Jobs:**
- Updates Python dependencies with `pip-tools`
- Creates automated PR with changes

---

### 4. Release Workflow (`release.yml`)

**Triggers:**
- Push tags matching `v*.*.*`

**Jobs:**
- Builds package
- Publishes to Test PyPI (optional)
- Publishes to PyPI
- Creates GitHub release
- Generates release notes

---

### 5. Stale Issues/PRs (`stale.yml`)

**Triggers:**
- Daily schedule (00:00 UTC)
- Manual trigger

**Jobs:**
- Marks issues stale after 60 days
- Marks PRs stale after 30 days
- Closes stale items after 7 days
- Exempts labeled issues (bug, enhancement, etc.)

---

### 6. CodeQL Security (`codeql.yml`)

**Triggers:**
- Push to main/develop
- Pull requests
- Weekly schedule (Wednesdays at 06:00 UTC)

**Jobs:**
- Analyzes Python code for security issues
- Uploads findings to GitHub Security tab

---

## 🔐 Required Secrets

Configure these secrets in GitHub repository settings:

| Secret | Purpose | Required For |
|--------|---------|--------------|
| `PYPI_API_TOKEN` | PyPI publishing | Release workflow |
| `TEST_PYPI_API_TOKEN` | Test PyPI publishing | Release workflow (optional) |
| `CODECOV_TOKEN` | Code coverage reporting | CI workflow (optional) |

---

## 🏷️ Semantic Commit Messages

The project follows semantic commit conventions:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test changes
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Other changes

**Examples:**
```
feat(cli): Add progress bar to snapshot command
fix(app): Handle database connection timeout
docs(readme): Update installation instructions
ci(workflow): Add security scanning
```

---

## 📊 Status Badges

Add these badges to your README:

```markdown
[![CI](https://github.com/frankosakwe/snapflow/actions/workflows/ci.yml/badge.svg)](https://github.com/frankosakwe/snapflow/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/frankosakwe/snapflow/branch/main/graph/badge.svg)](https://codecov.io/gh/frankosakwe/snapflow)
[![CodeQL](https://github.com/frankosakwe/snapflow/actions/workflows/codeql.yml/badge.svg)](https://github.com/frankosakwe/snapflow/actions/workflows/codeql.yml)
```

---

## 🚀 Release Process

### Creating a New Release

1. **Update version:**
   ```bash
   # Update version in snapflow/app.py
   __version__ = '1.1.0'
   ```

2. **Update CHANGELOG.md:**
   ```markdown
   ## [1.1.0] - 2026-07-02
   ### Added
   - New feature X
   ### Fixed
   - Bug Y
   ```

3. **Commit changes:**
   ```bash
   git add .
   git commit -m "chore: Bump version to 1.1.0"
   git push
   ```

4. **Create and push tag:**
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

5. **Automated actions:**
   - CI runs all tests
   - Package is built
   - Published to PyPI
   - GitHub release is created
   - Release notes are generated

---

## 🧪 Running CI Checks Locally

### Code Quality

```bash
# Format check
black --check snapflow tests

# Import sorting
isort --check-only --profile black snapflow tests

# Linting
flake8 snapflow tests --max-line-length=100 --extend-ignore=E203,W503

# Type checking
mypy snapflow --ignore-missing-imports

# Security scan
bandit -r snapflow

# Dependency check
safety check
```

### Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=snapflow --cov-report=html

# Specific test file
pytest tests/test_config.py -v

# Fast fail
pytest --maxfail=3
```

### Build

```bash
# Build package
python -m build

# Check distribution
twine check dist/*
```

---

## 🔧 Troubleshooting

### CI Failures

#### Tests Failing
1. Check test logs in GitHub Actions
2. Run tests locally: `pytest -v`
3. Check for environment-specific issues

#### Linting Failures
1. Run formatters locally:
   ```bash
   black snapflow tests
   isort --profile black snapflow tests
   ```
2. Fix flake8 issues
3. Commit and push

#### Build Failures
1. Check setup.py configuration
2. Verify dependencies in requirements.txt
3. Test build locally: `python -m build`

### Common Issues

**Issue**: Codecov upload fails
- **Solution**: Add `CODECOV_TOKEN` secret

**Issue**: PyPI publish fails
- **Solution**: Add `PYPI_API_TOKEN` secret

**Issue**: Tests timeout
- **Solution**: Increase timeout in pytest.ini

---

## 📈 Monitoring

### GitHub Actions Dashboard
- View workflow runs: `https://github.com/frankosakwe/snapflow/actions`
- Check specific workflow
- Download artifacts

### Code Coverage
- View on Codecov: `https://codecov.io/gh/frankosakwe/snapflow`

### Security
- Check Security tab in GitHub
- Review Dependabot alerts
- Monitor CodeQL results

---

## 🎯 Best Practices

1. **Always run local checks before pushing**
2. **Write meaningful commit messages**
3. **Keep PRs focused and small**
4. **Update tests with code changes**
5. **Document breaking changes**
6. **Review CI failures promptly**
7. **Keep dependencies updated**
8. **Monitor security alerts**

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Last Updated**: 2026-07-02
**SnapFlow Version**: 1.0.0
