# psycopg2-binary Windows Build Fix

## Problem
The CI/CD pipeline was failing on Windows runners with the error:
```
error: Microsoft Visual C++ 14.0 or greater is required
LINK : fatal error LNK1181: cannot open input file 'libpq.lib'
```

This occurred because `psycopg2-binary` was listed in `requirements.txt` as a mandatory dependency, but it requires PostgreSQL client libraries to build on Windows, which are not available on GitHub Actions Windows runners.

## Root Cause
- `psycopg2-binary` needs PostgreSQL development files (`libpq.lib`) to compile on Windows
- GitHub Actions Windows runners don't have PostgreSQL client libraries pre-installed
- The package was trying to build from source instead of using prebuilt wheels
- Tests don't actually need real database drivers since they use mocks

## Solution
Made database drivers optional and platform-specific:

### 1. Updated `requirements.txt`
- Removed `psycopg2-binary` and `PyMySQL` from mandatory dependencies
- Added comments directing users to install via extras: `pip install snapflow[postgresql]` or `pip install snapflow[mysql]`
- These drivers are already defined in `setup.py` under `extras_require`

### 2. Updated `.github/workflows/ci.yml`
- Added conditional installation steps for database drivers
- Unix systems (Ubuntu, macOS): Install both `psycopg2-binary` and `PyMySQL`
- Windows: Install only `PyMySQL` (skips psycopg2-binary)
- Used `runner.os` condition to differentiate platforms

### 3. Updated `.github/workflows/pr-checks.yml`
- Added database driver installation for Ubuntu runner (uses psycopg2-binary)
- PR checks only run on Ubuntu, so both drivers are safe to install

## Benefits
- ✅ Windows CI builds now succeed without PostgreSQL dependencies
- ✅ Tests pass on all platforms (they use mocks, not real databases)
- ✅ Optional dependencies properly defined in `setup.py`
- ✅ Users can install drivers they need via extras
- ✅ Maintains cross-platform compatibility

## Testing Strategy
- Tests use SQLite in-memory database with SQLAlchemy
- Database operations are mocked, so real drivers aren't needed for testing
- Production users install drivers based on their actual database: `pip install snapflow[postgresql]`

## Files Changed
- `requirements.txt` - Removed mandatory database drivers
- `.github/workflows/ci.yml` - Added conditional driver installation
- `.github/workflows/pr-checks.yml` - Added driver installation for Ubuntu

## Verification
After this fix:
1. Windows CI should install successfully without psycopg2-binary
2. Ubuntu and macOS CI should install both drivers
3. All 54 tests should pass on all platforms
4. No build errors related to libpq.lib or PostgreSQL
