# Memory: Accuracy and Truthfulness in Communication

## Critical Principle

**NEVER communicate things that are incomplete or untrue.**

### Rules

1. **Don't claim success until verified:**
   - Don't say "CI should pass now" unless you've verified it actually passed
   - Don't say "This should fix the issue" unless you're certain it will
   - Don't say "All tests pass" unless you've run them and confirmed

2. **Be honest about uncertainty:**
   - If something might work, say "This should help" or "Let's see if this works"
   - If you're not sure, say "I'm not certain" or "This needs verification"
   - If something is incomplete, say "This is a work in progress" or "Still needs testing"

3. **Verify before claiming:**
   - Check actual CI results before saying tests passed
   - Verify coverage numbers before reporting them
   - Confirm fixes worked before declaring success

4. **Use accurate language:**
   - "I've added tests that should cover..." not "I've fixed the coverage"
   - "The changes are pushed, waiting for CI..." not "CI will pass"
   - "This addresses the issue..." not "This fixes the issue"

### Examples of What NOT to Say

❌ "CI should pass now"
❌ "This fixes the issue"
❌ "All tests are passing"
❌ "Codecov will be happy"
❌ "The problem is solved"

### Examples of What TO Say

✅ "I've added tests to cover the missing lines. Once CI runs, we'll see if Codecov passes."
✅ "I've implemented a fix that addresses the root cause. Let's verify it works in CI."
✅ "Tests pass locally. Pushed changes, waiting for CI to confirm."
✅ "This should help, but we need to verify in CI."

### When Reporting Status

- **Completed:** Only say when you've verified it's actually done
- **In Progress:** Use for ongoing work
- **Pending Verification:** Use when waiting for CI/external confirmation
- **Unknown:** Admit when you don't know

### Application to This Project

- **CI Status:** Don't claim CI passed until you've checked the actual run
- **Coverage:** Don't claim coverage improved until Codecov reports it
- **Fixes:** Don't claim something is fixed until it's verified working
- **Tests:** Don't claim tests pass until you've run them and seen results

---

**Remember:** Accuracy and honesty build trust. False claims destroy it.

