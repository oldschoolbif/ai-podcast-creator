# Batch Merge Dependabot PRs
# Groups PRs by category and merges them safely

param(
    [switch]$DryRun = $false,
    [string]$Group = "all"  # all, python, devtools, actions
)

Write-Host "=== Dependabot PR Batch Merge ===" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No PRs will be merged" -ForegroundColor Yellow
    Write-Host ""
}

# Define PR groups
$pythonPRs = @(38, 37, 35, 34, 32, 31, 36)  # Core Python dependencies
$devToolsPRs = @(33, 30, 29)  # Dev tools and testing
$actionsPRs = @(28, 27, 26, 25)  # GitHub Actions

$allPRs = $pythonPRs + $devToolsPRs + $actionsPRs

function Merge-PRGroup {
    param(
        [int[]]$PRNumbers,
        [string]$GroupName
    )
    
    Write-Host "=== Merging $GroupName ===" -ForegroundColor Green
    Write-Host "PRs: $($PRNumbers -join ', ')" -ForegroundColor Gray
    Write-Host ""
    
    foreach ($pr in $PRNumbers) {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would merge PR #$pr" -ForegroundColor Yellow
        } else {
            Write-Host "Merging PR #$pr..." -ForegroundColor Cyan
            
            # Check PR status
            $prStatus = gh pr view $pr --json mergeable,state 2>&1 | ConvertFrom-Json
            
            if ($prStatus.state -ne "OPEN") {
                Write-Host "⚠️  PR #$pr is not open (state: $($prStatus.state))" -ForegroundColor Yellow
                continue
            }
            
            # For Dependabot PRs, always use --auto to wait for CI checks
            Write-Host "   Setting auto-merge (will merge when CI passes)..." -ForegroundColor Gray
            $result = gh pr merge $pr --merge --delete-branch --auto 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ PR #$pr merged successfully" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to merge PR #$pr" -ForegroundColor Red
                Write-Host $result
                Write-Host ""
                Write-Host "Continue with remaining PRs? (y/n)" -ForegroundColor Yellow
                $continue = Read-Host
                if ($continue -ne 'y') {
                    Write-Host "Stopping merge process" -ForegroundColor Yellow
                    return $false
                }
            }
            Write-Host ""
        }
    }
    
    return $true
}

# Execute based on group
switch ($Group.ToLower()) {
    "python" {
        $success = Merge-PRGroup -PRNumbers $pythonPRs -GroupName "Python Dependencies"
        if ($success -and -not $DryRun) {
            Write-Host "✅ Python dependencies merged. Run tests before continuing!" -ForegroundColor Green
        }
    }
    "devtools" {
        $success = Merge-PRGroup -PRNumbers $devToolsPRs -GroupName "Dev Tools & Testing"
        if ($success -and -not $DryRun) {
            Write-Host "✅ Dev tools merged. Run tests before continuing!" -ForegroundColor Green
        }
    }
    "actions" {
        $success = Merge-PRGroup -PRNumbers $actionsPRs -GroupName "GitHub Actions"
        if ($success -and -not $DryRun) {
            Write-Host "✅ GitHub Actions merged. CI should work with new versions!" -ForegroundColor Green
        }
    }
    "all" {
        Write-Host "Merging all groups in sequence..." -ForegroundColor Cyan
        Write-Host ""
        
        # Group 1: Python
        $success = Merge-PRGroup -PRNumbers $pythonPRs -GroupName "Python Dependencies"
        if (-not $success) { exit 1 }
        
        if (-not $DryRun) {
            Write-Host "⏸️  Pausing for testing..." -ForegroundColor Yellow
            Write-Host "Run: pytest tests/ -v" -ForegroundColor Gray
            Write-Host "Press Enter to continue with dev tools..." -ForegroundColor Yellow
            Read-Host
        }
        
        # Group 2: Dev Tools
        $success = Merge-PRGroup -PRNumbers $devToolsPRs -GroupName "Dev Tools & Testing"
        if (-not $success) { exit 1 }
        
        if (-not $DryRun) {
            Write-Host "⏸️  Pausing for testing..." -ForegroundColor Yellow
            Write-Host "Run: pytest tests/ -v" -ForegroundColor Gray
            Write-Host "Press Enter to continue with GitHub Actions..." -ForegroundColor Yellow
            Read-Host
        }
        
        # Group 3: Actions
        $success = Merge-PRGroup -PRNumbers $actionsPRs -GroupName "GitHub Actions"
        if (-not $success) { exit 1 }
        
        Write-Host ""
        Write-Host "✅ All Dependabot PRs merged!" -ForegroundColor Green
    }
    default {
        Write-Host "Invalid group: $Group" -ForegroundColor Red
        Write-Host "Valid options: all, python, devtools, actions" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "=== Complete ===" -ForegroundColor Cyan

