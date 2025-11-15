# Workflow Recommendations - Preventing PR Cleanup Mess

**Problem:** Large batches of PRs created conflicts and cleanup issues that took days to resolve.

**Solution:** Implement a more frequent, incremental workflow with smaller changes and faster feedback loops.

---

## 🎯 Core Principles

### 1. **Small, Frequent Commits**
- ✅ Commit and push after each logical unit of work
- ✅ Don't wait for "perfect" - push working code frequently
- ✅ Smaller commits = easier review, fewer conflicts

### 2. **One PR Per Feature/Fix**
- ✅ Create PR immediately after feature is complete
- ✅ Don't batch multiple unrelated changes
- ✅ Merge quickly after CI passes

### 3. **Fast Feedback Loops**
- ✅ Run tests locally before pushing
- ✅ Push frequently to trigger CI early
- ✅ Fix issues as they arise, not in batches

### 4. **Proactive Branch Management**
- ✅ Update branches before they fall behind
- ✅ Use auto-update workflow (already in place)
- ✅ Monitor PR status regularly

---

## 📋 Recommended Workflow

### Daily Development Cycle

```
1. Start work on feature/fix
   ↓
2. Make small, logical changes
   ↓
3. Run tests locally (pytest)
   ↓
4. Commit with clear message
   ↓
5. Push to branch
   ↓
6. CI runs automatically
   ↓
7. Fix any issues immediately
   ↓
8. Repeat steps 2-7 until feature complete
   ↓
9. Create PR when feature is done
   ↓
10. Monitor CI, merge when green
```

### Key Practices

