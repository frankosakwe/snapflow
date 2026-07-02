# SnapFlow Release Guide

Guide for maintainers on how to release new versions of SnapFlow.

## Pre-Release Checklist

### 1. Code Quality
- [ ] All tests passing (`pytest`)
- [ ] Code coverage ≥ 90% (`pytest --cov`)
- [ ] No linting errors (`make lint`)
- [ ] Code formatted (`make format`)
- [ ] Type checking passed (`mypy snapflow`)

### 2. Documentation
- [ ] README.md updated
- [ ] CHANGELOG.md updated with version changes
- [ ] Version number updated in `snapflow/app.py`
- [ ] Version number updated in `setup.py`
- [ ] All docstrings up to date
- [ ] Examples tested and working

### 3. Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Demo workflow tested
- [ ] Installation verified on all platforms

### 4. Version Control
- [ ] All changes committed
- [ ] Branch up to date with main
- [ ] No uncommitted changes

## Release Process

### Step 1: Update Version

Update version in multiple files:

**snapflow/app.py**:
```python
__version__ = '1.1.0'  # Update version
```

**setup.py**:
Version is read from `app.py`, so no change needed.

### Step 2: Update CHANGELOG.md

```markdown
## [1.1.0] - 2026-XX-XX

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Bug fix 1

### Deprecated
- Deprecated feature

### Removed
- Removed feature

### Security
- Security fix
```

### Step 3: Commit Version Changes

```bash
git add snapflow/app.py CHANGELOG.md
git commit -m "chore: bump version to 1.1.0"
git push origin main
```

### Step 4: Create Git Tag

```bash
# Create annotated tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push tag
git push origin v1.1.0
```

### Step 5: Build Distribution

```bash
# Clean previous builds
make clean

# Build distribution packages
python setup.py sdist bdist_wheel

# Verify packages
ls -lh dist/
```

Expected output:
```
dist/
├── snapflow-1.1.0-py3-none-any.whl
└── snapflow-1.1.0.tar.gz
```

### Step 6: Test Package Locally

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from built package
pip install dist/snapflow-1.1.0-py3-none-any.whl

# Verify installation
python -c "import snapflow; print(snapflow.__version__)"
snapflow --version

# Run verification script
python scripts/verify_installation.py

# Clean up
deactivate
rm -rf test_env
```

### Step 7: Upload to TestPyPI

```bash
# Install twine if needed
pip install twine

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Username: __token__
# Password: [Your TestPyPI token]
```

### Step 8: Test from TestPyPI

```bash
# Create test environment
python -m venv test_testpypi
source test_testpypi/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps snapflow
pip install -r requirements.txt

# Test installation
python -c "import snapflow; print(snapflow.__version__)"

# Clean up
deactivate
rm -rf test_testpypi
```

### Step 9: Upload to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Username: __token__
# Password: [Your PyPI token]
```

### Step 10: Verify PyPI Release

```bash
# Wait a few minutes for PyPI to update

# Test installation from PyPI
python -m venv test_pypi
source test_pypi/bin/activate
pip install snapflow==1.1.0
python -c "import snapflow; print(snapflow.__version__)"
deactivate
rm -rf test_pypi
```

### Step 11: Create GitHub Release

1. Go to: https://github.com/quantumdb/snapflow/releases/new
2. Tag version: `v1.1.0`
3. Release title: `SnapFlow v1.1.0`
4. Description: Copy relevant section from CHANGELOG.md
5. Attach dist files (optional)
6. Mark as pre-release (if applicable)
7. Publish release

Example release notes:

```markdown
# SnapFlow v1.1.0

## 🎉 What's New

- Feature 1: Description
- Feature 2: Description

## 🐛 Bug Fixes

- Fixed bug 1
- Fixed bug 2

## 📚 Documentation

- Improved README
- Added new examples

## 🔧 Technical Improvements

- Better error handling
- Performance improvements

## 📦 Installation

```bash
pip install --upgrade snapflow
```

## 📖 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.
```

### Step 12: Post-Release

1. Announce release:
   - [ ] GitHub Discussions
   - [ ] Twitter/Social media
   - [ ] Mailing list (if any)
   - [ ] Reddit (r/Python)

2. Update documentation:
   - [ ] Update version in README badges
   - [ ] Update examples if needed
   - [ ] Update installation instructions

3. Monitor:
   - [ ] Check PyPI download stats
   - [ ] Monitor GitHub issues
   - [ ] Respond to feedback

## Hotfix Release Process

For urgent bug fixes between regular releases:

1. Create hotfix branch:
   ```bash
   git checkout -b hotfix/1.0.1 v1.0.0
   ```

2. Fix the bug and commit:
   ```bash
   git commit -m "fix: critical bug description"
   ```

3. Update version to 1.0.1

4. Follow normal release process

5. Merge hotfix back to main:
   ```bash
   git checkout main
   git merge hotfix/1.0.1
   git push origin main
   ```

## Version Numbering

SnapFlow uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality, backwards compatible
- **PATCH** version: Bug fixes, backwards compatible

Examples:
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.0` → `1.1.0`: New feature
- `1.0.0` → `2.0.0`: Breaking change

## Release Schedule

- **Major releases**: When significant breaking changes are ready
- **Minor releases**: Monthly or when new features are complete
- **Patch releases**: As needed for bug fixes

## Release Automation (Future)

Consider automating releases with GitHub Actions:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build
        run: |
          pip install build twine
          python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

## Troubleshooting

### Issue: Upload to PyPI fails

**Solution**:
```bash
# Check package with twine
twine check dist/*

# Ensure you have correct credentials
cat ~/.pypirc
```

### Issue: Version conflict

**Solution**:
```bash
# Delete existing version from dist/
rm -rf dist/

# Rebuild
python setup.py sdist bdist_wheel
```

### Issue: Git tag already exists

**Solution**:
```bash
# Delete local tag
git tag -d v1.1.0

# Delete remote tag
git push origin :refs/tags/v1.1.0

# Recreate tag
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

## Security Releases

For security issues:

1. **DO NOT** disclose publicly until fixed
2. Create private fix
3. Coordinate disclosure with reporters
4. Release patch ASAP
5. Announce with security advisory
6. Update SECURITY.md

## Rollback Process

If a release has critical issues:

1. **Yank the release** from PyPI:
   - Log into PyPI
   - Go to release page
   - Click "Options" → "Yank"

2. **Delete GitHub release** (or mark as pre-release)

3. **Communicate**: Post issue explaining situation

4. **Fix and re-release**: Follow hotfix process

## Checklist Summary

Quick checklist for releases:

```bash
# Pre-release
make test && make lint && make format
git status  # Ensure clean

# Version bump
vim snapflow/app.py  # Update __version__
vim CHANGELOG.md     # Update changelog
git commit -am "chore: bump version to X.Y.Z"
git push

# Tag and build
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin vX.Y.Z
make clean && make build

# Test
pip install dist/snapflow-X.Y.Z-py3-none-any.whl
python scripts/verify_installation.py

# Release
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*  # Production

# Post-release
# Create GitHub release
# Announce on socials
# Monitor feedback
```

---

**Questions?** Contact the maintainers or open an issue.
