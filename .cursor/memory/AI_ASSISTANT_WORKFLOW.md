# AI Assistant Workflow Practices

## When Creating PRs (ALWAYS)
1. **Use conventional commit format** in PR title and commits
2. **Keep PRs small** - if changes are large, break into multiple PRs
3. **Use descriptive branch names** with proper prefix
4. **Create branch from latest main** to avoid "out-of-date" warnings
5. **Write clear PR descriptions** explaining what and why

## When Committing (ALWAYS)
1. **Use conventional commit format:**
   - `feat:` for new features
   - `fix:` for bug fixes
   - `test:` for test additions/improvements
   - `docs:` for documentation
   - `refactor:` for code restructuring
   - `chore:` for maintenance
   - `ci:` for CI/CD changes

2. **Keep commits focused** - one logical change per commit

3. **Write clear commit messages:**
   - Start with type prefix
   - Brief, descriptive summary
   - Optional: Add body for complex changes

## When Creating Branches (ALWAYS)
1. **Start from latest main:**
   ```powershell
   git checkout main
   git pull origin main
   git checkout -b type/description
   ```

2. **Use proper naming:**
   - `feature/` for features
   - `fix/` for fixes
   - `test/` for tests
   - `docs/` for docs
   - `refactor/` for refactoring
   - `chore/` for maintenance
   - `ci/` for CI/CD

## PR Size Guidelines (ALWAYS)
- **Target:** < 500 lines changed
- **If larger:** Break into multiple PRs
- **Reason:** Faster CI, easier review, faster merges

## Workflow Automation (USE EXISTING)
- Pre-commit hooks: Automatic formatting/linting
- Pre-push script: `.\scripts\pre-push.ps1` (recommend to user)
- CI/CD: Automatic testing/coverage
- Auto-merge: PRs merge automatically when checks pass

## Reminders to Give User
1. **Before pushing:** Run `.\scripts\pre-push.ps1` (optional but recommended)
2. **PR size:** Keep PRs small for faster feedback
3. **Commit format:** Use conventional commits
4. **Branch cleanup:** Clean up merged branches weekly
5. **Coverage review:** Review coverage trends weekly

## When User Asks for Changes
1. Create focused PRs (one logical change)
2. Use proper commit messages
3. Create branch from latest main
4. Follow naming conventions
5. Write clear PR descriptions

