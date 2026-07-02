# CI/CD Pipeline Monitoring Guide

## Quick Status Check

### GitHub Actions URL
🔗 https://github.com/frankosakwe/snapflow/actions

### Recent Commits to Monitor
1. **d5bceea** - Documentation (just pushed)
2. **ee37353** - Shell bash consistency (just pushed) 
3. **f9e208b** - psycopg2-binary Windows fix (just pushed)
4. **870d783** - Debugging and shell consistency
5. **0d743eb** - pytest installation fix
6. **a9a16d4** - pytest cross-platform fix
7. **f6d7851** - Markdown renderer fix
8. **d579028** - Core test fixes

---

## What to Look For

### ✅ Expected Success Indicators

#### 1. Test Job Matrix (should see ALL passing)
- Ubuntu-latest + Python 3.8 ✅
- Ubuntu-latest + Python 3.9 ✅
- Ubuntu-latest + Python 3.10 ✅
- Ubuntu-latest + Python 3.11 ✅
- Ubuntu-latest + Python 3.12 ✅
- Windows-latest + Python 3.8 ✅
- Windows-latest + Python 3.9 ✅
- Windows-latest + Python 3.10 ✅
- Windows-latest + Python 3.11 ✅
- Windows-latest + Python 3.12 ✅
- macOS-latest + Python 3.10 ✅
- macOS-latest + Python 3.11 ✅
- macOS-latest + Python 3.12 ✅

#### 2. Key Success Messages
Look for these in the logs:

**Installation Phase:**
```
Installing pip...
Installing requirements-dev.txt...
Installing package in editable mode...
Installation complete!
```

**Database Drivers (Unix):**
```
Installing database drivers for Unix...
Successfully installed psycopg2-binary-X.X.X PyMySQL-X.X.X
```

**Database Drivers (Windows):**
```
Installing database drivers for Windows...
Successfully installed PyMySQL-X.X.X
Skipping psycopg2-binary on Windows (not needed for tests)
```

**Pytest Verification:**
```
pytest version: X.X.X
```

**Test Execution:**
```
======================== 54 passed in X.XXs ========================
```

#### 3. All Jobs Should Pass
- ✅ code-quality
- ✅ test (all 13 matrix combinations)
- ✅ build
- ✅ docs
- ✅ security

---

## ❌ Potential Issues to Watch

### Issue 1: psycopg2-binary Still Failing on Windows
**Symptoms:**
```
error: Microsoft Visual C++ 14.0 or greater is required
LINK : fatal error LNK1181: cannot open input file 'libpq.lib'
```

**Resolution:**
- This should NOT happen with current fixes
- Check if conditional installation is working: `if: runner.os == 'Windows'`
- Verify Windows runner is NOT trying to install psycopg2-binary

### Issue 2: pytest Import Error
**Symptoms:**
```
ModuleNotFoundError: No module named 'pytest'
```

**Resolution:**
- Should NOT happen with `python -m pip install` standardization
- Check if requirements-dev.txt is being installed correctly
- Verify pytest is in the package list output

### Issue 3: Test Failures
**Symptoms:**
```
FAILED tests/test_models.py::TestSnapshot::test_snapshot_creation
```

**Resolution:**
- Should NOT happen - all tests passing locally
- Check for environment-specific issues in logs
- Review the specific test failure message

### Issue 4: Shell Command Not Found
**Symptoms:**
```
The term 'pytest' is not recognized as a name of a cmdlet
```

**Resolution:**
- Should NOT happen with `shell: bash` on all steps
- Verify bash shell is being used (check step header in logs)

---

## 📊 Performance Expectations

### Build Times (Approximate)
- **Ubuntu**: 3-5 minutes per Python version
- **Windows**: 4-6 minutes per Python version (faster now without psycopg2 build!)
- **macOS**: 4-6 minutes per Python version

### Total Pipeline Time
- **Before fixes**: ~45-60 minutes (with failures)
- **After fixes**: ~30-40 minutes (all passing)

