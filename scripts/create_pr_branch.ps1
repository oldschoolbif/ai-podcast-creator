# Complete workflow: Create branch, make changes, commit, push, create PR
# This ensures branch is always up-to-date and PR is created correctly

param(
    [Parameter(Mandatory=$true)]
    [string]$BranchName,
    
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage,
    
    [string]$BaseBranch = "main",
    [string]$PRTitle = "",
    [string]$PRBody = "",
    [switch]$SkipPR = $false
)

Write-Host "=== Complete PR Workflow ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create branch from latest main
Write-Host "Step 1: Creating branch from latest $BaseBranch..." -ForegroundColor Yellow
& "$PSScriptRoot\create_feature_branch.ps1" -BranchName $BranchName -BaseBranch $BaseBranch
if ($LASTEXITCODE -ne 0) {
    exit 1
}

# Step 2: Check for changes to commit
Write-Host ""
Write-Host "Step 2: Checking for changes..." -ForegroundColor Yellow
$status = git status --porcelain 2>&1
if (-not $status) {
    Write-Host "⚠️  No changes to commit!" -ForegroundColor Yellow
    Write-Host "   Make your changes first, then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found changes to commit:" -ForegroundColor Green
$status | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# Step 3: Stage all changes
Write-Host ""
Write-Host "Step 3: Staging changes..." -ForegroundColor Yellow
git add . 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to stage changes" -ForegroundColor Red
    exit 1
}

# Step 4: Commit
Write-Host "Step 4: Committing changes..." -ForegroundColor Yellow
git commit -m $CommitMessage 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to commit" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Committed: $CommitMessage" -ForegroundColor Green

# Step 5: Push
Write-Host ""
Write-Host "Step 5: Pushing to remote..." -ForegroundColor Yellow
git push -u origin $BranchName 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Pushed to origin/$BranchName" -ForegroundColor Green

# Step 6: Create PR (optional)
if (-not $SkipPR) {
    Write-Host ""
    Write-Host "Step 6: Creating pull request..." -ForegroundColor Yellow
    
    if (-not $PRTitle) {
        $PRTitle = $CommitMessage
    }
    
    if (-not $PRBody) {
        $PRBody = "Automated PR from workflow script.`n`nBranch is up-to-date with $BaseBranch."
    }
    
    $prOutput = gh pr create --title $PRTitle --body $PRBody 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Pull request created!" -ForegroundColor Green
        
        # Extract PR number from output (format: "https://github.com/.../pull/42" or "#42")
        $prNumber = $prOutput | Select-String -Pattern '#(\d+)' | ForEach-Object { $_.Matches[0].Groups[1].Value }
        if (-not $prNumber) {
            $prNumber = $prOutput | Select-String -Pattern '/pull/(\d+)' | ForEach-Object { $_.Matches[0].Groups[1].Value }
        }
        
        if ($prNumber) {
            Write-Host ""
            Write-Host "Step 7: Enabling auto-merge..." -ForegroundColor Yellow
            gh pr merge $prNumber --auto --merge 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Auto-merge enabled!" -ForegroundColor Green
                Write-Host "   PR will merge automatically when all checks pass." -ForegroundColor Cyan
            } else {
                Write-Host "⚠️  Could not enable auto-merge automatically" -ForegroundColor Yellow
                Write-Host "   You can enable it manually on the PR page." -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "⚠️  Failed to create PR (you can create it manually)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Workflow Complete! ===" -ForegroundColor Green
Write-Host ""

