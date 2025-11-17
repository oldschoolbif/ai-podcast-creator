# Auto-Update Out-of-Date PRs Guide

**Problem:** PRs become out-of-date when main branch gets new commits  
**Solution:** Automatically update PRs by merging main into them

---

## 🚀 Quick Solution

### **Option 1: Run Script Now (Immediate)**
```powershell
# Update all Dependabot PRs
.\scripts\auto_update_prs.ps1

# Update specific PRs
.\scripts\auto_update_prs.ps1 -PRNumbers @(38, 37, 35)

# Update all open PRs (not just Dependabot)
.\scripts\auto_update_prs.ps1 -All
```

### **Option 2: GitHub Actions (Automatic)**
Created `.github/workflows/auto-update-prs.yml` that:
- ✅ Runs every 6 hours automatically
- ✅ Updates all out-of-date Dependabot PRs
- ✅ Can be triggered manually

**To enable:**
1. Commit and push the workflow file
2. It will run automatically every 6 hours
3. Or trigger manually: Actions → "Auto-Update Out-of-Date PRs" → Run workflow

---

## 🔧 How It Works

### **Manual Script:**
1. Checks each PR to see if it's behind main
2. If behind, merges main into the PR branch
3. Updates the PR automatically

### **GitHub Actions:**
1. Runs on schedule (every 6 hours)
2. Finds all Dependabot PRs
3. Checks if they're behind main
4. Updates them automatically

---

## 📋 Dependabot Configuration (Alternative)

You can also configure Dependabot to auto-update PRs:

1. Create/update `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    # Auto-update PRs when base branch changes
    rebase-strategy: "auto"
```

2. Or in GitHub Settings:
   - Settings → Code security and analysis → Dependabot
   - Enable "Auto-merge" for dependency updates

---

## ✅ Current Status

**Script Created:** ✅ `scripts/auto_update_prs.ps1`  
**Workflow Created:** ✅ `.github/workflows/auto-update-prs.yml`  
**Ready to Use:** ✅ Both solutions ready

---

## 🎯 Recommended Approach

**Best Solution:** Use both!
1. **Run script now** to update current PRs
2. **Enable GitHub Actions** for automatic future updates
3. **Configure Dependabot** for long-term automation

---

## 📝 Usage Examples

### **Update All Dependabot PRs Now:**
```powershell
.\scripts\auto_update_prs.ps1
```

### **Update Specific PRs:**
```powershell
.\scripts\auto_update_prs.ps1 -PRNumbers @(38, 37, 35)
```

### **Check Status:**
```powershell
# See which PRs are behind
gh pr list --state open --json number,title,headRefName | ConvertFrom-Json | ForEach-Object {
    $behind = gh api repos/oldschoolbif/ai-podcast-creator/compare/main...$($_.headRefName) --jq '.behind_by'
    if ($behind -gt 0) {
        Write-Host "PR #$($_.number) is $behind commits behind"
    }
}
```

---

**All set! PRs will stay up-to-date automatically.** 🚀

