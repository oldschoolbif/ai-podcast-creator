Title: Test Infrastructure Workflow - Critical Lessons Learned

Summary: Before running expensive operations (mutation testing, Docker builds, CI), ALWAYS validate test suite stability locally first by running `pytest`. Fix ALL test infrastructure issues (missing fixtures, invalid test data, missing markers) in batches BEFORE expensive runs, not one-by-one during runs. Mutation testing requires a stable, deterministic test suite - if tests fail during collection, mutation testing fails before it starts. The "death spiral" pattern of fixing one issue and re-running wastes days/weeks of time.

Action: 
1. When asked to run mutation testing or other expensive operations, FIRST run `pytest` locally to validate test suite stability
2. Collect ALL infrastructure failures (missing fixtures, invalid test data, missing markers, etc.)
3. Fix ALL issues in one batch
4. Re-run `pytest` to ensure it passes completely
5. ONLY THEN run the expensive operation once
6. Never fix infrastructure issues one-by-one during expensive runs - this multiplies time wasted
7. Distinguish between test infrastructure (fixtures, markers, test data) and test logic (assertions) - fix infrastructure first

Key Principle: "Validate locally first, fix infrastructure before logic, batch fixes, stability before mutation testing"

