# 🛠️ IDE Auto-Formatting Setup Guide
**Date:** 2025-10-30  
**Status:** Ready to Configure

---

## 🎯 What This Does

- ✅ **Auto-format on save** (Black formatter)
- ✅ **Auto-sort imports** (isort)
- ✅ **Real-time linting** (Flake8)
- ✅ **Integrated testing** (pytest)
- ✅ **Type checking** (basic)

---

## 📝 VS Code / Cursor Setup

### Step 1: Create `.vscode/settings.json`

Create a file at `.vscode/settings.json` with this content:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=120"],
  "editor.formatOnSave": true,
  
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=120",
    "--ignore=E203,W503,E402,F401,F811"
  ],
  
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  },
  "python.sortImports.args": ["--profile=black"],
  
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests", "--tb=short", "-v"],
  
  "editor.rulers": [120],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/htmlcov": true
  }
}
```

### Step 2: Install Required Extensions

In VS Code/Cursor, press `Ctrl+Shift+X` and install:

1. **Python** (Microsoft) - Already installed
2. **Pylance** (Microsoft) - Should be bundled
3. **Optional but recommended:**
   - **Better Comments** (Aaron Bond)
   - **GitLens** (GitKraken)
   - **Test Explorer UI** (Holger Benl)

### Step 3: Verify Setup

1. Open any Python file
2. Make a small change
3. Press `Ctrl+S` to save
4. **Code should auto-format!** ✨

---

## 🐍 PyCharm Setup

### Step 1: Configure Black

1. Go to: `File` → `Settings` → `Tools` → `External Tools`
2. Click **+** to add a new tool
3. Configure:
   - **Name:** Black Formatter
   - **Program:** `$PyInterpreterDirectory$/black`
   - **Arguments:** `$FilePath$ --line-length=120`
   - **Working Directory:** `$ProjectFileDir$`
4. Click **OK**

### Step 2: Configure File Watcher

1. Go to: `File` → `Settings` → `Tools` → `File Watchers`
2. Click **+** → **Custom**
3. Configure:
   - **Name:** Black
   - **File type:** Python
   - **Scope:** Project Files
   - **Program:** `$PyInterpreterDirectory$/black`
   - **Arguments:** `$FilePath$ --line-length=120`
   - **Output paths:** `$FilePath$`
4. Click **OK**

### Step 3: Configure Flake8

1. Go to: `File` → `Settings` → `Editor` → `Inspections`
2. Enable: **Python** → **PEP 8 coding style violation**
3. Set extra options: `--max-line-length=120 --ignore=E203,W503,E402,F401,F811`

### Step 4: Configure isort

1. Go to: `File` → `Settings` → `Tools` → `External Tools`
2. Click **+** to add a new tool
3. Configure:
   - **Name:** isort
   - **Program:** `$PyInterpreterDirectory$/isort`
   - **Arguments:** `$FilePath$ --profile=black`
   - **Working Directory:** `$ProjectFileDir$`

---

## 🧪 Testing It Works

### Test 1: Auto-Formatting

1. Open `src/core/script_parser.py`
2. Add some messy code:
   ```python
   def test(   ):
       x=1+2
       return    x
   ```
3. Press `Ctrl+S` (or `Cmd+S` on Mac)
4. Should auto-format to:
   ```python
   def test():
       x = 1 + 2
       return x
   ```

### Test 2: Auto-Import Sorting

1. Open any file with imports
2. Mess up the import order:
   ```python
   import sys
   from pathlib import Path
   import os
   ```
3. Right-click → **Organize Imports** (or save if configured)
4. Should sort to:
   ```python
   import os
   import sys
   from pathlib import Path
   ```

### Test 3: Real-Time Linting

1. Type this deliberately bad code:
   ```python
   def bad_function():
       unused_var = 5
       x=1+2
   ```
2. You should see squiggly lines under issues
3. Hover to see Flake8 warnings

### Test 4: Integrated Testing

1. Open Testing panel (beaker icon in sidebar)
2. Click **Configure Tests** → **pytest**
3. Tests should appear in a tree view
4. Click any test to run it
5. See pass/fail status inline

---

## ⌨️ Keyboard Shortcuts

### VS Code / Cursor
```
Ctrl+S           - Save & Auto-format
Shift+Alt+F      - Manual format
Ctrl+Shift+P     - Command palette
  → "Format Document"
  → "Organize Imports"
