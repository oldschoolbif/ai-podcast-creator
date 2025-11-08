# Dependabot PR Cleanup Strategy

## Current Status

**9 Open Dependabot PRs** (all created Oct 30, 2025):
- All show as `MERGEABLE` ✅
- All have 5 checks (status unclear - may need to run)
- Created before your big coverage PR merge

## Recommendation: **Close and Recreate**

Since these were created before your major PR merge and may have stale CI status:

### Option 1: Close All, Let Dependabot Recreate (RECOMMENDED)
**Pros:**
- Fresh PRs based on current `main` branch
- CI will run with latest codebase
- Less risk of conflicts or missed updates

**Commands:**
```powershell
# Close all Dependabot PRs
foreach ($pr in @(1,2,3,4,5,7,8,9,10)) {
    gh pr close $pr --comment "Closing to allow Dependabot to recreate with latest main branch"
}
```

### Option 2: Batch Merge if CI Passes
**Only if:**
- All CI checks show as passed ✅
- You've verified they work with current codebase

**Commands:**
```powershell
# Merge all (only if CI passed)
foreach ($pr in @(1,2,3,4,5,7,8,9,10)) {
    gh pr merge $pr --squash --delete-branch
}
```

### Option 3: Manual Consolidation
- Close all Dependabot PRs
- Manually update `requirements.txt` with all versions
- Create single PR with all updates

## My Recommendation

**Close all 9 PRs** - they're from before your big merge and may have stale checks. Dependabot will automatically recreate them within 24-48 hours based on the current `main` branch.

The updates are:
1. `python-dotenv`: 1.0.0 → 1.2.1
2. `moviepy`: 1.0.3 → 2.2.1 (⚠️ Major version - test carefully!)
3. `loguru`: 0.7.2 → 0.7.3
4. `responses`: 0.24.1 → 0.25.8
5. `librosa`: 0.10.1 → 0.11.0
6. `requests`: 2.31.0 → 2.32.5
7. `faker`: 22.0.0 → 37.12.0 (⚠️ Major version jump!)
8. Testing group (9 updates)
9. Dev-tools group (3 updates)

