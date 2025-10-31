Param(
    [string]$MutmutArgs = ""
)

Write-Host "🐳 Launching Linux container for mutmut..." -ForegroundColor Cyan

$dockerImage = "python:3.11"

$script = @"
set -e
apt-get update >/dev/null
apt-get install -y --no-install-recommends build-essential >/dev/null
pip install --upgrade pip >/dev/null
pip install -r requirements-dev.txt >/dev/null
python -m mutmut run $MutmutArgs
python -m mutmut results
"@

docker run --rm `
    -v "${PWD}:/workspace" `
    -w /workspace `
    $dockerImage `
    bash -lc "$script"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Mutation testing finished (results above)." -ForegroundColor Green
} else {
    Write-Host "❌ Mutmut exited with code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}
