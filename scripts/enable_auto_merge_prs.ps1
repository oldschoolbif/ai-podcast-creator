# Enable auto-merge on individual PRs
# This enables auto-merge on each PR (different from repository setting)

param(
    [int[]]$PRNumbers = @(38, 37, 35, 34, 32, 31, 36, 33, 30, 29, 28, 27, 26, 25)
)

Write-Host "=== Enable Auto-Merge on PRs ===" -ForegroundColor Cyan
Write-Host ""

foreach ($pr in $PRNumbers) {
    Write-Host "Enabling auto-merge on PR #$pr..." -ForegroundColor Cyan
    
    # Enable auto-merge using GraphQL API
    $query = @"
mutation {
  enablePullRequestAutoMerge(input: {
    pullRequestId: "$(gh pr view $pr --json id -q .id)",
    mergeMethod: MERGE
  }) {
    pullRequest {
      autoMergeRequest {
        enabledAt
      }
    }
  }
}
"@
    
    $result = gh api graphql -f query=$query 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Auto-merge enabled on PR #$pr" -ForegroundColor Green
    } else {
        # Try alternative: use gh pr merge with --auto flag
        Write-Host "  ⚠️  GraphQL method failed, trying alternative..." -ForegroundColor Yellow
        
        # Check if PR is ready
        $prStatus = gh pr view $pr --json mergeable,state 2>&1 | ConvertFrom-Json
        
        if ($prStatus.state -eq "OPEN" -and $prStatus.mergeable -eq $true) {
            Write-Host "  PR is mergeable, merging now..." -ForegroundColor Cyan
            gh pr merge $pr --merge --delete-branch 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ PR #$pr merged!" -ForegroundColor Green
            }
        } else {
            Write-Host "  ⏳ PR #$pr not ready yet (mergeable: $($prStatus.mergeable))" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
}

Write-Host "=== Complete ===" -ForegroundColor Cyan

