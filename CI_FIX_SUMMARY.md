# CI Fix Summary - Test Init Without GPU

## Problem
CI was failing on `test_init_without_gpu` in `tests/unit/test_gpu_utils.py`. The test was using `patch.dict("sys.modules", {"torch": mock_torch})` but if torch was already imported by other tests or modules, the patch wouldn't work correctly.

## Root Cause
When `patch.dict("sys.modules", ...)` is used, it only affects new imports. If `torch` is already imported and cached in `sys.modules`, the existing reference is used instead of the mock.

## Solution
Modified `test_init_without_gpu` to:
1. Remove `torch` from `sys.modules` before patching (if present)
2. Apply the patch as before
3. Restore `torch` after the test completes (if it was there)

This matches the pattern already used in `test_init_without_pytorch` in the same file.

## Changes Made
- `tests/unit/test_gpu_utils.py`: Updated `test_init_without_gpu` to properly handle torch module cleanup

## Testing
- ✅ Test passes locally
- ✅ All tests in `test_gpu_utils.py` pass locally
- ⏳ Waiting for CI to confirm fix

## Next Steps
1. Monitor CI run #248 to confirm fix
2. If still failing, fetch actual CI logs to see exact error
3. Consider applying same pattern to other similar tests if needed

