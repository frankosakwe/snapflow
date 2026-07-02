"""
SnapFlow Installation Verification Script

Run this script to verify that SnapFlow is installed correctly.
"""

import sys
from importlib import import_module


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("  ✗ Python 3.8+ required")
        print(f"  Current version: {sys.version}")
        return False
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_module_imports():
    """Check if all required modules can be imported."""
    print("\nChecking module imports...")
    
    modules = [
        ('snapflow', 'SnapFlow core'),
        ('snapflow.app', 'Application module'),
        ('snapflow.cli', 'CLI module'),
        ('snapflow.config', 'Configuration module'),
        ('snapflow.models', 'Models module'),
        ('snapflow.operations', 'Operations module'),
        ('snapflow.exceptions', 'Exceptions module'),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            import_module(module_name)
            print(f"  ✓ {description}")
        except ImportError as e:
            print(f"  ✗ {description}: {e}")
            all_ok = False
    
    return all_ok


def check_dependencies():
    """Check if all dependencies are installed."""
    print("\nChecking dependencies...")
    
    dependencies = [
        ('yaml', 'PyYAML'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('humanize', 'humanize'),
        ('schema', 'schema'),
        ('click', 'Click'),
        ('sqlalchemy_utils', 'SQLAlchemy-Utils'),
        ('psutil', 'psutil'),
    ]
    
    all_ok = True
    for module_name, package_name in dependencies:
        try:
            mod = import_module(module_name)
            version = getattr(mod, '__version__', 'unknown')
            print(f"  ✓ {package_name}: {version}")
        except ImportError:
            print(f"  ✗ {package_name}: not installed")
            all_ok = False
    
    return all_ok


def check_version():
    """Check SnapFlow version."""
    print("\nChecking SnapFlow version...")
    
    try:
        from snapflow import __version__
        print(f"  ✓ SnapFlow version: {__version__}")
        return True
    except Exception as e:
        print(f"  ✗ Could not determine version: {e}")
        return False


def check_cli_entry_point():
    """Check if CLI entry point is available."""
    print("\nChecking CLI entry point...")
    
    try:
        from snapflow.cli import main
        print("  ✓ CLI entry point found")
        return True
    except ImportError as e:
        print(f"  ✗ CLI entry point not found: {e}")
        return False


def check_database_drivers():
    """Check available database drivers."""
    print("\nChecking database drivers (optional)...")
    
    drivers = [
        ('psycopg2', 'PostgreSQL driver'),
        ('pymysql', 'MySQL driver'),
    ]
    
    for module_name, description in drivers:
        try:
            import_module(module_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ⚠ {description}: not installed (optional)")


def run_basic_test():
    """Run a basic functionality test."""
    print("\nRunning basic functionality test...")
    
    try:
        from snapflow.models import generate_unique_hash, Snapshot, DatabaseTable
        
        # Test hash generation
        hash1 = generate_unique_hash()
        hash2 = generate_unique_hash()
        assert hash1 != hash2, "Hash generation failed"
        print("  ✓ Hash generation works")
        
        # Test model creation
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            hash='abc123def456789012345678901234'
        )
        assert snapshot.snapshot_name == 'test'
        print("  ✓ Snapshot model works")
        
        table = DatabaseTable(
            table_name='test_db',
            snapshot=snapshot
        )
        assert table.table_name == 'test_db'
        print("  ✓ DatabaseTable model works")
        
        # Test internal name generation
        internal_name = table.get_master_name()
        assert internal_name.startswith('snapflow_')
        print("  ✓ Internal name generation works")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Basic test failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("SnapFlow Installation Verification")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_module_imports(),
        check_dependencies(),
        check_version(),
        check_cli_entry_point(),
        run_basic_test(),
    ]
    
    check_database_drivers()  # Optional, doesn't affect result
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All checks passed! SnapFlow is installed correctly.")
        print("\nNext steps:")
        print("  1. Run 'snapflow --help' to see available commands")
        print("  2. Run 'snapflow init' to configure your first project")
        print("  3. Run 'snapflow version' to verify CLI is working")
        print("=" * 60)
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("  1. Reinstall SnapFlow: pip install --upgrade snapflow")
        print("  2. Install missing dependencies: pip install -r requirements.txt")
        print("  3. Check Python version: python --version")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
