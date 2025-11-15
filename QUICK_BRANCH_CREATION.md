# Quick Branch Creation Guide

**Problem:** Branches created from wrong base show "out-of-date" warnings.

**Solution:** Use automated scripts that always create branches from latest main.

---

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)

```powershell
# Creates branch from latest main automatically
.\scripts\create_feature_branch.ps1 -BranchName "feature/my-feature"
```

**What it does:**
1. ✅ Checks for uncommitted changes (prevents data loss)
2. ✅ Fetches latest from remote
3. ✅ Switches to main
4. ✅ Pulls latest changes
5. ✅ Creates new branch from up-to-date main
6. ✅ **No "out-of-date" warnings!**

### Option 2: Git Alias (One-time Setup)

```powershell
# Setup once
.\scripts\git-alias-setup.ps1

# Then use anywhere
git newbranch feature/my-feature
```

### Option 3: Complete Workflow (Branch → Commit → Push → PR)

```powershell
# After making your changes
.\scripts\create_pr_branch.ps1 `
  -BranchName "feature/my-feature" `
  -CommitMessage "feat: Add new feature" `
  -PRTitle "feat: Add new feature" `
  -PRBody "Description of changes"
```

---

## 📋 Manual Steps (If You Prefer)

If you want to do it manually, always follow this order:

```bash
# 1. Fetch latest
git fetch origin

# 2. Switch to main
git checkout main

# 3. Pull latest
git pull origin main

# 4. Create new branch
git checkout -b feature/my-feature
```

**Important:** Always start from `main`, never from another feature branch!

---

## ⚠️ Common Mistakes

### ❌ Wrong Way
```bash
# On feature/other-branch
git checkout -b feature/new-branch  # ❌ Based on old branch!
```

### ✅ Right Way
```bash
# Always start from main
git checkout main
git pull origin main
git checkout -b feature/new-branch  # ✅ Based on latest main!
```

---

## 🔧 Troubleshooting

### "Branch already exists"
```bash
# Switch to existing branch
git checkout feature/my-feature

# Or delete and recreate
git branch -D feature/my-feature
.\scripts\create_feature_branch.ps1 -BranchName "feature/my-feature"
```

### "You have uncommitted changes"
```bash
# Option 1: Commit them
git add .
git commit -m "WIP: Save progress"

# Option 2: Stash them
git stash
# ... create branch ...
git stash pop  # Restore changes

# Option 3: Discard them (careful!)
git restore .
```

---

## 📊 Benefits

- ✅ **No "out-of-date" warnings** - Branch always based on latest main
- ✅ **Consistent workflow** - Same process every time
- ✅ **Less manual work** - Scripts handle the details
- ✅ **Fewer conflicts** - Starting from latest code
- ✅ **Faster PRs** - No need to update branch after creation

---

## 🎯 Best Practice

**Always use the script when creating a new branch:**

```powershell
.\scripts\create_feature_branch.ps1 -BranchName "feature/your-feature"
```

This ensures your branch is always up-to-date from the start!

---

**Last Updated:** 2025-11-14

