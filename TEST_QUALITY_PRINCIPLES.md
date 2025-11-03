# 🎯 Test Quality Principles

## Core Principle: Fix Root Causes, Not Symptoms

**When fixing test failures, address the root-cause, do not just work around it and skip past it. Make it better, not non-existent.**

### What This Means:

1. **Don't Skip Tests to Make CI Pass**
   - Skipping tests when dependencies are missing = lost coverage
   - Instead: Mock dependencies properly so tests run regardless of what's installed
   - Use `sys.modules` mocking, not `@pytest.mark.skipif`

2. **Don't Work Around the Problem**
   - If a test fails because a dependency isn't installed → Mock it
   - If a test fails because of a path issue → Fix the path logic
   - If a test fails because of an import error → Fix the import structure

3. **Improve Test Quality**
   - Every fix should make tests more robust
   - Every fix should maintain or improve coverage
   - Every fix should make tests work in all environments (local, CI, etc.)

### Example of Wrong Approach:
```python
@pytest.mark.skipif(not TTS_AVAILABLE, reason="TTS library not installed")
def test_something():
    # This test never runs in CI if TTS not installed = lost coverage!
```

### Example of Right Approach:
```python
@patch.dict(sys.modules, {"TTS": create_mock_tts_module()[0]})
def test_something():
    # This test ALWAYS runs in CI, coverage maintained!
```

## Why This Matters:

- **Test coverage is hard-earned** - don't throw it away
- **CI should verify code works** - not just that some tests can skip
- **Quality mindset** - fix problems properly, not hide them
- **Future-proof** - tests work in all environments

## Related Principles:

- **QA-First Mindset**: Tests are part of code quality, not an afterthought
- **Coverage Matters**: Every percentage point represents real work
- **Robust Testing**: Tests should work everywhere, not just where dependencies are installed

---

*"Make it better, not non-existent."* - Test Quality Principle

