# Why CI Errors Aren't Caught Locally

## The Problem

**Local Environment:**
- Python 3.13.9
- pytest 7.4.3
- Windows PowerShell
- Direct exit code checking

**CI Environment:**
- Python 3.11
- pytest 8.4.2 (from requirements.txt)
- Ubuntu Linux / bash
- GitHub Actions output variable capture

## Key Differences

### 1. **Exit Code Capture Mechanism**

**Local (`check_ci_locally.ps1`):**
```powershell
$result1 = python -m pytest -q 2>&1
$exitCode1 = $LASTEXITCODE  # Direct PowerShell variable
```

**CI (GitHub Actions):**
```bash
pytest -q | tee pytest_run1.log
exit_code=${PIPESTATUS[0]}  # Capture from pipe
echo "exit_code=${exit_code}" >> "$GITHUB_OUTPUT"  # Store in GitHub Actions outputs
exit 0  # Always exit 0 with continue-on-error
```

The CI workflow uses `continue-on-error: true` and captures exit codes via `GITHUB_OUTPUT`, which behaves differently than direct exit code checking.

### 2. **Pytest Version Difference**

- **Local:** pytest 7.4.3
- **CI:** pytest 8.4.2

Pytest 8.x has breaking changes and different behavior that might cause issues.

### 3. **Python Version Difference**

- **Local:** Python 3.13.9
- **CI:** Python 3.11

Different Python versions can have different behaviors, especially with:
- Import resolution
- Exception handling
- Warning behavior

### 4. **Operating System Differences**

- **Local:** Windows
- **CI:** Ubuntu Linux

Different:
- File paths
- Shell behavior
- Environment variable handling
- Process management

## Why Tests Pass Locally But Fail in CI

1. **The workflow logic itself is failing** - The "Compare run results" step is failing because exit codes aren't being captured properly in GitHub Actions with `continue-on-error: true`

2. **Pytest version differences** - pytest 8.4.2 might have different behavior than 7.4.3

3. **Environment differences** - Python 3.11 vs 3.13, Linux vs Windows

## Solutions

### Option 1: Match CI Environment Locally
- Use Python 3.11
- Install pytest 8.4.2
- Use WSL or Docker to match Linux environment

### Option 2: Fix the Workflow
- The current issue is that exit codes aren't being captured properly
- We've added debugging to diagnose the issue
- Once we see the debug output, we can fix the workflow

### Option 3: Simplify the Workflow
- Remove `continue-on-error` complexity
- Use simpler exit code checking
- Or use GitHub Actions' built-in test result features

## Next Steps

1. Wait for CI run #239 to see debug output
2. Analyze what's actually failing
3. Fix the workflow based on actual error messages
4. Update local simulation script to match CI exactly

