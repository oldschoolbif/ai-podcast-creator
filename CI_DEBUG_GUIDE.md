# CI Debugging Guide

## Quick Access Methods

### Option 1: Download Full Logs (Best for Large Outputs)
```powershell
# Get latest run ID
cd D:\dev\AI_Podcast_Creator
$runId = (gh run list --workflow=tests.yml --branch feature/audio-visualizer-coverage --limit 1 --json databaseId --jq -r '.[0].databaseId')

# Download full logs
gh run view $runId --log > ci_logs.txt

# Then you can share the file or just the relevant sections
```

### Option 2: Filter for Errors Only (Smaller Output)
```powershell
# Get just error lines
gh run view <run-id> --log | Select-String -Pattern '(FAILED|ERROR|Traceback|AssertionError|ModuleNotFoundError|ImportError)' -Context 3,10
```

### Option 3: View in Browser (Easiest)
```powershell
# Opens GitHub Actions page in browser - easy to copy specific sections
gh run view <run-id> --web

# Or just
gh run view --web  # Opens latest run
```

### Option 4: Get Specific Job Logs
```powershell
# List all jobs in a run
gh run view <run-id> --json jobs --jq '.[] | "\(.name): \(.conclusion)"'

# Get logs for specific job
gh run view <run-id> --job <job-id> --log
```

## Recommended Workflow

1. **For single test failures**: Copy/paste the error section is fine
2. **For multiple failures or large logs**: Download via `gh run view <run-id> --log > ci_logs.txt`
3. **For quick browsing**: Use `gh run view --web` and copy from browser
4. **For sharing**: Upload the downloaded `.txt` file or paste relevant sections

## Character Limits

- GitHub UI: Shows full logs (may need to "show more" for very long outputs)
- Copy/paste: Usually fine for individual test failures
- File download: Best for full runs with multiple failures
- Error filtering: Best for quick diagnosis without noise