#### ✅ DO:
- **Push after each logical change** (even if feature isn't complete)
- **Run tests locally** before pushing
- **Create PR early** (can mark as draft if not ready)
- **Update branch** if it falls behind
- **Merge quickly** after CI passes
- **One feature per PR** (easier to review and merge)

#### ❌ DON'T:
- **Don't batch multiple features** in one PR
- **Don't wait days** before pushing
- **Don't let PRs pile up** (merge or close quickly)
- **Don't ignore CI failures** (fix immediately)
- **Don't create huge PRs** (hard to review, more conflicts)

---

## 🔧 Implementation Strategy

### For Coverage Improvements (Current Task)

**Instead of:**
- Working on coverage for days
- Creating one huge PR with all coverage improvements
- Dealing with conflicts when merging

**Do this:**
1. **Pick one module** (e.g., `src/core/tts_engine.py`)
2. **Add tests for that module** (aim for 60%+ coverage)
3. **Run tests locally** - ensure they pass
4. **Commit and push** immediately
5. **Create PR** - "Increase coverage for tts_engine"
6. **Merge when CI passes** (usually within minutes)
7. **Repeat** for next module

**Benefits:**
- ✅ Small, focused PRs merge quickly
- ✅ No conflicts (each PR is independent)
- ✅ Fast feedback (CI runs on each push)
- ✅ Easy to review (one module at a time)
- ✅ Progress is visible (multiple small PRs)

### For Feature Development

**Instead of:**
- Working on feature for days
- Creating PR with all changes at once
- Waiting for review, dealing with conflicts

**Do this:**
1. **Break feature into small steps**
2. **Complete one step** (e.g., add function, add tests)
3. **Commit and push** immediately
4. **CI runs** - fix issues if any
5. **Continue to next step**
6. **Create PR** when feature is complete
7. **Merge quickly** after CI passes

**Benefits:**
- ✅ Continuous integration (CI runs on each push)
- ✅ Early feedback on issues
- ✅ Smaller, easier-to-review PRs
- ✅ Less risk of conflicts

---

## 🚀 Quick Start Guide

### Step 1: Before Starting Work

**Option A: Use the automated script (Recommended)**
```powershell
# Creates branch from latest main automatically
.\scripts\create_feature_branch.ps1 -BranchName "feature/coverage-tts-engine"
```

**Option B: Use git alias (after setup)**
```bash
# First time: Run setup script
.\scripts\git-alias-setup.ps1

# Then use alias
git newbranch feature/coverage-tts-engine
```

**Option C: Manual (if you prefer)**
```bash
# Make sure you're on latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/coverage-tts-engine
```

### Step 2: Make Changes

```bash
# Make your changes (add tests, fix code, etc.)
# ...

# Run tests locally
python -m pytest tests/unit/test_tts_engine.py -v

# Check coverage
python -m pytest --cov=src/core/tts_engine --cov-report=term-missing
```

### Step 3: Commit and Push

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "test: Add coverage for tts_engine.generate() method"

# Push immediately
git push origin feature/coverage-tts-engine
```

### Step 4: Create PR (if feature complete)

```bash
# Create PR via GitHub CLI
gh pr create --title "test: Increase coverage for tts_engine" --body "Adds tests for generate() method, increases coverage to 65%"

# Or create via GitHub web UI
```

### Step 5: Monitor and Merge

```bash
# Check CI status
gh pr checks

# When green, merge
gh pr merge --squash --delete-branch
```

---

## 📊 Workflow Comparison

### Old Workflow (Caused Problems)
```
Day 1-3: Work on multiple features
Day 4: Create 8 PRs at once
Day 5-7: Deal with conflicts, update branches
Day 8: Finally merge everything
```
**Problems:**
- ❌ PRs pile up
- ❌ Conflicts multiply
- ❌ Takes days to clean up
- ❌ Hard to track progress

### New Workflow (Recommended)
```
Day 1: Feature 1 → PR → Merge (30 min)
Day 1: Feature 2 → PR → Merge (30 min)
Day 1: Feature 3 → PR → Merge (30 min)
...
```
**Benefits:**
- ✅ PRs merge quickly
- ✅ No conflicts (each is independent)
- ✅ Fast feedback
- ✅ Progress is visible

---

## 🛠️ Tools & Automation

### Already in Place ✅

1. **Auto-Update PRs Workflow**
   - Runs every 6 hours
   - Updates out-of-date PRs automatically
   - Prevents PRs from falling behind

2. **Auto-Merge**
   - Enabled on Dependabot PRs
   - Merges automatically when CI passes
   - Reduces manual work

3. **Comprehensive CI/CD**
   - Tests run on every push
   - Coverage reported automatically
   - Quality gates prevent bad code

### New Automation Tools ✅

1. **`create_feature_branch.ps1`** - Automated Branch Creation
   ```powershell
   # Always creates branch from latest main
   .\scripts\create_feature_branch.ps1 -BranchName "feature/my-feature"
   ```
   - ✅ Fetches latest from remote
   - ✅ Switches to main
   - ✅ Pulls latest changes
   - ✅ Creates new branch from up-to-date main
   - ✅ **Prevents "out-of-date" warnings!**

2. **`create_pr_branch.ps1`** - Complete Workflow Automation
   ```powershell
   # Complete workflow: branch → commit → push → PR
   .\scripts\create_pr_branch.ps1 -BranchName "feature/my-feature" `
     -CommitMessage "feat: Add new feature" `
     -PRTitle "feat: Add new feature" `
     -PRBody "Description of changes"
   ```

3. **Git Aliases** - Quick Commands
   ```bash
   # Setup once
   .\scripts\git-alias-setup.ps1
   
   # Then use
   git newbranch feature/my-feature
   ```

### Recommended Additions

1. **Pre-commit Hooks** (optional)
   ```bash
   # Run tests before commit
   pre-commit install
   ```

2. **Local Test Script**
   ```bash
   # Quick test before pushing
   ./scripts/quick_test.sh
   ```

3. **Coverage Gate** (already in place)
   - Fails if coverage drops
   - Prevents regression

---

## 📈 Expected Outcomes

### With New Workflow:

- **PR Merge Time:** 30-60 minutes (vs. days)
- **Conflict Rate:** Near zero (small, frequent PRs)
- **CI Feedback:** Immediate (runs on each push)
- **Code Quality:** Maintained (tests run frequently)
- **Developer Experience:** Much better (fast feedback)

### Metrics to Track:

- Average PR size (lines changed)
- Time from PR creation to merge
- Number of conflicts per PR
- CI pass rate
- Coverage trend over time

---

## 🎯 Action Plan

### Immediate (This Session)

1. ✅ Fix failing tests (done)
2. 🔄 Increase coverage incrementally (in progress)
   - Pick one module
   - Add tests
   - Push and create PR
   - Merge when green
   - Repeat

### Short-Term (This Week)

1. **Adopt new workflow** for all new work
2. **Break down large tasks** into smaller PRs
3. **Push frequently** (at least daily)
4. **Monitor PR status** (don't let them pile up)

### Long-Term (Ongoing)

1. **Maintain workflow discipline**
2. **Review and optimize** based on experience
3. **Share best practices** with team
4. **Track metrics** to measure improvement

---

## 💡 Tips & Tricks

### Quick Commands

```bash
# Check what needs to be committed
git status

# See what changed
git diff

# Run tests before pushing
python -m pytest -q

# Push and create PR in one go
git push origin feature/my-feature && gh pr create --fill
```

### When to Push

- ✅ After adding a test that passes
- ✅ After fixing a bug
- ✅ After completing a small feature
- ✅ Before end of day (save progress)
- ✅ After CI passes on previous push

### When NOT to Push

- ❌ When tests are failing (fix first)
- ❌ When code doesn't compile (fix first)
- ❌ When you're in the middle of a refactor (complete first)

---

## 📝 Summary

**Key Takeaway:** Small, frequent PRs merge quickly and avoid conflicts. Large batches cause problems.

**Action:** Start using this workflow immediately for coverage improvements and all future work.

**Goal:** Merge PRs within hours, not days. Keep the kitchen clean!

---

**Last Updated:** 2025-11-14  
**Status:** Ready to implement

