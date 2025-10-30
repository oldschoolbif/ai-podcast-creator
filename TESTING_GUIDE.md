# Automated Testing Guide

## 🎯 Overview

AI Podcast Creator now has a **comprehensive automated testing framework** using **pytest**.

---

## ✅ What We've Implemented

### Testing Framework:
- **pytest** - Industry-standard Python testing
- **pytest-cov** - Code coverage reporting
- **pytest-mock** - Mocking for isolated tests
- **pytest-xdist** - Parallel test execution

### Test Types:
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Multi-component testing
3. **Smoke Tests** - Quick validation
4. **GPU Tests** - GPU-specific testing
5. **Performance Tests** - Benchmarking

### Test Coverage:
- ✅ GPU utilities (`test_gpu_utils.py`)
- ✅ Script parser (`test_script_parser.py`)
- ✅ Complete pipeline (`test_pipeline.py`)
- ✅ Error handling
- ✅ Module imports

---

## 🚀 Quick Start

### 1. Install Test Dependencies

```powershell
cd AI_Podcast_Creator
pip install -r requirements-test.txt
```

### 2. Run Tests (Multiple Options)

**Option A: PowerShell Script (Recommended for Windows)**
```powershell
# Quick validation (smoke + unit tests)
.\run_tests.ps1

# Specific test types
.\run_tests.ps1 smoke       # Quick smoke tests
.\run_tests.ps1 unit        # Unit tests only
.\run_tests.ps1 integration # Integration tests
.\run_tests.ps1 gpu         # GPU tests
.\run_tests.ps1 coverage    # Full suite + coverage report
.\run_tests.ps1 fast        # Fast tests only (exclude slow)
.\run_tests.ps1 all         # All tests
```

**Option B: Python Script (Cross-platform)**
```powershell
python run_tests.py
```

**Option C: Direct pytest (Most flexible)**
```powershell
# Run all tests
pytest

# Run specific test types
pytest -m smoke
pytest -m unit
pytest -m integration
pytest -m gpu

# Run specific files
pytest tests/unit/test_gpu_utils.py
pytest tests/integration/test_pipeline.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run in parallel (faster)
pytest -n auto
```

---

## 📊 Test Markers

Tests are organized with markers for easy filtering:

| Marker | Description | Usage |
|--------|-------------|-------|
| `smoke` | Quick validation tests | `pytest -m smoke` |
| `unit` | Unit tests | `pytest -m unit` |
| `integration` | Integration tests | `pytest -m integration` |
| `slow` | Slow-running tests | `pytest -m "not slow"` |
| `gpu` | Requires GPU | `pytest -m gpu` |
| `network` | Requires internet | `pytest -m "not network"` |
| `audio` | Audio processing | `pytest -m audio` |
| `video` | Video processing | `pytest -m video` |

---

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_data/               # Test data files
├── unit/                    # Unit tests
│   ├── test_gpu_utils.py    # GPU utility tests
│   ├── test_script_parser.py # Script parser tests
│   ├── test_tts_engine.py   # TTS engine tests
│   ├── test_audio_mixer.py  # Audio mixer tests
│   └── test_music_generator.py # Music generator tests
└── integration/             # Integration tests
    └── test_pipeline.py     # End-to-end pipeline tests
```

---

## 🔧 Configuration Files

### `pytest.ini`
Main pytest configuration:
- Test discovery patterns
- Output options
- Coverage settings
- Test markers

### `requirements-test.txt`
Testing dependencies:
- pytest and plugins
- Mocking tools
- Coverage tools
- Test utilities

### `.github/workflows/tests.yml`
CI/CD configuration:
- Automated testing on push/PR
- Multiple OS and Python versions
- Coverage reporting
- GPU testing (requires self-hosted runner)

---

## 💡 Writing New Tests

### Example Unit Test

```python
# tests/unit/test_my_module.py

import pytest
from src.my_module import MyClass

