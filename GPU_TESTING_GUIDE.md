# GPU Testing Guide

## What is CUDA?

**CUDA** (Compute Unified Device Architecture) is NVIDIA's parallel computing platform and programming model that allows developers to use NVIDIA GPUs for general-purpose computing beyond just graphics.

### Key Points:
- **CUDA** = NVIDIA's GPU computing platform
- Allows GPUs to accelerate computation-intensive tasks
- Used for AI/ML workloads (PyTorch, TensorFlow, etc.)
- Requires:
  - NVIDIA GPU hardware
  - CUDA Toolkit installed
  - CUDA-enabled libraries (PyTorch with CUDA support)

### In This Project:
- GPU acceleration speeds up:
  - **TTS (Coqui XTTS)**: 5x faster
  - **Music (MusicGen)**: 10x faster  
  - **Avatar (SadTalker)**: 12x faster
- Overall: **10-12x speedup** for podcast generation

---

## When Do GPU Tests Run?

### Current Configuration

GPU tests are **quarantined** (disabled by default) and only run when explicitly enabled:

#### 1. **CI/CD (GitHub Actions)**
- **Status**: ❌ **Disabled** (GPU tests skipped)
- **Reason**: GitHub Actions runners don't have NVIDIA GPUs
- **Configuration**: `PY_ENABLE_GPU_TESTS=0` in `.github/workflows/tests.yml`
- **Result**: All `@pytest.mark.gpu` tests are automatically skipped

#### 2. **Local Development (Manual)**
- **Status**: ✅ **Can be enabled** on machines with NVIDIA GPUs
- **How to enable**:
  ```bash
  # Windows PowerShell
  $env:PY_ENABLE_GPU_TESTS="1"
  pytest tests/unit -m gpu
  
  # Linux/Mac
  export PY_ENABLE_GPU_TESTS=1
  pytest tests/unit -m gpu
  ```

