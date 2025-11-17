# Test Infrastructure Fixes Explained

## What is "Test Infrastructure"?

**Test infrastructure** refers to the **foundation** that makes tests runnable - not the test logic itself, but the supporting pieces that tests depend on:

- **Fixtures** - Shared test data/setup functions
- **Markers** - Labels that categorize tests (gpu, slow, e2e, etc.)
- **Test data generators** - Helpers that create valid test files
- **Configuration** - pytest settings, environment variables
- **Dependencies** - What tests need to run (mocks, stubs, etc.)

Think of it like building a house:
- **Test logic** = The actual tests (the rooms)
- **Test infrastructure** = Foundation, plumbing, wiring (what makes the rooms usable)

## The Problem: Tests Were Failing Before They Could Run

During mutation testing, pytest would **fail during test collection** (before running any tests) because:

1. Tests referenced fixtures that didn't exist
2. Tests tried to run GPU code without proper markers
3. Tests created invalid test data that broke downstream
4. Tests imported modules/fixtures that weren't available

**Result:** Mutation testing never got to run the actual tests - it failed at the "setup" phase.

## Specific Infrastructure Fixes We Made

### 1. Missing Fixtures ✅

**Problem:** Tests referenced fixtures that weren't defined in `conftest.py`

**Example:**
```python
# tests/property/test_property_based_expansion.py
def test_all_styles_generate_frames(self, test_config_visualization, ...):
    # ❌ ERROR: fixture 'test_config_visualization' not found
```

**Fix:** Added missing fixtures to `tests/conftest.py`:
```python
@pytest.fixture
def test_config_visualization(temp_dir: Path) -> dict:
    """Create test config with visualization settings."""
    return {
        "video": {"resolution": [1920, 1080], "fps": 30},
        "visualization": {
            "style": "waveform",
            "primary_color": [0, 150, 255],
            # ... etc
        },
    }

@pytest.fixture
def sample_script_text() -> str:
    """Sample script text for testing."""
    return """# Introduction
Welcome to today's podcast episode..."""
```

**Why it matters:** Without these fixtures, pytest can't even collect the tests, let alone run them.

---

### 2. GPU Test Markers ✅

**Problem:** GPU tests were trying to access CUDA without proper markers, causing failures

**Example:**
```python
# tests/unit/test_gpu_utils_real.py
def test_optimize_for_inference_with_cuda(self):
    # ❌ ERROR: RuntimeError: Found no NVIDIA driver
    # Test tried to use GPU but wasn't marked, and GPU wasn't available
```

**Fix:** Added `@pytest.mark.gpu` marker:
```python
@pytest.mark.gpu
def test_optimize_for_inference_with_cuda(self):
    """Test inference optimization with CUDA."""
    # Now properly skipped when GPU not available
```

**Why it matters:** 
- Tests marked `@pytest.mark.gpu` are automatically skipped when `PY_ENABLE_GPU_TESTS=0`
- Prevents tests from failing when GPU isn't available
- Allows mutation testing to exclude GPU tests by default

---

### 3. Invalid Test Data Creation ✅

**Problem:** E2E tests were creating fake/invalid audio files that broke downstream code

**Example:**
```python
# tests/e2e/test_complete_workflows.py
audio_file = temp_dir / "audio.mp3"
audio_file.write_bytes(b"fake-audio")  # ❌ Only 10 bytes - invalid MP3
# Later: FFmpeg fails because file is corrupted
```

**Fix:** Use proper audio file generator:
```python
from tests.conftest import create_valid_mp3_file

audio_file = temp_dir / "audio.mp3"
create_valid_mp3_file(audio_file, duration_seconds=5.0)  # ✅ Valid MP3 file
```

**Why it matters:** 
- Mutation testing runs real code paths (not just mocks)
- Invalid test data causes real code to fail
- Tests need valid data to exercise real behavior

---

### 4. Property/Performance Test Dependencies ✅

**Problem:** Property and performance tests referenced fixtures/dependencies that weren't available

**Example:**
```python
# tests/property/test_property_based_expansion.py
def test_all_styles_generate_frames(self, test_config_visualization, ...):
    # ❌ ERROR: fixture 'test_config_visualization' not found
    # (Same as #1, but discovered during mutation testing)
```

**Fix:** Same as #1 - added missing fixtures to `conftest.py`

**Why it matters:** All test files need access to shared fixtures through `conftest.py`

---

## The Pattern: Death Spiral

What happened during the week:

1. **Run mutation testing** → Fails: "fixture 'test_config_visualization' not found"
2. **Fix:** Add fixture to conftest.py
3. **Re-run mutation testing** → Fails: "GPU test tried to access CUDA"
4. **Fix:** Add `@pytest.mark.gpu` marker
5. **Re-run mutation testing** → Fails: "Audio file validation failed"
6. **Fix:** Use `create_valid_mp3_file` helper
7. **Re-run mutation testing** → Fails: "fixture 'sample_script_text' not found"
8. **Fix:** Add fixture to conftest.py
9. **Re-run mutation testing** → ... (repeat)

**Each fix revealed another infrastructure problem** - we were fixing infrastructure issues **during** mutation testing runs instead of **before**.

## What Should Have Happened

**Correct workflow:**
1. ✅ Run `pytest` locally first
2. ✅ Fix ALL infrastructure issues (fixtures, markers, test data)
3. ✅ Ensure pytest passes completely
4. ✅ THEN run mutation testing once

**What actually happened:**
1. ❌ Started mutation testing immediately
2. ❌ Fixed issues one-by-one as they appeared
3. ❌ Each fix required a full Docker cycle (5-10 minutes)
4. ❌ Never got to actual mutation testing

## Summary

**Test infrastructure fixes** = Fixing the **foundation** that makes tests runnable:
- ✅ Missing fixtures → Added to `conftest.py`
- ✅ Missing markers → Added `@pytest.mark.gpu` where needed
- ✅ Invalid test data → Use proper generators (`create_valid_mp3_file`)
- ✅ Missing dependencies → Added shared fixtures

**These aren't test logic fixes** - the actual tests were correct. We just needed to fix the **supporting infrastructure** so tests could actually run.

**Result:** Now pytest can collect and run all tests successfully, so mutation testing can finally execute.

