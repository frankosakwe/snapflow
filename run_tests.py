#!/usr/bin/env python
"""
Test Runner Script for SnapFlow

Runs the complete test suite and reports results.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("SnapFlow Test Suite")
    print("=" * 70)
    print()
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed. Installing...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-q",
            "pytest", "pytest-cov", "pytest-mock"
        ])
        import pytest
    
    # Run tests
    print("Running tests...")
    print()
    
    args = [
        "-v",
        "--tb=short",
        "--color=yes",
    ]
    
    result = pytest.main(args)
    
    print()
    print("=" * 70)
    if result == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {result}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    sys.exit(main())