class TestMyClass:
    def test_initialization(self):
        """Test MyClass initialization."""
        obj = MyClass()
        assert obj is not None
    
    def test_method(self, test_config):
        """Test a method with fixture."""
        obj = MyClass(test_config)
        result = obj.do_something()
        assert result == expected_value
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that takes time."""
        # ... slow test ...
        pass
```

### Example Integration Test

```python
# tests/integration/test_my_pipeline.py

import pytest

@pytest.mark.integration
@pytest.mark.slow
class TestMyPipeline:
    def test_end_to_end(self, test_config, temp_dir):
        """Test complete pipeline."""
        # Setup
        input_file = temp_dir / 'input.txt'
        
        # Execute
        result = run_pipeline(input_file)
        
        # Verify
        assert result.exists()
        assert result.stat().st_size > 0
```

---

## 📈 Coverage Reports

### Generate HTML Coverage Report

```powershell
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

### Coverage Summary

```powershell
pytest --cov=src --cov-report=term-missing
```

Shows coverage % and missing lines in terminal.

---

## 🎯 Common Test Scenarios

### 1. Before Committing Changes

```powershell
# Run fast tests
.\run_tests.ps1 fast
```

### 2. Before Creating PR

```powershell
# Run full suite with coverage
.\run_tests.ps1 coverage
```

### 3. Testing GPU Features

```powershell
# Run GPU tests only
.\run_tests.ps1 gpu
```

### 4. Quick Validation

```powershell
# Run smoke tests
.\run_tests.ps1 smoke
```

### 5. Testing Specific Component

```powershell
# Test just GPU utils
pytest tests/unit/test_gpu_utils.py -v

# Test just script parser
pytest tests/unit/test_script_parser.py -v
```

---

## 🐛 Debugging Failed Tests

### Run with More Verbose Output

```powershell
pytest -vv
```

### Stop on First Failure

```powershell
pytest -x
```

### Run Specific Test

```powershell
pytest tests/unit/test_gpu_utils.py::TestGPUManager::test_init_with_gpu
```

### Show Print Statements

```powershell
pytest -s
```

### Drop into Debugger on Failure

```powershell
pytest --pdb
```

---

## 🔄 Continuous Integration

Tests run automatically on:
- **Push to main/develop**
- **Pull requests**
- **Weekly schedule** (Sunday midnight)

### CI Test Matrix:
- **OS**: Ubuntu, Windows
- **Python**: 3.10, 3.11, 3.12
- **Tests**: Smoke, Unit, Integration
- **Coverage**: Uploaded to Codecov

### CI Status:
Check `.github/workflows/tests.yml` for configuration.

---

## 🏗️ Test Fixtures

Shared fixtures are defined in `tests/conftest.py`:

| Fixture | Description |
|---------|-------------|
| `project_root` | Project root directory |
| `test_data_dir` | Test data directory |
| `temp_dir` | Temporary directory (auto-cleanup) |
| `test_config` | Minimal test configuration |
| `test_config_file` | Config file path |
| `sample_script_text` | Sample podcast script |
| `sample_script_file` | Sample script file |
| `mock_audio_file` | Mock audio file |
| `gpu_available` | GPU availability check |
| `skip_if_no_gpu` | Skip test if no GPU |
| `skip_if_no_internet` | Skip if no internet |

### Using Fixtures

```python
def test_my_function(test_config, temp_dir):
    """Test with fixtures."""
    # test_config and temp_dir automatically provided
    pass
```

---

## ⚡ Performance Testing

```powershell
# Run with benchmarking
pytest --benchmark-only

# Compare performance
pytest --benchmark-compare
```

---

## 📋 Test Checklist

**Before every commit:**
- [ ] Run `.\run_tests.ps1 fast` (< 1 minute)
- [ ] All tests pass
- [ ] No new linter warnings

**Before every PR:**
- [ ] Run `.\run_tests.ps1 coverage`
- [ ] Coverage > 80%
- [ ] All integration tests pass
- [ ] Documentation updated

**Weekly:**
- [ ] Run `.\run_tests.ps1 all`
- [ ] GPU tests pass (if GPU available)
- [ ] Performance benchmarks OK

---

## 🎓 Best Practices

### 1. Test Naming
- Start with `test_`
- Be descriptive: `test_gpu_detection_with_rtx_4060`
- Group related tests in classes

### 2. Test Organization
- One test file per source file
- Group by functionality
- Use markers for categorization

### 3. Test Independence
- Each test should run independently
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 4. Mocking
- Mock external dependencies
- Mock slow operations
- Mock network calls

### 5. Assertions
- One logical assertion per test
- Use descriptive assertion messages
- Test edge cases

---

## 🚨 Common Issues

### Issue: "Module not found"
**Solution:** Ensure you're in project root and src is in path
```powershell
cd AI_Podcast_Creator
$env:PYTHONPATH = "."
pytest
```

### Issue: "GPU tests failing"
**Solution:** GPU tests require actual GPU hardware
```powershell
# Skip GPU tests
pytest -m "not gpu"
```

### Issue: "Slow tests timing out"
**Solution:** Skip slow tests or increase timeout
```powershell
pytest -m "not slow"
# Or
pytest --timeout=300
```

---

## 📊 Current Test Statistics

**Total Tests:** 30+ tests  
**Test Files:** 5+ files  
**Coverage Target:** 80%+  
**Test Markers:** 8 markers  
**CI/CD:** GitHub Actions ready

---

## 🎯 Next Steps

1. **Run tests now:**
   ```powershell
   .\run_tests.ps1
   ```

2. **Check coverage:**
   ```powershell
   .\run_tests.ps1 coverage
   ```

3. **View coverage report:**
   ```powershell
   start htmlcov/index.html
   ```

4. **Add tests for new features** as you develop them

---

## 🤝 Contributing Tests

When adding new features:
1. Write tests FIRST (TDD)
2. Run tests FREQUENTLY
3. Maintain coverage ABOVE 80%
4. Document test CASES
5. Use appropriate MARKERS

---

## 📞 Support

**Test failing?**
1. Check error message
2. Run with `-vv` for verbose output
3. Check if it's environment-specific
4. Review test fixtures
5. Check CI logs

**Need help?**
- See examples in existing tests
- Check pytest documentation
- Review conftest.py fixtures

---

**Happy Testing!** 🧪✅

