# CI/CD Setup Guide 🚀

## Quick Start (5 minutes)

### 1. Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Test it works
pre-commit run --all-files
```

**Done!** Now your code will be automatically:
- ✅ Formatted with Black
- ✅ Linted with Flake8
- ✅ Tested (fast tests) before commit
- ✅ Security scanned with Bandit

---

## What You Just Got ✨

### 🤖 GitHub Actions CI
**Location:** `.github/workflows/`

**3 Workflows:**
1. **`tests.yml`** - Runs on every push/PR
   - Tests on Python 3.10, 3.11, 3.12
   - Tests on Ubuntu + Windows
   - Coverage reporting
   - Security scanning
   - Code quality checks

2. **`codecov.yml`** - Coverage tracking
   - Uploads to Codecov
   - Posts PR comments with coverage
   - Generates coverage badges

3. **`quality-advanced.yml`** - Weekly deep scans
   - Mutation testing
   - Type checking (MyPy)
   - Performance tests
   - Dependency audits

### 🎯 Pre-commit Hooks
**Location:** `.pre-commit-config.yaml`

**Runs automatically on commit:**
- Removes trailing whitespace
- Fixes line endings
- Formats with Black
- Sorts imports with isort
- Lints with Flake8
- Security scan with Bandit
- Runs fast unit tests

**Bypass if needed:**
```bash
git commit -m "message" --no-verify
```

### ⚙️ Configuration
**Location:** `pyproject.toml`

Centralizes all tool configs:
- Black (formatting)
- isort (import sorting)
- pytest (testing)
- coverage (coverage reporting)
- Bandit (security)
- MyPy (type checking)

---

## GitHub Setup (Optional - 10 minutes)

### 1. Enable GitHub Actions
Already enabled if you pushed! Check:
- Go to your repo → Actions tab
- You should see workflows running

### 2. Add Branch Protection (Recommended)
Go to: `Settings → Branches → Add branch protection rule`

**For `main` branch:**
- ✅ Require pull request reviews (1 reviewer)
- ✅ Require status checks to pass:
  - `Test Python 3.11 (ubuntu-latest)`
  - `Coverage Gate`
  - `Security Scan`
- ✅ Require branches to be up to date
- ✅ Include administrators
- ❌ Allow force pushes (leave unchecked)

### 3. Set up Codecov (Optional - Better Coverage Tracking)

**Free for public repos!**

1. Go to https://codecov.io/
2. Sign in with GitHub
3. Add your repository
4. Copy the upload token
5. Add to GitHub repo:
   - `Settings → Secrets → New repository secret`
   - Name: `CODECOV_TOKEN`
   - Value: (paste token)

**Benefits:**
- Coverage trends over time
- Beautiful visualizations
- PR coverage comments
- Coverage badges

---

## Developer Workflow

### Before You Commit
```bash
# Pre-commit hooks run automatically, but you can test manually:
pre-commit run --all-files

# Or run tests manually:
pytest tests/unit -x --tb=short

# Check coverage:
pytest --cov=src --cov-report=term
```

### Before You Push
```bash
# Run full test suite:
pytest

# Check coverage:
pytest --cov=src --cov-report=html
# Opens in browser: file:///.../htmlcov/index.html
```

### Creating a PR
1. Push your branch
2. Create PR on GitHub
3. **Wait for CI checks** (2-5 minutes)
4. If checks fail:
   - Click "Details" to see error
   - Fix locally
   - Push again (CI re-runs automatically)

### What CI Checks

| Check | What It Does | Time |
|-------|-------------|------|
| **Tests** | Runs all 286 tests | ~2 min |
| **Coverage** | Checks coverage ≥30% | ~2 min |
| **Security** | Scans for vulnerabilities | ~1 min |
| **Linting** | Checks code style | ~30s |
| **Quality** | Code complexity analysis | ~30s |

---

## Advanced Usage

### Running Specific Tests

```bash
# Fast tests only:
pytest tests/unit -x --maxfail=3

# Integration tests:
pytest tests/integration

# Specific module:
pytest tests/unit/test_tts_engine.py

# Specific test:
pytest tests/unit/test_tts_engine.py::test_generate_with_different_tld

# With coverage:
pytest tests/unit --cov=src/core/tts_engine

# Parallel execution (faster):
pytest -n auto
```

### Security Scanning

```bash
# Scan for security issues:
bandit -r src/

# Check dependencies:
pip install safety
safety check