Ctrl+Shift+`     - Open terminal
F5               - Run/Debug
```

### PyCharm
```
Ctrl+Alt+L       - Reformat Code
Ctrl+Alt+O       - Optimize Imports
Ctrl+Shift+A     - Find Action
Shift+F10        - Run
Shift+F9         - Debug
```

---

## 🎨 Optional: Color Themes

### Recommended for Python Development

**VS Code:**
- **Dark+** (default) - Good contrast
- **Monokai Pro** - Popular, colorful
- **One Dark Pro** - Atom-inspired
- **Night Owl** - Easy on the eyes

**PyCharm:**
- **Darcula** (default) - Professional
- **High Contrast** - Maximum visibility
- **Material Theme** - Modern, colorful

---

## 🔧 Troubleshooting

### "Black not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install black
```

### "Flake8 not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install flake8
```

### "isort not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install isort
```

### Auto-format not working
1. Check that Python interpreter is set to `venv`
2. Check that Black is installed in venv
3. Reload window: `Ctrl+Shift+P` → "Reload Window"

### Linting too strict
Edit `.vscode/settings.json` and add more ignores:
```json
"python.linting.flake8Args": [
  "--max-line-length=120",
  "--ignore=E203,W503,E402,F401,F811,W293"
]
```

---

## 📊 What Each Tool Does

### Black
- **What:** Code formatter
- **Why:** Enforces consistent style
- **When:** On save (automatic)
- **Config:** Line length 120, PEP 8 compliant

### isort
- **What:** Import sorter
- **Why:** Organizes imports alphabetically
- **When:** On save or manual
- **Config:** Black-compatible profile

### Flake8
- **What:** Style checker (linter)
- **Why:** Catches style violations
- **When:** Real-time as you type
- **Config:** Max line 120, ignores common false positives

### pytest
- **What:** Test runner
- **Why:** Run tests from IDE
- **When:** On-demand (click to run)
- **Config:** Uses `pytest.ini` from project

---

## 🎯 Expected Behavior

Once configured, this happens **automatically**:

1. **You type code** → Flake8 shows issues in real-time
2. **You save (`Ctrl+S`)** → Black formats, isort sorts imports
3. **You commit** → Pre-commit hooks run (from our CI/CD setup)
4. **You push** → GitHub Actions run full test suite

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Opening a Python file shows syntax highlighting
- [ ] Saving a file auto-formats the code
- [ ] Messy imports get auto-sorted on save
- [ ] Linting issues show squiggly lines
- [ ] Tests appear in test explorer panel
- [ ] Terminal opens in venv (shows `(venv)` prefix)
- [ ] Hovering over code shows type hints
- [ ] Ctrl+Click on imports jumps to definition

---

## 🚀 You're All Set!

Your IDE is now configured for:
- ✅ **Auto-formatting** (Black)
- ✅ **Import sorting** (isort)
- ✅ **Real-time linting** (Flake8)
- ✅ **Integrated testing** (pytest)
- ✅ **Type hints** (Pylance/PyCharm)

**Happy coding!** 🎉

---

## 📚 Further Reading

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [VS Code Python Guide](https://code.visualstudio.com/docs/python/python-tutorial)
- [PyCharm Python Guide](https://www.jetbrains.com/help/pycharm/quick-start-guide.html)

---

*Created: 2025-10-30*  
*Last Updated: 2025-10-30*  
*Version: 1.0*

