# Generate Coverage and Status Badges
Write-Host "📛 Generating project badges..." -ForegroundColor Cyan
Write-Host ""

# Install badge generators if needed
pip install coverage-badge genbadge[all] --quiet

# Generate coverage badge
Write-Host "1️⃣ Generating coverage badge..." -ForegroundColor Yellow
pytest --cov=src --cov-report=term --cov-report=json --tb=no -q > $null 2>&1
coverage-badge -o coverage.svg -f

# Generate test badge
Write-Host "2️⃣ Generating test status badge..." -ForegroundColor Yellow
$testResult = pytest --tb=no -q 2>&1 | Select-String "passed"
if ($testResult -match "(\d+) passed") {
    $passed = $matches[1]
    $color = "brightgreen"
    $label = "$passed tests passing"
} else {
    $passed = "unknown"
    $color = "lightgrey"
    $label = "tests"
}

# Create badges directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "docs/badges" > $null

# Move badges
Move-Item -Force coverage.svg docs/badges/coverage.svg

Write-Host ""
Write-Host "✅ Badges generated!" -ForegroundColor Green
Write-Host "📂 Location: docs/badges/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add to README.md:" -ForegroundColor Yellow
Write-Host "![Coverage](docs/badges/coverage.svg)" -ForegroundColor White
Write-Host ""

