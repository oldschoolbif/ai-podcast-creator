Param(
    [string]$MutmutArgs = ""
)

Write-Host "🐳 Launching Linux container for mutmut..." -ForegroundColor Cyan

$dockerImage = "python:3.11"

$bashCommands = @(
    "set -e",
    "apt-get update >/dev/null",
    "apt-get install -y --no-install-recommends build-essential pkg-config libavformat-dev libavdevice-dev libavfilter-dev libavcodec-dev libavutil-dev libswresample-dev libswscale-dev >/dev/null",
    "python -m venv /tmp/mutenv",
    "source /tmp/mutenv/bin/activate",
    "python -m pip install --upgrade --quiet pip setuptools wheel",
    "pip install --quiet -r requirements-mutation.txt",
    "pip install --quiet -r requirements-dev.txt",
    "python -m mutmut run $MutmutArgs",
    "python -m mutmut results"
) -join " && "

docker run --rm `
    -v "${PWD}:/workspace" `
    -w /workspace `
    $dockerImage `
    bash -lc "$bashCommands"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Mutation testing finished (results above)." -ForegroundColor Green
} else {
    Write-Host "❌ Mutmut exited with code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}
