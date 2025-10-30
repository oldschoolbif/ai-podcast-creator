# Setup Steps - Copy/Paste These Commands

**Copy and paste these commands ONE AT A TIME into your PowerShell.**

---

## Step 1: Create Virtual Environment (30 seconds)

```powershell
cd d:\dev\AI_Podcast_Creator
python -m venv venv
```

**You should see:** A `venv` folder is created (takes 20-30 seconds)

---

## Step 2: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

**You should see:** `(venv)` appears at the start of your prompt

**If you get an error about execution policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

---

## Step 3: Upgrade pip

```powershell
pip install --upgrade pip
```

**You should see:** pip upgrading to latest version

---

## Step 4: Install Main Dependencies (2-5 minutes)

```powershell
pip install -r requirements.txt
```

**You should see:** Lots of packages installing (PyTorch, etc.)
This takes a few minutes - be patient!

---

## Step 5: Install Test Dependencies (1 minute)

```powershell
pip install -r requirements-test.txt
```

**You should see:** Test packages installing (pytest, coverage, etc.)

---

## Step 6: Verify Installation

```powershell
python -m pytest --version
```

**You should see:** `pytest 7.4.3` or similar

---

## Step 7: Run Tests! 🚀

```powershell
python -m pytest -v tests/
```

**You should see:** Tests running and passing!

---

## ✅ What Success Looks Like

```
==================== test session starts ====================
platform win32 -- Python 3.10.x, pytest-7.4.3
collected 25 items

tests/integration/test_pipeline.py::TestSmokeTests::test_all_modules_import PASSED [ 4%]
tests/integration/test_pipeline.py::TestSmokeTests::test_gpu_utils_available PASSED [ 8%]
tests/unit/test_gpu_utils.py::TestGPUManager::test_init_without_gpu PASSED [12%]
... more tests ...

==================== 25 passed in 5.23s ====================
```

---

## 🐛 If Tests Fail

**Don't worry!** That's what testing is for. Tell me:
1. Which tests failed?
2. What error messages?
3. Copy/paste the output

We'll fix them together! 🔧

---

## 📊 After Tests Pass

Try these commands:

```powershell
# Run just smoke tests
python -m pytest -v -m smoke tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest -v tests/unit/test_gpu_utils.py
```

---

## 🎯 Current Status

✅ Test framework created  
✅ 30+ tests written  
✅ Documentation complete  
⏳ Waiting for you to run the setup steps above  

**Start with Step 1!** 🚀

