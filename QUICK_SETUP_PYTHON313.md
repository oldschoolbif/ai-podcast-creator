# Quick Setup with Python 3.13

**You have Python 3.13.9 installed - perfect!**

## ✅ Run These Commands (Copy/Paste):

```powershell
# Navigate
cd d:\dev\AI_Podcast_Creator

# Create venv with Python 3.13
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install test dependencies
pip install -r requirements-test.txt

# Verify pytest
python -m pytest --version

# Run tests!
python -m pytest -v tests/
```

---

## 🎯 Expected Output:

After running tests, you should see:
```
==================== test session starts ====================
collected X items

tests/integration/test_pipeline.py::TestSmokeTests::test_all_modules_import PASSED
tests/unit/test_gpu_utils.py::TestGPUManager::test_init_without_gpu PASSED
...

==================== X passed in Y.YYs ====================
```

---

## ⚠️ Note About Python 3.13

Python 3.13 is very new (released Oct 2024). Some packages might have issues:

**If you get errors:**
1. Most will still work fine
2. PyTorch might need updating
3. Some dependencies might not have wheels yet

**If needed, you can downgrade:**
```powershell
# Install Python 3.11 from Windows Store instead
start ms-windows-store://pdp/?ProductId=9NRWMJP3717K
```

But try with 3.13 first - it should work! 🚀

