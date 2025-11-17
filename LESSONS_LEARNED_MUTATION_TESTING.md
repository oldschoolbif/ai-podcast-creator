# Lessons Learned: Mutation Testing Workflow

## Core Lessons

### 1. **Always Validate Test Suite Stability FIRST**
**Lesson:** Before running expensive operations (mutation testing, Docker builds, CI), always run `pytest` locally to ensure the test suite passes completely.

**Why:** Infrastructure issues (missing fixtures, invalid test data, missing markers) will cause expensive operations to fail repeatedly, wasting hours/days.

**Action:** Run `pytest` locally → Fix ALL issues → THEN run expensive operations.

---

### 2. **Fix Infrastructure Issues BEFORE Expensive Runs**
**Lesson:** Don't fix test infrastructure issues DURING expensive runs. Fix them all FIRST, then run once.

**Why:** Each fix during an expensive run requires a full re-run cycle (5-10 minutes for Docker, hours for mutation testing). Fixing one-by-one multiplies time wasted.

**Action:** 
- Identify ALL infrastructure issues first
- Fix them all in one batch
- Validate with `pytest`
- THEN run expensive operation once

---

### 3. **Test Infrastructure vs Test Logic**
**Lesson:** Distinguish between test infrastructure (fixtures, markers, test data generators) and test logic (actual assertions).

**Why:** Test logic can be correct, but if infrastructure is broken, tests can't run. Fix infrastructure first.

**Action:** When tests fail, ask: "Is this a test logic issue or an infrastructure issue?" Fix infrastructure first.

---

### 4. **Mutation Testing Requires Stable Test Suite**
**Lesson:** Mutation testing requires a STABLE, DETERMINISTIC test suite. If tests fail during collection, mutation testing can't work.

**Why:** Mutation testing runs the test suite hundreds/thousands of times. If tests fail during collection, mutation testing fails before it even starts.

**Action:** Ensure test suite is stable and deterministic before attempting mutation testing.

---

### 5. **Don't Fix Issues One-by-One During Expensive Runs**
**Lesson:** When an expensive operation fails, don't fix one issue and re-run. Fix ALL issues first.

**Why:** Each re-run wastes time. Fixing one-by-one creates a "death spiral" where each fix reveals another issue.

**Action:** 
- Let expensive operation fail completely
- Collect ALL errors/issues
- Fix them all
- Re-run once

---

## Workflow Pattern to Follow

### ❌ WRONG (What We Did):
```
1. Start mutation testing
2. Fails: "fixture not found"
3. Fix fixture
4. Re-run mutation testing (5-10 min)
5. Fails: "GPU test crashed"
6. Fix marker
7. Re-run mutation testing (5-10 min)
8. Fails: "invalid audio file"
9. Fix test data
10. Re-run mutation testing (5-10 min)
... (repeat for days)
```

### ✅ RIGHT (What We Should Do):
```
1. Run pytest locally
2. Collect ALL failures
3. Fix ALL infrastructure issues
4. Run pytest again - ensure it passes
5. THEN run mutation testing once
```

---

## Key Principles

1. **Validate locally first** - Always run `pytest` locally before expensive operations
2. **Fix infrastructure before logic** - Infrastructure issues block everything
3. **Batch fixes** - Fix all issues at once, not one-by-one
4. **Stability first** - Ensure test suite is stable before mutation testing
5. **Don't fix during expensive runs** - Fix before, not during

---

## Red Flags to Watch For

- Tests failing during collection (not execution) → Infrastructure issue
- Same test failing repeatedly with different errors → Infrastructure issue
- Expensive operation failing before it starts → Infrastructure issue
- Fixing one issue reveals another → Should have fixed all first

---

## Memory Commitments

These lessons should be remembered for future work:
- Always validate test suite stability before expensive operations
- Fix infrastructure issues in batches, not one-by-one
- Run pytest locally first to catch infrastructure issues
- Mutation testing requires a stable, deterministic test suite

