Param(
    [string]$Args = ""
)

Write-Host "🔬 Running mutation tests (mutmut)..." -ForegroundColor Cyan

if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activate your virtual environment first ( .\venv\Scripts\Activate.ps1 )." -ForegroundColor Yellow
    exit 1
}

# Ensure mutmut is available
try {
    mutmut --help | Out-Null
} catch {
    Write-Host "❌ mutmut not found. Install dev dependencies first (pip install -r requirements-dev.txt)." -ForegroundColor Red
    exit 1
}

$command = "mutmut run $Args".Trim()
Write-Host "▶️  $command" -ForegroundColor Magenta
Invoke-Expression $command

Write-Host "✅ Mutation testing complete." -ForegroundColor Green
