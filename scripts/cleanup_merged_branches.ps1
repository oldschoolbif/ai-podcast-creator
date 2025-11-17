# Clean up merged branches (local and remote)

Write-Host "=== Cleaning Up Merged Branches ===" -ForegroundColor Cyan
Write-Host ""

# Switch to main
Write-Host "Switching to main branch..." -ForegroundColor Yellow
git checkout main
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to switch to main" -ForegroundColor Red
    exit 1
}

# Pull latest
Write-Host "Pulling latest from origin..." -ForegroundColor Yellow
git pull origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to pull from origin" -ForegroundColor Red
    exit 1
}

Write-Host ""

# List local branches
Write-Host "=== Local Branches ===" -ForegroundColor Green
$localBranches = git branch | ForEach-Object { $_.Trim().Replace('* ', '') } | Where-Object { $_ -ne 'main' -and $_ -notmatch '^\s*$' }

Write-Host "Found branches:" -ForegroundColor Gray
$localBranches | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
Write-Host ""

# Check which are merged
Write-Host "Checking merged branches..." -ForegroundColor Yellow
$mergedBranches = @()

foreach ($branch in $localBranches) {
    $merged = git branch --merged main | Select-String $branch
    if ($merged) {
        $mergedBranches += $branch
        Write-Host "✅ $branch is merged" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $branch is NOT merged" -ForegroundColor Yellow
    }
}

Write-Host ""

if ($mergedBranches.Count -eq 0) {
    Write-Host "No merged branches to clean up" -ForegroundColor Gray
} else {
    Write-Host "Branches to delete: $($mergedBranches -join ', ')" -ForegroundColor Cyan
    $confirm = Read-Host "Delete these branches? (y/n)"
    
    if ($confirm -eq 'y') {
        foreach ($branch in $mergedBranches) {
            Write-Host "Deleting $branch..." -ForegroundColor Yellow
            git branch -d $branch
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Deleted $branch" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Could not delete $branch (may have unmerged changes)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "Skipped branch deletion" -ForegroundColor Gray
    }
}

Write-Host ""

# Prune remote tracking branches
Write-Host "=== Remote Tracking Branches ===" -ForegroundColor Green
Write-Host "Pruning remote tracking branches..." -ForegroundColor Yellow
git remote prune origin
Write-Host "✅ Remote branches pruned" -ForegroundColor Green

Write-Host ""
Write-Host "=== Cleanup Complete ===" -ForegroundColor Cyan

