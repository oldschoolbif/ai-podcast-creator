# Mutation Testing

## What is Mutation Testing?

Mutation testing **tests your tests** by introducing bugs (mutations) in your code and checking if your tests catch them.

**Example:**
```python
# Original code
if x > 5:
    return True

# Mutant 1: Change > to >=
if x >= 5:  # ❌ Tests should catch this!
    return True

# Mutant 2: Change > to <
if x < 5:   # ❌ Tests should catch this!
    return True
```

If your tests **don't fail** when these mutations are introduced, your tests are weak!

---

## Running Mutation Tests

### Install
```powershell
pip install mutmut
```

### Quick Test (Single File)
```powershell
# Test audio_mixer.py (already has 100% coverage)
mutmut run --paths-to-mutate=src/core/audio_mixer.py --tests-dir=tests/unit

# Show results
mutmut show

# See survived mutants (tests didn't catch them)
mutmut show survived
```

### Full Test (All Core Modules)
```powershell
# This takes 30-60 minutes!
mutmut run --paths-to-mutate=src/core/ --tests-dir=tests/

# Generate HTML report
mutmut html
```

---

## Interpreting Results

### Mutation Score
```
Mutation Score = (Killed + Timeout) / Total Mutants
```

**Target: 80%+** (excellent test quality)

### Mutant Status
- **Killed** ✅ - Test failed (good!)
- **Survived** ❌ - Test passed (bad! weak test)
- **Timeout** ⏱️ - Infinite loop (good, test framework caught it)
- **Suspicious** 🤔 - Needs investigation

---

## Example Session

```powershell
PS> mutmut run --paths-to-mutate=src/core/audio_mixer.py

Legend for output:
🎉 Killed mutants.   The goal is for everything to end up in this bucket.
⏰ Timeout.          Test suite took 10 times as long as the baseline so were killed.
🤔 Suspicious.       Tests took a long time, but not long enough to be fatal.
🙁 Survived.         This means your tests needs to be expanded.

Results:
🎉 25 killed
⏰ 2 timeout
🤔 0 suspicious
🙁 3 survived

Mutation score: 90.00%  # (25+2)/(25+2+3) = 90%
```

---

## Fixing Weak Tests

### Example: Survived Mutant

```python
# Original code (src/core/audio_mixer.py)
def mix(self, audio1, audio2):
    if not audio1.exists():
        raise FileNotFoundError("Audio file not found")
    # ...

# Mutant that survived
def mix(self, audio1, audio2):
    if audio1.exists():  # Changed 'not' to nothing
        raise FileNotFoundError("Audio file not found")
    # Test still passed! ❌
```

**Problem:** No test checks that exception is raised when file doesn't exist!

**Fix:** Add test:
```python
def test_mix_raises_error_for_missing_file(mixer, temp_dir):
    """Mix should raise FileNotFoundError for missing audio."""
    fake_path = temp_dir / 'nonexistent.mp3'
    
    with pytest.raises(FileNotFoundError):
        mixer.mix(fake_path, None)  # ✅ Now catches the mutant!
```

---

## Best Practices

### 1. Start Small
```powershell
# Test one file at a time
mutmut run --paths-to-mutate=src/core/audio_mixer.py
```

### 2. Focus on High-Value Code
- Core business logic
- Security-critical code
- Bug-prone areas

### 3. Don't Aim for 100%
- 80%+ is excellent
- 85%+ is world-class
- Some mutants are impossible to kill (logging, etc.)

### 4. Run Regularly
```powershell
# Add to weekly quality checks
# Already in .github/workflows/quality-advanced.yml
```

---

## CI Integration

Mutation testing is already set up in:
- `.github/workflows/quality-advanced.yml`
- Runs weekly on Monday 3am UTC
- Tests core modules only (faster)

To run locally before pushing big changes:
```powershell
.\scripts\mutation-test.ps1  # (create this script if desired)
```

---

## Resources

- **mutmut docs:** https://mutmut.readthedocs.io/
- **Mutation testing explained:** https://en.wikipedia.org/wiki/Mutation_testing
- **Industry standards:** 80%+ mutation score

---

## Example: Perfect Score

**audio_mixer.py** has 100% line coverage and should have ~90% mutation score:

```powershell
PS> mutmut run --paths-to-mutate=src/core/audio_mixer.py
# Results: 🎉 45 killed, ⏰ 3 timeout, 🙁 2 survived
# Score: 96% (48/50)
```

This means our tests actually catch bugs! ✅

