#!/usr/bin/env python
"""
SnapFlow Verification Script

Comprehensive verification that SnapFlow is properly installed and working.
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Verify Python version is 3.8+."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False


def check_module_imports():
    """Verify all SnapFlow modules can be imported."""
    print("\n🔍 Checking module imports...")
    
    modules = [
        'snapflow',
        'snapflow.app',
        'snapflow.cli',
        'snapflow.config',
        'snapflow.models',
        'snapflow.operations',
        'snapflow.exceptions',
    ]
    
    all_ok = True
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"   ✅ {module_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {e}")
            all_ok = False
    
    return all_ok


def check_dependencies():
    """Verify required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    dependencies = [
        'yaml',
        'click',
        'sqlalchemy',
        'humanize',
        'schema',
        'psutil',
        'sqlalchemy_utils',
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} (missing)")
            all_ok = False
    
    return all_ok


def check_version():
    """Check SnapFlow version."""
    print("\n🔍 Checking SnapFlow version...")
    try:
        from snapflow import __version__
        print(f"   ✅ SnapFlow v{__version__}")
        return True
    except Exception as e:
        print(f"   ❌ Could not determine version: {e}")
        return False


def check_cli_entry_point():
    """Verify CLI entry point exists."""
    print("\n🔍 Checking CLI entry point...")
    try:
        from snapflow.cli import main
        print("   ✅ CLI main() function found")
        return True
    except ImportError as e:
        print(f"   ❌ CLI import failed: {e}")
        return False


def check_models():
    """Verify database models."""
    print("\n🔍 Checking database models...")
    try:
        from snapflow.models import Snapshot, DatabaseTable, generate_unique_hash
        
        # Test hash generation
        hash1 = generate_unique_hash()
        hash2 = generate_unique_hash()
        assert len(hash1) == 32, "Hash should be 32 chars"
        assert hash1 != hash2, "Hashes should be unique"
        
        # Test model creation
        snapshot = Snapshot(
            snapshot_name="test",
            project_name="test_project"
        )
        assert snapshot.snapshot_name == "test"
        assert snapshot.is_ready is True
        
        table = DatabaseTable(
            table_name="test_db",
            snapshot=snapshot
        )
        assert table.table_name == "test_db"
        
        print("   ✅ Models work correctly")
        return True
    except Exception as e:
        print(f"   ❌ Model check failed: {e}")
        return False


def check_operations():
    """Verify database operations module."""
    print("\n🔍 Checking database operations...")
    try:
        from snapflow.operations import SUPPORTED_DIALECTS
        assert 'postgresql' in SUPPORTED_DIALECTS
        assert 'mysql' in SUPPORTED_DIALECTS
        print(f"   ✅ Supported dialects: {', '.join(SUPPORTED_DIALECTS)}")
        return True
    except Exception as e:
        print(f"   ❌ Operations check failed: {e}")
        return False


def check_exceptions():
    """Verify custom exceptions."""
    print("\n🔍 Checking exception hierarchy...")
    try:
        from snapflow.exceptions import (
            SnapFlowError,
            InvalidConfigError,
            MissingConfigError,
            DatabaseError,
            SnapshotNotFoundError,
            SnapshotAlreadyExistsError,
        )
        
        # Test exception creation
        exc = SnapshotNotFoundError("test")
        assert exc.snapshot_name == "test"
        assert "test" in str(exc)
        
        print("   ✅ Exception classes work correctly")
        return True
    except Exception as e:
        print(f"   ❌ Exception check failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("SnapFlow Verification")
    print("=" * 70)
    
    checks = [
        check_python_version,
        check_module_imports,
        check_dependencies,
        check_version,
        check_cli_entry_point,
        check_models,
        check_operations,
        check_exceptions,
    ]
    
    results = [check() for check in checks]
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ All {total} checks passed!")
        print("\nSnapFlow is properly installed and ready to use.")
        return 0
    else:
        print(f"❌ {passed}/{total} checks passed")
        print(f"\n{total - passed} check(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
