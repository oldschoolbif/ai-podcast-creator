# 🚀 CI/CD Quick Start (5 Minutes)

## One-Time Setup

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Run setup script
.\scripts\setup_dev_tools.ps1
```

**That's it!** ✅ You now have:
- ✅ Automatic code formatting (Black)
- ✅ Automatic linting (Flake8)
- ✅ Automatic security scanning (Bandit)
- ✅ Fast tests run before commit
- ✅ GitHub Actions CI on push

---

## Daily Workflow

### Before You Start Coding
```powershell
git pull
```

### While Coding
**Code as normal!** Pre-commit hooks will auto-fix most issues.

### Before You Commit
```powershell
# Optional: run fast tests manually
.\scripts\test-fast.ps1
```

Then commit normally:
```powershell
git add .
git commit -m "Your message"
# Hooks run automatically here ✨
```

### Before You Push
```powershell
# Recommended: ensure CI will pass
.\scripts\pre-push.ps1
```

Then push:
```powershell
git push
```

**GitHub Actions will:**
- ✅ Run all 286 tests
- ✅ Check coverage ≥30%
- ✅ Security scan
- ✅ Post results on PR

---

## Useful Commands

```powershell
# Run all tests
.\scripts\test.ps1

# Run fast tests only
.\scripts\test-fast.ps1

# Generate coverage report (opens in browser)
.\scripts\coverage.ps1

# Run linting
.\scripts\lint.ps1

# Run security scan
.\scripts\security.ps1

# Pre-push checks (recommended before pushing)
.\scripts\pre-push.ps1
```

---

## What Happens Automatically

### On Every Commit (Pre-commit hooks)
1. Formats code with Black
2. Sorts imports with isort
3. Lints with Flake8
4. Security scan with Bandit
5. Runs fast unit tests

**Time:** ~10-30 seconds

### On Every Push (GitHub Actions)
1. Tests on Python 3.10, 3.11, 3.12
2. Tests on Ubuntu + Windows
3. Full test suite (286 tests)
4. Coverage check (≥30%)
5. Security scans
6. Code quality checks

**Time:** ~2-5 minutes

---

## Troubleshooting

### Commit blocked by pre-commit?
```powershell
# See what failed
pre-commit run --all-files

# Fix formatting issues automatically
black src/ tests/
isort --profile=black src/ tests/

# Bypass if urgent (not recommended)
git commit -m "message" --no-verify
```

### CI failing on GitHub but passing locally?
1. Check Python version: `python --version` (CI uses 3.10, 3.11, 3.12)
2. Update dependencies: `pip install -r requirements.txt`
3. Run full suite: `.\scripts\test.ps1`

### Pre-commit hooks not running?
```powershell
# Reinstall hooks
pre-commit uninstall
pre-commit install
pre-commit run --all-files
```

---

## Pro Tips 💡

1. **Run `.\scripts\pre-push.ps1` before pushing** - Saves time by catching issues locally
2. **Check CI status before merging** - Green checkmark ✅ means good to merge
3. **Review coverage on new code** - Keep it above 30%
4. **Let hooks fix formatting** - Don't fight Black, it's consistent
5. **Security warnings are important** - Review Bandit findings

---

## Full Documentation

- **Setup Guide:** `CI_CD_SETUP_GUIDE.md` (comprehensive)
- **QA Roadmap:** `QA_EXCELLENCE_ROADMAP.md` (future improvements)
- **Test Status:** `TEST_COVERAGE_FINAL_REPORT.md` (current coverage)

---

## Status Check

✅ **Pre-commit installed?**
```powershell
pre-commit --version
```

✅ **Hooks working?**
```powershell
pre-commit run --all-files
```

✅ **Tests passing?**
```powershell
.\scripts\test-fast.ps1
```

✅ **Ready to push?**
```powershell
.\scripts\pre-push.ps1
```

---

## Questions?

Check `CI_CD_SETUP_GUIDE.md` for detailed help!

---

*Last updated: 2025-10-29*