# Full audit:
pip install pip-audit
pip-audit
```

### Code Quality

```bash
# Check complexity:
pip install radon
radon cc src/ -a -nb

# Maintainability index:
radon mi src/

# Type checking:
pip install mypy
mypy src/ --config-file=pyproject.toml
```

### Mutation Testing (Test Your Tests!)

```bash
# Install:
pip install mutmut

# Run on specific file:
mutmut run --paths-to-mutate=src/core/audio_mixer.py

# Show results:
mutmut show

# Generate HTML report:
mutmut html
```

---

## Troubleshooting

### Pre-commit hooks failing?

```bash
# Update hooks:
pre-commit autoupdate

# Clean and reinstall:
pre-commit uninstall
pre-commit install
pre-commit run --all-files
```

### CI tests passing locally but failing in GitHub?

**Common causes:**
1. **Different Python version**
   - CI tests Python 3.10, 3.11, 3.12
   - Check: `python --version`

2. **Missing dependencies**
   - CI installs from `requirements.txt`
   - Check: `pip freeze > requirements.txt`

3. **OS differences**
   - CI tests Ubuntu + Windows
   - Path separators, line endings, etc.

4. **Environment variables**
   - CI doesn't have your local config
   - Check for hardcoded paths

### Coverage dropping?

```bash
# See what's not covered:
pytest --cov=src --cov-report=term-missing

# HTML report (easier to read):
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Maintenance

### Updating Dependencies

```bash
# Check outdated:
pip list --outdated

# Update pre-commit hooks (do this monthly):
pre-commit autoupdate

# Update GitHub Actions (check for new versions):
# .github/workflows/*.yml - bump version numbers
```

### Adding New Tests

1. Write test in `tests/unit/` or `tests/integration/`
2. Run locally: `pytest tests/unit/test_your_new_test.py`
3. Check coverage: `pytest --cov=src/your_module`
4. Commit (pre-commit runs fast tests)
5. Push (CI runs full suite)

---

## Metrics & Monitoring

### View Test Reports

**After each CI run:**
1. Go to GitHub Actions
2. Click on the workflow run
3. Scroll down to "Artifacts"
4. Download: `test-report-*.html`
5. Open in browser

### View Coverage

**Option 1: Codecov (if set up)**
- https://codecov.io/gh/YOUR_USERNAME/AI_Podcast_Creator

**Option 2: Artifacts**
- GitHub Actions → Workflow run → Artifacts → `coverage-report`

**Option 3: Local**
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Track Quality Trends

**Weekly Report (automated):**
- Runs every Monday at 3am UTC
- Check: Actions → Advanced Quality Checks
- Downloads: mutation reports, type checking results

---

## Best Practices

### ✅ Do:
- Run tests before pushing
- Keep tests fast (<2 min for full suite)
- Fix failing tests immediately
- Review coverage on new code
- Update dependencies regularly
- Let CI catch issues (don't bypass)

### ❌ Don't:
- Push broken tests
- Skip pre-commit hooks (without good reason)
- Ignore security warnings
- Let coverage drop below 30%
- Force push to main
- Bypass branch protection

---

## Help & Resources

### Documentation
- pytest: https://docs.pytest.org/
- pre-commit: https://pre-commit.com/
- GitHub Actions: https://docs.github.com/actions
- Codecov: https://docs.codecov.com/

### Getting Help
1. Check CI logs for error details
2. Run locally with same command as CI
3. Check this guide's troubleshooting section
4. Ask team for help

### Quick Reference Card

```bash
# Essential Commands
pre-commit run --all-files   # Run all pre-commit hooks
pytest                        # Run all tests
pytest -x --tb=short         # Stop on first failure
pytest --cov=src             # Run with coverage
bandit -r src/               # Security scan
black src/ tests/            # Format code
flake8 src/                  # Lint code

# Before Commit
pre-commit run --all-files

# Before Push
pytest && echo "✅ Ready to push!"

# After Pull
pip install -r requirements.txt  # Update deps
```

---

## Status

**Current Setup:** ✅ **COMPLETE**

- ✅ GitHub Actions CI
- ✅ Pre-commit hooks
- ✅ Security scanning
- ✅ Coverage tracking
- ✅ Code quality checks
- ✅ Advanced quality scans (weekly)

**Next Steps (Optional):**
- Set up Codecov account
- Enable branch protection
- Add mutation testing to CI
- Add GUI E2E tests

---

*Last Updated: 2025-10-29*  
*Version: 1.0*

