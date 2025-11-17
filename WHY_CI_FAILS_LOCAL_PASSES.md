# Why CI Errors Continue and Aren't Caught Locally

## Root Cause Analysis

### The Real Problem

**The CI workflow is failing at the "Compare run results" step**, not because pytest is failing, but because **exit codes aren't being captured properly** in GitHub Actions when using `continue-on-error: true`.

### Key Differences

| Aspect | Local | CI |
|--------|-------|-----|
| **Python** | 3.13.9 | 3.11 |
| **pytest** | 7.4.3 | 8.4.2 |
| **OS** | Windows | Ubuntu Linux |
| **Exit Code Check** | Direct (`$LASTEXITCODE`) | GitHub Actions outputs (`$GITHUB_OUTPUT`) |
| **Error Handling** | Normal exit | `continue-on-error: true` |

### Why Local Passes But CI Fails

1. **Different Exit Code Capture:**
   - **Local:** PowerShell directly captures `$LASTEXITCODE` - works immediately
   - **CI:** Uses `GITHUB_OUTPUT` with `continue-on-error: true` - has issues capturing outputs

2. **GitHub Actions Quirk:**
   - When `continue-on-error: true` is set, GitHub Actions may not properly capture output variables if the step would have failed
   - Even though we're exiting with 0, the output variables might not be set correctly

3. **Environment Differences:**
   - Python 3.11 vs 3.13
   - pytest 8.4.2 vs 7.4.3
   - Linux vs Windows
   - These could cause different behaviors, but the main issue is the workflow logic

### What's Actually Happening

The workflow steps show:
- ✅ Pytest run 1: success
- ✅ Pytest run 2: success  
- ❌ Compare run results: failure

This means:
- Pytest is actually running successfully (both runs pass)
- But the exit codes aren't being captured/read properly in the compare step
- The compare step fails because it can't find the exit codes

### Solution

We need to check the debug output from CI run #239 to see:
1. What exit code values are being captured (if any)
2. Whether they're empty strings
3. What the actual error message is

Once we see the debug output, we can fix the workflow properly.

## Immediate Actions

1. ✅ Added extensive debugging to compare step (run #239)
2. ⏳ Wait for debug output to see what's actually happening
3. 🔧 Fix workflow based on actual error messages
4. ✅ Created local simulation script to test workflow logic

## Long-term Fix

Consider simplifying the workflow:
- Remove `continue-on-error` complexity
- Use GitHub Actions' built-in test result features
- Or use a simpler exit code checking mechanism

