# CI Version Compatibility Fix

**Issue:** Version mismatch between requirements.txt and pytest configuration

## Problem Identified

- **requirements.txt** specifies: `pytest==8.4.2`
- **pytest.ini** had: `minversion = 7.0`
- **pyproject.toml** had: `minversion = "7.0"`

This mismatch could cause pytest 8.x to reject the configuration or behave unexpectedly.

## Fix Applied

Updated `minversion` to `8.0` in both configuration files to match the pytest version in requirements.txt.

**Files Changed:**
- `pytest.ini`: `minversion = 7.0` → `minversion = 8.0`
- `pyproject.toml`: `minversion = "7.0"` → `minversion = "8.0"`

## Why This Matters

Pytest 8.x has breaking changes from 7.x:
- Different configuration parsing
- Stricter validation
- Different plugin loading behavior

Having `minversion = 7.0` while using pytest 8.4.2 could cause:
- Configuration validation errors
- Plugin loading issues
- Unexpected test behavior

## Commit

Latest commit updates minversion to match pytest 8.4.2

---

*This should resolve version compatibility issues in CI*

