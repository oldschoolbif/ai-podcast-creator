# Testing Menu Guide

## 🚀 Quick Start

Run the interactive testing menu:

```powershell
cd D:\dev\AI_Podcast_Creator
.\test_menu.ps1
```

## 📋 Menu Options

### TESTING
- **[1] Run All Unit Tests** - Runs all tests in `tests/unit/` with verbose output
- **[2] Run All Tests with Coverage** - Generates HTML, XML, and terminal coverage reports
- **[3] Run Fast Tests Only** - Skips GPU, network, and slow tests (great for quick checks)
- **[4] Run Specific Test File** - Choose which test file to run from a list

### COVERAGE
- **[5] Show Coverage Report** - Opens the HTML coverage report in your browser
- **[6] Show Coverage Summary** - Shows coverage % in terminal
- **[7] Generate HTML Coverage Report** - Creates interactive HTML report
- **[8] Identify Untested Code** ⭐ - **Shows which files need more tests!**

### CODE QUALITY
- **[9] Show Linter Issues** ⭐ - **Shows code style and syntax issues!**
- **[10] Run Code Quality Checks** - Comprehensive quality analysis (flake8, black, isort)
- **[11] Show Type Checking Issues** - Runs mypy type checker

### UTILITIES
- **[12] List All Tests** - Shows all available test cases
- **[13] Check Test Dependencies** - Verifies pytest and related packages are installed
- **[14] Clean Test Cache** - Removes `.pytest_cache`, `__pycache__`, coverage files
- **[15] Show Test Statistics** - Displays test suite metrics

## 🎯 Most Useful Options

### To See Test Coverage
1. Run option **[2]** - Run Tests with Coverage
2. Then option **[5]** - Show Coverage Report (opens in browser)

### To Find What Tests Are Needed
Run option **[8]** - Identify Untested Code

This will show you:
```
Files needing more test coverage:

File                              Statements  Missing  Coverage
----                              ----------  -------  --------
src/core/some_module.py           150         25       83%
src/utils/helper.py               50          10       80%
```

### To See Code Issues
Run option **[9]** - Show Linter Issues

This will show:
- Syntax errors
- Undefined variables
- Unused imports
- Style violations

## 💡 Tips

### First Time Setup
1. Run option **[13]** to check/install test dependencies
2. Run option **[2]** to generate initial coverage report
3. Run option **[8]** to see what needs testing

### Daily Workflow
```powershell
# Quick check before committing
.\test_menu.ps1
# Choose [3] - Fast tests
# Choose [9] - Linter issues
```

### Deep Analysis
```powershell
# Full test suite with coverage
.\test_menu.ps1
# Choose [2] - Full coverage
# Choose [8] - Untested code
# Choose [10] - Quality checks
```

### Cleaning Up
```powershell
# Remove all test artifacts
.\test_menu.ps1
# Choose [14] - Clean cache
```

## 📊 Understanding Coverage Output

### Coverage Report Example
```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/core/tts_engine.py            234     12    95%     45-52, 89-92
src/core/audio_mixer.py           47      0     100%
src/utils/gpu_utils.py            123     5     96%     178-182
---------------------------------------------------------------
TOTAL                             1234    45    96%
```

- **Stmts**: Total statements in file
- **Miss**: Statements not covered by tests
- **Cover**: Coverage percentage
- **Missing**: Line numbers not tested

### What's Good Coverage?
- **100%** - Perfect! (ideal for critical modules)
- **90-99%** - Excellent (most production code)
- **80-89%** - Good (acceptable for many projects)
- **Below 80%** - Needs more tests

## 🔧 Troubleshooting

### "Virtual environment not found"
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### "pytest not found"
```powershell
.\venv\Scripts\python.exe -m pip install pytest pytest-cov pytest-asyncio
```

### Menu not opening
```powershell
# Run with explicit PowerShell
pwsh -ExecutionPolicy Bypass -File .\test_menu.ps1
```

## 📁 Output Files

After running tests, you'll find:

- `htmlcov/index.html` - Interactive coverage report
- `coverage.xml` - XML coverage data (for CI/CD)
- `.coverage` - Coverage database
- `test_results_full.txt` - Test output log

## 🎨 Color Coding

- **Green (✓)** - Success, passing tests, good coverage
- **Yellow (⚠)** - Warnings, moderate coverage
- **Red (✗)** - Errors, failures, missing tests
- **Cyan** - Headers and sections
- **Magenta** - Menu categories

## 🚀 Next Steps

1. **Run option [2]** to see current coverage
2. **Run option [8]** to identify gaps
3. **Write more tests** for modules with low coverage
4. **Run option [9]** to fix code quality issues
5. **Repeat** until you reach your coverage goal!

Enjoy your comprehensive testing menu! 🎉


