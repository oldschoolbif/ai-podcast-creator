# Memory: No Shortcuts in Testing

## Core Principle

**NEVER disable, fake out, or work around testing issues. Always fix the root cause properly.**

### Guidelines

- **Fix the actual issue**: Don't disable Codecov checks, don't mark tests as skipped, don't use `continue-on-error` to hide failures
- **Root cause analysis**: Understand why tests are failing and fix the underlying problem
- **Proper solutions only**: If coverage is missing, write tests. If tests fail, fix the code or tests properly
- **No workarounds**: Avoid temporary fixes, hacks, or "just make it pass" solutions

### Why This Matters

- **Code quality**: Shortcuts lead to technical debt and hidden bugs
- **Maintainability**: Proper fixes are easier to maintain long-term
- **Team trust**: Reliable tests build confidence in the codebase
- **Professional standards**: Quality code requires quality testing

### Examples of What NOT to Do

- ❌ Disable Codecov checks with `fail_ci_if_error: false`
- ❌ Skip failing tests with `@pytest.mark.skip`
- ❌ Use `continue-on-error` to hide failures
- ❌ Comment out failing tests
- ❌ Lower coverage thresholds to make checks pass
- ❌ Mock everything to avoid real testing

### Examples of What TO Do

- ✅ Write proper tests to cover missing lines
- ✅ Fix the code to make tests pass
- ✅ Investigate why tests fail and fix root cause
- ✅ Improve test quality, not lower standards
- ✅ Ensure tests accurately reflect real behavior

---

**Remember:** Quality over speed. Fix it right the first time.

