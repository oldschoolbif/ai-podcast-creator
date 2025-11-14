# Create a new feature branch from latest main
# Ensures branch is always up-to-date from the start

param(
    [Parameter(Mandatory=$true)]
    [string]$BranchName,
    
    [string]$BaseBranch = "main"
)

Write-Host "=== Creating Feature Branch ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check current status
Write-Host "Step 1: Checking current status..." -ForegroundColor Yellow
$currentBranch = git rev-parse --abbrev-ref HEAD 2>&1
$status = git status --porcelain 2>&1

if ($status) {
    Write-Host "⚠️  You have uncommitted changes!" -ForegroundColor Yellow
    Write-Host "   Please commit or stash them first." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  1. git stash (save changes temporarily)" -ForegroundColor Gray
    Write-Host "  2. git commit (commit changes)" -ForegroundColor Gray
    Write-Host "  3. git restore . (discard changes)" -ForegroundColor Gray
    exit 1
}

# Step 2: Fetch latest from remote
Write-Host "Step 2: Fetching latest from remote..." -ForegroundColor Yellow
git fetch origin 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to fetch from remote" -ForegroundColor Red
    exit 1
}

# Step 3: Switch to base branch
Write-Host "Step 3: Switching to $BaseBranch..." -ForegroundColor Yellow
git checkout $BaseBranch 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to checkout $BaseBranch" -ForegroundColor Red
    exit 1
}

# Step 4: Pull latest changes
Write-Host "Step 4: Pulling latest changes..." -ForegroundColor Yellow
git pull origin $BaseBranch 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to pull latest changes" -ForegroundColor Red
    exit 1
}

# Step 5: Create new branch
Write-Host "Step 5: Creating new branch '$BranchName'..." -ForegroundColor Yellow
git checkout -b $BranchName 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create branch '$BranchName'" -ForegroundColor Red
    Write-Host "   Branch might already exist. Use: git checkout $BranchName" -ForegroundColor Yellow
    exit 1
}

# Step 6: Verify
Write-Host ""
Write-Host "✅ Branch '$BranchName' created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Current branch: $(git rev-parse --abbrev-ref HEAD)" -ForegroundColor Cyan
Write-Host "Based on: $BaseBranch (latest)" -ForegroundColor Cyan
Write-Host ""
Write-Host "You're ready to make changes!" -ForegroundColor Green
Write-Host ""

