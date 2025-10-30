"""
Test Runner Script
Automated testing with different configurations
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print('='*70)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print(f"\n❌ FAILED: {description}")
            return False
        else:
            print(f"\n✅ PASSED: {description}")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  AI PODCAST CREATOR - AUTOMATED TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Test 1: Quick smoke tests
    results['smoke'] = run_command(
        "pytest -v -m smoke tests/",
        "1. SMOKE TESTS (Quick validation)"
    )
    
    # Test 2: Unit tests only
    results['unit'] = run_command(
        "pytest -v -m unit tests/unit/",
        "2. UNIT TESTS (Individual components)"
    )
    
    # Test 3: Integration tests (excluding GPU and network)
    results['integration'] = run_command(
        "pytest -v -m \"integration and not gpu and not network\" tests/integration/",
        "3. INTEGRATION TESTS (Component interaction)"
    )
    
    # Test 4: GPU tests (if GPU available)
    results['gpu'] = run_command(
        "pytest -v -m gpu tests/ --continue-on-collection-errors",
        "4. GPU TESTS (GPU acceleration features)"
    )
    
    # Test 5: Full test suite with coverage
    results['full'] = run_command(
        "pytest -v --cov=src --cov-report=term-missing tests/",
        "5. FULL TEST SUITE WITH COVERAGE"
    )
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name.upper()}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

