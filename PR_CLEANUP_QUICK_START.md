# PR Cleanup - Quick Start Guide

**Status:** Ready to Execute  
**Created:** After PR #39 Success

---

## 🎯 Quick Summary

- **14 Dependabot PRs** open (dependency updates)
- **PR #39** ✅ Merged (test coverage improvements)
- **Scripts created** for batch merging

---

## 🚀 Fast Track (Recommended)

### **Step 1: Review the Plan**
```powershell
# Read the cleanup plan
cat PR_CLEANUP_PLAN.md
```

### **Step 2: Batch Merge Dependabot PRs**

#### **Option A: Dry Run First (Recommended)**
```powershell
# See what would happen
.\scripts\batch_merge_dependabot.ps1 -DryRun -Group all
```

#### **Option B: Merge by Group (Safest)**
```powershell
# Group 1: Python dependencies
.\scripts\batch_merge_dependabot.ps1 -Group python

# Test after Group 1
pytest tests/ -v

# Group 2: Dev tools
.\scripts\batch_merge_dependabot.ps1 -Group devtools

# Test after Group 2
pytest tests/ -v

# Group 3: GitHub Actions
.\scripts\batch_merge_dependabot.ps1 -Group actions
```

#### **Option C: Merge All at Once (Fast)**
```powershell
# Merge everything (with pauses for testing)
.\scripts\batch_merge_dependabot.ps1 -Group all
```

### **Step 3: Clean Up Local Branches**
```powershell
# Clean up merged branches
.\scripts\cleanup_merged_branches.ps1
```

### **Step 4: Verify Everything Works**
```powershell
# Make sure you're on main
git checkout main
git pull origin main

# Run tests
.\venv\Scripts\Activate.ps1
pytest tests/ -v

# Check status
git status
```

---

## 📋 Manual Alternative

If you prefer manual control:

### **Merge Dependabot PRs:**
```powershell
# Python dependencies
gh pr merge 38 --merge --delete-branch
gh pr merge 37 --merge --delete-branch
gh pr merge 35 --merge --delete-branch
gh pr merge 34 --merge --delete-branch
gh pr merge 32 --merge --delete-branch
gh pr merge 31 --merge --delete-branch
gh pr merge 36 --merge --delete-branch

# Dev tools
gh pr merge 33 --merge --delete-branch
gh pr merge 30 --merge --delete-branch
gh pr merge 29 --merge --delete-branch

# GitHub Actions
gh pr merge 28 --merge --delete-branch
gh pr merge 27 --merge --delete-branch
gh pr merge 26 --merge --delete-branch
gh pr merge 25 --merge --delete-branch
```

### **Clean Up Branches:**
```powershell
git checkout main
git pull origin main
git branch -d qa/avatar-generator-tests
git branch -d feature/waveform-advanced-features
git remote prune origin
```

---

## ⚠️ Important Notes

1. **Test After Each Group** - Don't merge all at once without testing
2. **Check CI** - Make sure CI passes after merging
3. **Backup First** - Consider creating a backup branch: `git branch backup-before-cleanup`
4. **Review PRs** - Quick review of each PR before merging (especially major version bumps)

---

## 🎉 After Cleanup

Once cleanup is complete:
- ✅ All Dependabot PRs merged
- ✅ Local branches cleaned up
- ✅ Main branch up-to-date
- ✅ Ready for new features!

---

**Next:** Start working on new features with a clean slate! 🚀

