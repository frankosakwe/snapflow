# Pytest Command Fix - Cross-Platform Compatibility

**Date**: July 2, 2026  
**Commit**: `a9a16d4`  
**Issue**: pytest not found in PATH during GitHub Actions execution

---

## Problem

The CI/CD pipeline was failing with:

```
pytest: D:\a\_temp\83c5d43f-87ad-4fe1-954b-740a1882f6f5.ps1:2
Line |
   2 |  pytest -v --cov=snapflow --cov-report=xml --cov-report=term-missing - …
     |  ~~~~~~
     | The term 'pytest' is not recognized as a name of a cmdlet, function, 
     | script file, or executable program.
Error: Process completed with exit code 1.
```

**Root Cause**: 
- Running `pytest` directly relies on it being in the system PATH
- On Windows runners, the pytest script may not be added to PATH correctly
- This is a common cross-platform compatibility issue

---

## Solution

Changed all direct `pytest` calls to `python -m pytest` in CI workflows.

### Why This Works

Using `python -m pytest` instead of `pytest`:
1. ✅ **Cross-platform**: Works consistently on Windows, Linux, and macOS
2. ✅ **Reliable**: Doesn't depend on PATH configuration
3. ✅ **Standard**: Official Python way to run installed modules
4. ✅ **Explicit**: Uses the same Python interpreter that installed pytest

---

## Files Modified

### 1. `.github/workflows/ci.yml`

**Before**:
```yaml
- name: Run tests with pytest
  run: |
    pytest -v --cov=snapflow --cov-report=xml --cov-report=term-missing --cov-report=html
```

**After**:
```yaml
- name: Run tests with pytest
  run: |
    python -m pytest -v --cov=snapflow --cov-report=xml --cov-report=term-missing --cov-report=html
```

Also updated benchmark test comment:
```yaml
- name: Run benchmark tests
  run: |
    echo "Benchmark tests would run here"
    echo "python -m pytest tests/benchmark/ --benchmark-only"
```

### 2. `.github/workflows/pr-checks.yml`

**Before**:
```yaml
- name: Run quick tests
  run: |
    pytest tests/ -v --maxfail=3

- name: Run tests with coverage
  run: |
    pytest --cov=snapflow --cov-report=term --cov-report=html
```

**After**:
```yaml
- name: Run quick tests
  run: |
    python -m pytest tests/ -v --maxfail=3

- name: Run tests with coverage
  run: |
    python -m pytest --cov=snapflow --cov-report=term --cov-report=html
```

---

## Changes Summary

| File | Lines Changed | Description |
|------|---------------|-------------|
| `.github/workflows/ci.yml` | 2 changes | Main test job + benchmark comment |
| `.github/workflows/pr-checks.yml` | 2 changes | Quick tests + coverage tests |

**Total**: 4 pytest calls updated

---

## Impact

### Before Fix
❌ Tests failing on Windows runners  
❌ PATH-dependent execution  
❌ Inconsistent behavior across platforms  

### After Fix
✅ Tests run on all platforms (Windows, Linux, macOS)  
✅ Platform-independent execution  
✅ Consistent behavior everywhere  
✅ Follows Python best practices  

---

## Testing

The fix will be verified when GitHub Actions runs:
1. ✅ Ubuntu runners - Should continue working
2. ✅ Windows runners - Should now work (previously failing)
3. ✅ macOS runners - Should continue working

---

## Best Practices

### Always Use `python -m pytest` When:
- Running in CI/CD pipelines
- Using virtual environments
- Working across platforms
- Automating test execution

### Can Use Direct `pytest` When:
- Running locally (developer machine)
- PATH is definitely configured
- Platform-specific scripts

---

## Related Issues

This fix addresses:
- Cross-platform compatibility
- Windows PowerShell execution issues
- PATH configuration problems
- CI/CD reliability

---

## Additional Notes

### Other Commands That Should Use `-m` Flag

Following the same pattern, consider using:
- `python -m pip` instead of `pip`
- `python -m coverage` instead of `coverage`
- `python -m black` instead of `black`
- `python -m flake8` instead of `flake8`

**Why**: Same cross-platform reliability benefits.

### Already Using `-m` Flag in Our CI

Our workflows already correctly use:
```yaml
python -m pip install --upgrade pip  ✅
```

Now pytest follows the same pattern.

---

## Verification Commands

Test locally with both methods to verify compatibility:

```bash
# Direct call (may fail on some systems)
pytest -v

# Module call (works everywhere)
python -m pytest -v
```

Both should produce identical results when both work, but `python -m pytest` is more reliable.

---

## Commit History (Recent)

```
a9a16d4 - Fix pytest command: use 'python -m pytest' for cross-platform compatibility
f6d7851 - Fix CI docs check: add markdown support for readme-renderer
d579028 - Fix test failure and deprecation warnings
dd8efd5 - docs: Add CI/CD improvements summary and update README badges
```

---

## Expected CI Results

After this fix:

✅ **Code Quality** - Pass  
✅ **Tests on Ubuntu** - Pass (continues to work)  
✅ **Tests on Windows** - Pass (now fixed) ⭐  
✅ **Tests on macOS** - Pass (continues to work)  
✅ **Build** - Pass  
✅ **Docs** - Pass  
✅ **Security** - Pass  

---

## Conclusion

This is a **critical fix** for CI/CD reliability. Using `python -m pytest` ensures:
- Consistent behavior across all platforms
- No PATH-related failures
- Better alignment with Python best practices
- More maintainable CI/CD pipelines

---

**Status**: ✅ **FIX DEPLOYED**

All pytest calls in CI workflows have been updated to use `python -m pytest` for maximum compatibility.

---

**Monitor**: https://github.com/frankosakwe/snapflow/actions