#### 3. **Dedicated GPU CI (Future)**
- **Status**: ⚠️ **Not yet configured**
- **Would require**: 
  - Self-hosted runners with NVIDIA GPUs, OR
  - Cloud GPU runners (GitHub doesn't provide GPU runners)
  - Services like: AWS EC2 (g4dn), Google Cloud (GPU instances), Azure (NC-series)

---

## How GPU Tests Are Skipped

### Test Marking
Tests that require GPU are marked with `@pytest.mark.gpu`:

```python
@pytest.mark.gpu
def test_generate_sadtalker_gpu(self, test_config, temp_dir, skip_if_no_gpu):
    """Test SadTalker with GPU acceleration."""
    # This test only runs if PY_ENABLE_GPU_TESTS=1 AND CUDA is available
```

### Skip Logic (in `tests/conftest.py`)

```python
def _handle_gpu_quarantine() -> None:
    # Step 1: Check if GPU tests are enabled via environment variable
    if not _gpu_tests_enabled():  # Checks PY_ENABLE_GPU_TESTS == "1"
        pytest.skip("GPU quarantine: set PY_ENABLE_GPU_TESTS=1 to enable GPU tests.")
    
    # Step 2: Check if CUDA is actually available
    torch = _torch_module()
    if torch is not None and not torch.cuda.is_available():
        pytest.skip("GPU tests enabled but no CUDA device available.")
```

### Skip Conditions:
1. ❌ `PY_ENABLE_GPU_TESTS != "1"` → Skip (default in CI)
2. ❌ PyTorch not installed → Skip
3. ❌ CUDA not available → Skip
4. ✅ `PY_ENABLE_GPU_TESTS=1` AND CUDA available → **Run test**

---

## GPU Tests in This Project

### Test Files with GPU Tests:
- `tests/unit/test_gpu_utils.py` - 17 GPU tests
- `tests/unit/test_gpu_utils_real.py` - 4 GPU tests
- `tests/unit/test_avatar_generator.py` - 2 GPU tests
- `tests/unit/test_music_generator.py` - 1 GPU test
- `tests/unit/test_tts_engine_coverage.py` - 1 GPU test
- `tests/integration/test_pipeline.py` - 2 GPU tests
- **Total**: ~27 GPU-marked tests

### What They Test:
- GPU detection and initialization
- CUDA availability checks
- GPU memory management
- GPU-accelerated TTS generation
- GPU-accelerated music generation
- GPU-accelerated avatar generation
- Performance optimizations (FP16, cuDNN, etc.)

---

## Running GPU Tests Locally

### Prerequisites:
1. **NVIDIA GPU** (6GB+ VRAM recommended)
2. **CUDA Toolkit** installed
3. **CUDA-enabled PyTorch** installed
4. **Environment variable** set

### Step-by-Step:

```bash
# 1. Verify GPU is detected
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# 2. Enable GPU tests
export PY_ENABLE_GPU_TESTS=1  # Linux/Mac
# OR
$env:PY_ENABLE_GPU_TESTS="1"  # Windows PowerShell

# 3. Run GPU tests
pytest tests/unit -m gpu -v

# 4. Run specific GPU test file
pytest tests/unit/test_gpu_utils.py -m gpu -v

# 5. Run all tests (GPU tests will run if enabled)
pytest tests/unit -v
```

### Expected Output:
```
tests/unit/test_gpu_utils.py::test_gpu_detection PASSED
tests/unit/test_avatar_generator.py::test_generate_sadtalker_gpu PASSED
...
```

---

## Why GPU Tests Are Disabled in CI

### Current CI Setup:
- **Runner**: `ubuntu-latest` (GitHub-hosted)
- **GPU**: ❌ None available
- **Cost**: Free tier doesn't include GPU runners

### Options for GPU CI:

#### Option 1: Self-Hosted Runners (Recommended)
```yaml
# .github/workflows/gpu-tests.yml
jobs:
  gpu-tests:
    runs-on: self-hosted  # Your own machine with GPU
    env:
      PY_ENABLE_GPU_TESTS: "1"
```

#### Option 2: Cloud GPU Runners
- **AWS EC2**: g4dn instances (~$0.50/hour)
- **Google Cloud**: GPU instances (~$0.70/hour)
- **Azure**: NC-series (~$0.90/hour)

#### Option 3: Keep Disabled (Current)
- ✅ Tests are written and ready
- ✅ Can be run manually on GPU machines
- ✅ CI focuses on CPU compatibility
- ✅ GPU functionality tested during manual QA

---

## Recommendations

### For Development:
1. **Run GPU tests locally** before committing GPU-related changes
2. **Document GPU requirements** in test docstrings
3. **Use mocking** for GPU tests that don't require actual GPU (already done)

### For CI/CD:
1. **Current approach is fine** - GPU tests are optional
2. **Consider self-hosted runner** if you have a GPU machine
3. **Add GPU test job** that runs on schedule (nightly) rather than every PR

### For Contributors:
- GPU tests are **optional** - don't worry if they're skipped
- Focus on **CPU compatibility** - all code should work without GPU
- GPU is an **optimization**, not a requirement

---

## Summary

| Environment | GPU Tests Run? | How to Enable |
|------------|----------------|---------------|
| **GitHub Actions CI** | ❌ No | Not possible (no GPU runners) |
| **Local (no GPU)** | ❌ No | N/A (CUDA not available) |
| **Local (with GPU)** | ✅ Yes | `PY_ENABLE_GPU_TESTS=1` |
| **Self-hosted CI** | ✅ Yes | Configure runner + env var |
| **Cloud GPU CI** | ✅ Yes | Configure cloud runner + env var |

**Current Status**: GPU tests are **quarantined** (disabled by default) and run only when:
1. `PY_ENABLE_GPU_TESTS=1` is set
2. CUDA is available on the system

This is the **correct approach** for projects where GPU is optional but beneficial.