---

## 🔍 How to Read GitHub Actions Logs

### 1. Navigate to Actions Tab
https://github.com/frankosakwe/snapflow/actions

### 2. Click on the Latest Workflow Run
Should be titled: "CI/CD Pipeline" with commit message

### 3. Check Overall Status
- Green checkmark = All jobs passed ✅
- Red X = Some jobs failed ❌
- Yellow circle = Jobs still running ⏳

### 4. Drill Into Failed Jobs (if any)
- Click on the failed job name
- Expand the failing step
- Read error message carefully
- Check "Display Python and pip info" step for versions
- Check "Install dependencies" step for installation logs

### 5. Compare Across Matrix
- If Windows-3.8 fails but Windows-3.9 passes → Python version issue
- If all Windows fail but Ubuntu passes → Platform-specific issue
- If all platforms fail → General code or config issue

---

## 🛠️ Quick Fixes (If Needed)

### If a Job Fails:

#### 1. Check the Error Message
```bash
# Look in GitHub Actions logs for the specific error
```

#### 2. Reproduce Locally
```bash
# Clone and test locally
git pull origin main
python -m pytest -v
```

#### 3. Apply Fix and Push
```bash
git add .
git commit -m "fix: [description of fix]"
git push origin main
```

#### 4. Monitor New Run
- GitHub Actions will automatically trigger on push
- Watch the new run for success

---

## 📈 Success Criteria

### Pipeline is SUCCESSFUL when:
1. ✅ All 13 test matrix combinations pass
2. ✅ Code quality job passes (Black, flake8, isort, mypy)
3. ✅ Build job creates distribution packages
4. ✅ Documentation job validates README
5. ✅ Security job completes (may have warnings, that's OK)
6. ✅ All 54 tests pass on each platform/Python combination
7. ✅ Zero test failures, zero fatal errors
8. ✅ Coverage reports upload successfully

### Pipeline Can Be Considered COMPLETE when:
- At least one full successful run across all matrix combinations
- No red X marks in the workflow visualization
- All checkmarks green ✅

---

## 🎯 What Success Looks Like

### GitHub Actions Summary View:
```
✅ CI/CD Pipeline #XX
   ✅ code-quality (3m 24s)
   ✅ test (13 jobs)
      ✅ ubuntu-latest / 3.8 (4m 12s)
      ✅ ubuntu-latest / 3.9 (4m 08s)
      ✅ ubuntu-latest / 3.10 (4m 15s)
      ✅ ubuntu-latest / 3.11 (4m 11s)
      ✅ ubuntu-latest / 3.12 (4m 18s)
      ✅ windows-latest / 3.8 (5m 34s)
      ✅ windows-latest / 3.9 (5m 28s)
      ✅ windows-latest / 3.10 (5m 41s)
      ✅ windows-latest / 3.11 (5m 38s)
      ✅ windows-latest / 3.12 (5m 45s)
      ✅ macos-latest / 3.10 (5m 22s)
      ✅ macos-latest / 3.11 (5m 18s)
      ✅ macos-latest / 3.12 (5m 29s)
   ✅ build (2m 45s)
   ✅ docs (1m 32s)
   ✅ security (2m 18s)
```

---

## 📞 Next Actions After Success

### 1. Update README.md
Add CI badges:
```markdown
[![CI/CD Pipeline](https://github.com/frankosakwe/snapflow/actions/workflows/ci.yml/badge.svg)](https://github.com/frankosakwe/snapflow/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/frankosakwe/snapflow/branch/main/graph/badge.svg)](https://codecov.io/gh/frankosakwe/snapflow)
```

### 2. Mark Task Complete
- Update project tracking documents
- Close related issues
- Document lessons learned

### 3. Plan Next Phase
- Feature development
- Documentation improvements
- Release preparation
- Marketing/community outreach

---

**Last Updated**: 2026-07-02
**Status**: ✅ All fixes pushed, awaiting CI validation
**Repository**: https://github.com/frankosakwe/snapflow
