# Check Branch Updates Before Proceeding

## Critical Workflow Step
**ALWAYS check if PR branch is up-to-date with main before proceeding with next work.**

## When to Check
1. **Before starting new work** - Check if current PR branch needs updating
2. **After PR is created** - Verify branch is up-to-date
3. **Before monitoring for merge** - Ensure branch is current
4. **When CI checks are pending** - Branch might be out-of-date

## How to Check
```powershell
# Check PR status
gh pr view <PR_NUMBER> --json state,mergeable,isDraft

# Check if branch is behind
git fetch origin main
git log HEAD..origin/main --oneline

# Update branch if needed
git checkout <branch-name>
git merge origin/main --no-edit
git push
```

## GitHub CLI Check
```powershell
# Check if PR is behind
gh pr view <PR_NUMBER> --json headRefName,baseRefName,isDraft
# If shows "This branch is out-of-date" warning, update it
```

## Workflow Integration
Before starting new coverage improvement:
1. ✅ Check if previous PR branch is up-to-date
2. ✅ Update if needed
3. ✅ Then proceed with next work

## Why This Matters
- Out-of-date branches cause CI delays
- Can cause merge conflicts
- Slows down the workflow
- User explicitly requested this check

