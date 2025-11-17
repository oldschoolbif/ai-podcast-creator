# Solo Developer Best Practices - Memory

## Commit Message Format (ALWAYS USE)
Use conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Adding/improving tests
- `docs:` - Documentation
- `refactor:` - Code restructuring
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes
- `style:` - Formatting (no code change)

**Format:** `type: Brief description`

**Examples:**
- `feat: Add avatar generation feature`
- `fix: Resolve coverage gaps in music generator`
- `test: Improve avatar_generator coverage`
- `ci: Restore auto-enable-merge workflow`

## PR Size Guidelines (ALWAYS FOLLOW)
- **Keep PRs small:** < 500 lines changed
- **One logical change per PR**
- **Fast CI = fast feedback = fast merges**
- **Easier to review (even solo)**

## Branch Naming (ALWAYS USE)
Use consistent prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `test/` - Test improvements
- `docs/` - Documentation
- `refactor/` - Code restructuring
- `chore/` - Maintenance
- `ci/` - CI/CD changes

**Examples:**
- `feature/avatar-generation`
- `fix/coverage-gaps`
- `test/improve-music-generator`
- `ci/restore-auto-merge`

## Workflow Steps (ALWAYS FOLLOW)
1. **Create branch from latest main:**
   ```powershell
   git checkout main
   git pull origin main
   git checkout -b feature/name
   ```

2. **Make changes and commit frequently:**
   ```powershell
   git add .
   git commit -m "type: Clear description"
   ```

3. **Before pushing, run pre-push validation:**
   ```powershell
   .\scripts\pre-push.ps1  # Optional but recommended
   ```

4. **Push and create PR:**
   ```powershell
   git push -u origin feature/name
   gh pr create --fill
   ```

5. **PR will auto-merge when checks pass**

## Code Quality (AUTOMATED - TRUST IT)
- Pre-commit hooks handle formatting/linting automatically
- CI handles testing/coverage automatically
- Don't manually format - let tools do it
- Trust the automation

## Reminders for User
- Run `.\scripts\pre-push.ps1` before pushing (catches issues early)
- Keep PRs small and focused
- Use conventional commit format
- Clean up merged branches weekly
- Review coverage trends weekly

