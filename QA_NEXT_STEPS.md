# QA Next Steps

## Current Status

✅ **Test Infrastructure Fixed**
- Missing fixtures added
- GPU test markers configured
- Invalid test data generators fixed
- Missing markers added (smoke, no_cpu_patch)
- Mutants directory cleaned up

✅ **Mutant Coverage Verified**
- All 8 surviving mutants have tests that pass locally
- Tests are correctly designed to kill the mutants

📊 **Current Test Coverage: 55.97%**
- **Target:** 70% (per `.codecov.yml`)
- **Gap:** Need to increase by ~14%

## Next Steps (Prioritized)

### 1. **Verify Mutation Testing Works** 🔄 HIGH PRIORITY
**Status:** Pending  
**Time:** 30-60 minutes  
**Action:**
- Run mutation testing now that infrastructure is fixed
- Verify the 8 mutants are actually killed
- Ensure mutation testing completes successfully

**Why:** We've fixed infrastructure and verified tests exist, but haven't confirmed mutation testing actually works end-to-end.

---

### 2. **Increase Test Coverage to 70%+** 📈 HIGH PRIORITY  
**Status:** Pending  
**Time:** 2-4 hours  
**Current:** 55.97%  
**Target:** 70%  
**Gap:** ~14%  

**Action:**
- Identify modules with low coverage
- Write targeted tests for uncovered code paths
- Focus on high-value areas (core functionality, error handling)

**Why:** Codecov threshold is 70% - we're currently below target.

---

### 3. **Fix Failing Tests** 🔧 MEDIUM PRIORITY
**Status:** In Progress  
**Time:** 1-2 hours  

**Current Failures:**
- GPU utils tests (likely GPU-related, may need markers)
- Avatar generator tests (may need mocking/stubs)
- Some integration/property tests

**Action:**
- Review failing tests
- Fix or mark appropriately (skip if GPU-dependent, etc.)
- Ensure test suite passes completely

**Why:** Test suite should pass before running mutation testing or coverage analysis.

---

### 4. **Ensure Mutation Testing in CI** 🚀 MEDIUM PRIORITY
**Status:** Pending  
**Time:** 1-2 hours  

**Action:**
- Verify mutation testing can run in GitHub Actions
- Add mutation testing workflow (or update existing)
- Ensure it runs deterministically

**Why:** Mutation testing should evolve with the codebase, not just run locally.

---

## Recommended Order

1. **Fix failing tests** (ensure suite passes)
2. **Verify mutation testing works** (confirm 8 mutants killed)
3. **Increase coverage to 70%** (meet codecov threshold)
4. **Set up mutation testing in CI** (automate for ongoing use)

---

## Notes

- Test infrastructure is now stable
- All known infrastructure issues have been addressed
- Tests for the 8 mutants exist and pass locally
- Coverage needs improvement to meet 70% threshold
- Some tests are failing and need attention

