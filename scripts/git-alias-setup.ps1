# Setup git aliases for common workflow commands
# Makes it easier to follow the correct workflow

Write-Host "=== Setting Up Git Aliases ===" -ForegroundColor Cyan
Write-Host ""

# Create new branch from latest main
git config --global alias.newbranch '!f() { git fetch origin && git checkout main && git pull origin main && git checkout -b "$1"; }; f'

# Create branch and switch (ensures up-to-date)
git config --global alias.cob '!f() { git fetch origin && git checkout main && git pull origin main && git checkout -b "$1"; }; f'

Write-Host "✅ Git aliases configured!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  git newbranch feature/my-feature" -ForegroundColor Gray
Write-Host "  git cob feature/my-feature" -ForegroundColor Gray
Write-Host ""
Write-Host "Both commands will:" -ForegroundColor Yellow
Write-Host "  1. Fetch latest from remote" -ForegroundColor Gray
Write-Host "  2. Switch to main" -ForegroundColor Gray
Write-Host "  3. Pull latest changes" -ForegroundColor Gray
Write-Host "  4. Create and switch to new branch" -ForegroundColor Gray
Write-Host ""

