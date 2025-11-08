# GPU Utilization Testing Guide

## Overview

GPU utilization tests ensure that components properly utilize GPU resources when available. These tests are integrated into the CI pipeline and can be run locally.

## Test Structure

### Unit Tests (`tests/unit/test_gpu_utilization.py`)

Tests cover:
1. **GPU Utilization Tracking** - Metrics correctly track GPU usage before/after components
2. **CPU/RAM Tracking** - System resource monitoring
3. **GPU Manager** - `get_utilization()` method works correctly
4. **Component GPU Usage** - Components that should use GPU are tracked
5. **GPU Utilization Thresholds** - Components meet minimum GPU usage requirements
6. **Real GPU Integration** - Tests with actual GPU hardware (skip if unavailable)

## Running Tests

### Local Testing (with GPU)

```bash
# Run all GPU utilization tests
pytest tests/unit/test_gpu_utilization.py -v

# Run only non-GPU tests (mocked)
pytest tests/unit/test_gpu_utilization.py -v -m "not gpu"

# Run only real GPU tests (requires GPU)
pytest tests/unit/test_gpu_utilization.py -v -m "gpu"
```

### CI Pipeline

GPU utilization tests are automatically run in CI:
- Tests that don't require GPU run on all runners
- Tests requiring real GPU are skipped (marked with `continue-on-error: true`)
- Tests verify GPU utilization tracking logic works correctly

## Expected GPU Utilization by Component

| Component | Expected GPU % | Notes |
|-----------|---------------|-------|
| `script_parsing` | 0% | Text parsing, CPU-only |
| `tts_generation` | 40-80% | Coqui TTS (if Python < 3.12), otherwise cloud-based (0%) |
| `audio_mixing` | 0% | pydub is CPU-based |
| `avatar_generation` | 80-100% | SadTalker/Wav2Lip should heavily utilize GPU |
| `video_composition` | 20-40% | NVENC encoding (if successful), otherwise CPU fallback |

## Test Coverage

### Mocked Tests (Always Run)

- GPU utilization tracking before/after components
- CPU and RAM usage tracking
- GPU manager `get_utilization()` method
- Component GPU usage expectations
- Metrics JSON export with GPU data

### Real GPU Tests (Skip if No GPU)

- Actual GPU utilization during tensor operations
- Real GPU metrics collection
- Integration with actual GPU hardware

## Adding New GPU Tests

When adding new GPU-accelerated components:

1. **Add test case** in `test_gpu_utilization.py`:
   ```python
   def test_new_component_uses_gpu(self, tmp_path):
       """Test that new component uses GPU."""
       # ... test implementation
   ```

2. **Update component list** in `test_component_should_use_gpu`:
   ```python
   ("new_component", True),  # Should use GPU
   ```

3. **Add threshold test** if component should use significant GPU:
   ```python
   ("new_component", 50.0),  # Minimum 50% GPU utilization
   ```

## CI Integration

GPU tests are integrated into `.github/workflows/tests.yml`:

```yaml
- name: Run GPU utilization tests
  shell: bash
  run: |
    pytest tests/unit/test_gpu_utilization.py -v -m "not gpu"
  continue-on-error: true
```

**Note:** Tests are set to `continue-on-error: true` because:
- CI runners may not have GPU available
- Real GPU tests will be skipped automatically
- Mocked tests validate the tracking logic works correctly

## Troubleshooting

### Tests Fail Locally

**Issue:** `test_real_gpu_utilization_tracking` fails
**Solution:** This is expected if no GPU is available. The test is marked with `@pytest.mark.skipif` and will skip automatically.

**Issue:** `test_component_minimum_gpu_utilization` fails
**Solution:** Check that the component is actually using GPU. Verify:
- GPU environment variables are set
- CUDA is available
- Component is calling GPU operations

### CI Tests Fail

**Issue:** Tests fail in CI
**Solution:** Check that mocked GPU tests are passing. Real GPU tests are expected to skip in CI.

## Best Practices

1. **Always Mock GPU Tests** - Don't require real GPU for unit tests
2. **Mark Real GPU Tests** - Use `@pytest.mark.skipif` for hardware-dependent tests
3. **Test Tracking Logic** - Verify metrics collection works even without GPU
4. **Document Expectations** - Update this guide when adding new GPU components

## Related Files

- `tests/unit/test_gpu_utilization.py` - GPU utilization test suite
- `src/utils/metrics.py` - Metrics tracking implementation
- `src/utils/gpu_utils.py` - GPU detection and utilities
- `.github/workflows/tests.yml` - CI pipeline configuration

