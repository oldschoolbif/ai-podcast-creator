# Monitor PRs and merge when CI checks pass
# This works around the auto-merge limitation

param(
    [int[]]$PRNumbers = @(38, 37, 35, 34, 32, 31, 36, 33, 30, 29, 28, 27, 26, 25),
    [int]$CheckInterval = 60,  # seconds
    [switch]$Continuous = $false
)

Write-Host "=== PR Monitor & Auto-Merge ===" -ForegroundColor Cyan
Write-Host "Monitoring PRs: $($PRNumbers -join ', ')" -ForegroundColor Gray
Write-Host "Check interval: $CheckInterval seconds" -ForegroundColor Gray
Write-Host ""

function Check-AndMergePR {
    param([int]$prNumber)
    
    Write-Host "Checking PR #$prNumber..." -ForegroundColor Cyan
    
    # Get PR status
    $pr = gh pr view $prNumber --json mergeable,state,statusCheckRollup,title 2>&1 | ConvertFrom-Json
    
    if ($pr.state -ne "OPEN") {
        Write-Host "  ⚠️  PR #$prNumber is $($pr.state)" -ForegroundColor Yellow
        return $false
    }
    
    # Check if all status checks pass
    $allChecksPassed = $true
    $pendingChecks = @()
    
    if ($pr.statusCheckRollup) {
        foreach ($check in $pr.statusCheckRollup) {
            if ($check.conclusion -eq "SUCCESS") {
                Write-Host "  ✅ $($check.name)" -ForegroundColor Green
            } elseif ($check.conclusion -eq "FAILURE") {
                Write-Host "  ❌ $($check.name)" -ForegroundColor Red
                $allChecksPassed = $false
            } elseif ($check.conclusion -eq "PENDING" -or $null -eq $check.conclusion) {
                Write-Host "  ⏳ $($check.name)" -ForegroundColor Yellow
                $pendingChecks += $check.name
                $allChecksPassed = $false
            }
        }
    }
    
    # Check mergeable status
    if ($pr.mergeable -eq $true -and $allChecksPassed) {
        Write-Host "  ✅ PR #$prNumber is ready to merge!" -ForegroundColor Green
        Write-Host "  Merging..." -ForegroundColor Cyan
        
        $result = gh pr merge $prNumber --merge --delete-branch 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ PR #$prNumber merged successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ Failed to merge: $result" -ForegroundColor Red
            return $false
        }
    } elseif ($pr.mergeable -eq $false) {
        Write-Host "  ⏳ PR #$prNumber not mergeable yet (checks pending or conflicts)" -ForegroundColor Yellow
        if ($pendingChecks.Count -gt 0) {
            Write-Host "  Pending checks: $($pendingChecks -join ', ')" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⏳ Waiting for checks to pass..." -ForegroundColor Yellow
    }
    
    return $false
}

$mergedCount = 0
$iteration = 0

while ($true) {
    $iteration++
    Write-Host ""
    Write-Host "=== Iteration $iteration ===" -ForegroundColor Cyan
    Write-Host ""
    
    $remainingPRs = @()
    
    foreach ($pr in $PRNumbers) {
        $merged = Check-AndMergePR -prNumber $pr
        if ($merged) {
            $mergedCount++
            Write-Host ""
        } else {
            $remainingPRs += $pr
        }
    }
    
    Write-Host ""
    Write-Host "Progress: $mergedCount/$($PRNumbers.Count) merged" -ForegroundColor Cyan
    
    if ($remainingPRs.Count -eq 0) {
        Write-Host ""
        Write-Host "✅ All PRs merged!" -ForegroundColor Green
        break
    }
    
    if (-not $Continuous) {
        Write-Host ""
        Write-Host "Next check in $CheckInterval seconds..." -ForegroundColor Gray
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Start-Sleep -Seconds $CheckInterval
    } else {
        break
    }
}

Write-Host ""
Write-Host "=== Complete ===" -ForegroundColor Cyan
Write-Host "Merged: $mergedCount/$($PRNumbers.Count) PRs" -ForegroundColor $(if ($mergedCount -eq $PRNumbers.Count) { "Green" } else { "Yellow" })

