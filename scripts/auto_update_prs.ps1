# Automatically update out-of-date PRs by merging main into them

param(
    [int[]]$PRNumbers = @(),
    [switch]$All = $false,
    [switch]$DependabotOnly = $true
)

Write-Host "=== Auto-Update Out-of-Date PRs ===" -ForegroundColor Cyan
Write-Host ""

# Get PRs to update
if ($All) {
    Write-Host "Getting all open PRs..." -ForegroundColor Yellow
    $PRs = gh pr list --state open --json number,headRefName,isDraft --limit 50 | ConvertFrom-Json
} elseif ($PRNumbers.Count -gt 0) {
    $PRs = $PRNumbers | ForEach-Object {
        gh pr view $_ --json number,headRefName,isDraft 2>&1 | ConvertFrom-Json
    }
} else {
    Write-Host "Getting Dependabot PRs..." -ForegroundColor Yellow
    $PRs = gh pr list --state open --json number,headRefName,isDraft --limit 50 | ConvertFrom-Json | Where-Object { $_.headRefName -like "dependabot/*" }
}

if ($PRs.Count -eq 0) {
    Write-Host "No PRs found to update" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($PRs.Count) PR(s) to check" -ForegroundColor Cyan
Write-Host ""

$updatedCount = 0
$upToDateCount = 0
$errorCount = 0

foreach ($pr in $PRs) {
    if ($pr.isDraft) {
        Write-Host "⏭️  PR #$($pr.number) is a draft - skipping" -ForegroundColor Gray
        continue
    }
    
    Write-Host "Checking PR #$($pr.number)..." -ForegroundColor Cyan
    
    # Check if PR is up-to-date
    $prDetails = gh pr view $pr.number --json mergeable,state,headRefName,baseRefName,isDraft 2>&1 | ConvertFrom-Json
    
    if ($prDetails.state -ne "OPEN") {
        Write-Host "  ⚠️  PR #$($pr.number) is not open (state: $($prDetails.state))" -ForegroundColor Yellow
        continue
    }
    
    # Check if branch is behind
    $behind = gh api repos/oldschoolbif/ai-podcast-creator/compare/$($prDetails.baseRefName)...$($prDetails.headRefName) --jq '.behind_by' 2>&1
    
    if ($LASTEXITCODE -eq 0 -and $behind -gt 0) {
        Write-Host "  ⚠️  Branch is $behind commit(s) behind base" -ForegroundColor Yellow
        Write-Host "  Updating branch..." -ForegroundColor Cyan
        
        # Update branch using GitHub API
        $branchName = $prDetails.headRefName
        $result = gh api repos/oldschoolbif/ai-podcast-creator/merges -X POST -f base=$branchName -f head=$($prDetails.baseRefName) -f commit_message="Merge $($prDetails.baseRefName) into $branchName" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ PR #$($pr.number) updated successfully!" -ForegroundColor Green
            $updatedCount++
        } else {
            Write-Host "  ❌ Failed to update PR #$($pr.number)" -ForegroundColor Red
            Write-Host "  Error: $result" -ForegroundColor Red
            $errorCount++
        }
    } else {
        Write-Host "  ✅ PR #$($pr.number) is up-to-date" -ForegroundColor Green
        $upToDateCount++
    }
    
    Write-Host ""
}

Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Updated: $updatedCount" -ForegroundColor Green
Write-Host "Up-to-date: $upToDateCount" -ForegroundColor Green
Write-Host "Errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })

