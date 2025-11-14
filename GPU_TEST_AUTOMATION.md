# GPU Test Automation Guide

## How We Ensure GPU Tests Run Locally and Frequently

### Current Mechanisms

#### 1. **PowerShell Profile Integration** ✅
- **Location**: `scripts/setup-gpu-testing.ps1`
- **Purpose**: Automatically enables GPU tests in every PowerShell session
- **How it works**:
  - Adds `$env:PY_ENABLE_GPU_TESTS = "1"` to your PowerShell profile
  - Runs automatically when you open a new PowerShell window
  - Ensures GPU tests are enabled by default on GPU machines

**Setup:**
```powershell
.\scripts\setup-gpu-testing.ps1
```

#### 2. **Pre-Push Hook Integration** ✅
- **Location**: `scripts/pre-push.ps1`
- **Purpose**: Runs GPU tests before pushing code
- **How it works**:
  - Checks if GPU is available (`nvidia-smi` command)
  - Checks if GPU tests are enabled (`PY_ENABLE_GPU_TESTS=1`)
  - Runs GPU tests automatically before push
  - **Non-blocking**: GPU test failures don't prevent push (they're optional)

**Usage:**
```powershell
.\scripts\pre-push.ps1  # Runs before git push
```

#### 3. **Dedicated GPU Test Script** ✅
- **Location**: `scripts/test-gpu.ps1`
- **Purpose**: Easy way to run all GPU tests
- **Features**:
  - Auto-enables GPU tests if not set
  - Checks GPU availability
  - Runs all GPU-marked tests
  - Provides clear feedback

**Usage:**
```powershell
.\scripts\test-gpu.ps1
```

#### 4. **Test Environment Script** ✅
- **Location**: `scripts/test_env_example.ps1`
- **Purpose**: Sets up test environment variables
- **Note**: GPU tests disabled by default (line 13), but can be enabled

**To enable:**
```powershell
# Uncomment line 16 in test_env_example.ps1
$env:PY_ENABLE_GPU_TESTS = "1"
```

#### 5. **Weekly Reminder Script** ✅
- **Location**: `scripts/run-gpu-tests-reminder.ps1` (created by setup script)
- **Purpose**: Reminds you to run GPU tests regularly
- **Usage**: Run manually or schedule with Windows Task Scheduler

---

## Frequency Recommendations

### Daily/Before Commits
- **When**: Before pushing GPU-related changes
- **How**: `.\scripts\pre-push.ps1` (automatic)
- **Coverage**: All GPU tests

### Weekly
- **When**: Once per week on GPU machines
- **How**: `.\scripts\run-gpu-tests-reminder.ps1`
- **Coverage**: All GPU tests
- **Purpose**: Catch GPU regressions early

### After GPU Code Changes
- **When**: After modifying GPU-related code
- **How**: `.\scripts\test-gpu.ps1`
- **Coverage**: Specific GPU test files
- **Purpose**: Verify GPU functionality still works

---

## Current Status

### Your System:
- ✅ **GPU Hardware**: NVIDIA GeForce RTX 4060 Laptop GPU (8GB)
- ⚠️ **PyTorch**: Not installed in Windows Python environment
- ⚠️ **CUDA**: Not available (PyTorch required)

### Test Availability:
- **Total GPU Tests**: ~35 tests
  - `test_gpu_utils.py`: 31 tests
  - `test_gpu_utils_real.py`: 4 tests
  - Integration tests: GPU-marked tests available

### Current Behavior:
- GPU tests are **skipped** because:
  1. PyTorch not installed, OR
  2. CUDA not available

---

## Setup Instructions

### Step 1: Install PyTorch with CUDA
```powershell
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 2: Enable GPU Tests
```powershell
# Option A: Run setup script (recommended)
.\scripts\setup-gpu-testing.ps1

# Option B: Manual setup
$env:PY_ENABLE_GPU_TESTS = "1"
```

### Step 3: Verify Setup
```powershell
# Check GPU detection
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Run GPU tests
.\scripts\test-gpu.ps1
```

---

## Automation Strategies

### Strategy 1: PowerShell Profile (Recommended) ✅
**Pros:**
- Automatic on every session
- No manual steps needed
- Works for all developers with GPUs

**Cons:**
- Only works if profile is loaded
- Requires initial setup

**Setup:**
```powershell
.\scripts\setup-gpu-testing.ps1
```

### Strategy 2: Pre-Push Hook ✅
**Pros:**
- Runs automatically before push
- Catches GPU issues before CI
- Non-blocking (doesn't fail push)

**Cons:**
- Only runs before push
- Requires manual git hook setup

**Setup:**
Already configured in `scripts/pre-push.ps1`

### Strategy 3: Scheduled Task (Windows)
**Pros:**
- Runs automatically on schedule
- No manual intervention
- Good for weekly checks

**Cons:**
- Requires Windows Task Scheduler setup
- Only runs when machine is on

**Setup:**
```powershell
# Create scheduled task to run weekly
$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-File D:\dev\AI_Podcast_Creator\scripts\run-gpu-tests-reminder.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -TaskName "AI_Podcast_Creator_GPU_Tests" -Action $action -Trigger $trigger
```

### Strategy 4: Git Hooks
**Pros:**
- Runs automatically on git events
- Can be shared via `.git/hooks/`

**Cons:**
- Requires hook installation
- May slow down git operations

---

## Best Practices

### ✅ Do:
1. **Enable GPU tests in PowerShell profile** on GPU machines
2. **Run GPU tests before pushing** GPU-related changes
3. **Run weekly** to catch regressions
4. **Document GPU requirements** in test docstrings
5. **Use mocking** for GPU tests that don't need real GPU

### ❌ Don't:
1. **Don't require GPU** for basic functionality
2. **Don't fail CI** if GPU tests are skipped
3. **Don't skip GPU tests** if GPU is available
4. **Don't ignore GPU test failures** on GPU machines

---

## Monitoring GPU Test Health

### Check GPU Test Status:
```powershell
# Count GPU tests
pytest tests/unit tests/integration -m gpu --collect-only -q

# Run GPU tests with coverage
$env:PY_ENABLE_GPU_TESTS="1"
pytest tests/unit tests/integration -m gpu --cov=src/utils/gpu_utils -v
```

### Track GPU Test Runs:
- **Before commits**: Check pre-push output
- **Weekly**: Review reminder script output
- **After GPU changes**: Run `test-gpu.ps1` manually

---

## Troubleshooting

### GPU Tests Not Running?
1. Check `PY_ENABLE_GPU_TESTS=1` is set
2. Verify GPU hardware: `nvidia-smi`
3. Check PyTorch: `python -c "import torch; print(torch.cuda.is_available())"`
4. Run setup: `.\scripts\setup-gpu-testing.ps1`

### GPU Tests Skipped?
- **Expected** if:
  - No GPU hardware
  - PyTorch not installed
  - CUDA not available
  - `PY_ENABLE_GPU_TESTS != "1"`

### GPU Tests Failing?
- Check GPU drivers: `nvidia-smi`
- Verify CUDA version matches PyTorch
- Check GPU memory availability
- Review test output for specific errors

---

## Summary

**Current Automation:**
- ✅ PowerShell profile integration (auto-enable)
- ✅ Pre-push hook (runs before push)
- ✅ Dedicated test script (easy manual run)
- ✅ Weekly reminder script (scheduled runs)

**Frequency:**
- **Before push**: Automatic (via pre-push hook)
- **Weekly**: Manual or scheduled
- **After GPU changes**: Manual (via test script)

**Next Steps:**
1. Run `.\scripts\setup-gpu-testing.ps1` to enable GPU tests
2. Install PyTorch with CUDA support
3. Run `.\scripts\test-gpu.ps1` to verify everything works

