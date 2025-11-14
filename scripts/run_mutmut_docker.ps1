Param(
    [string]$MutmutArgs = ""
)

Write-Host "🐳 Launching Linux container for mutmut..." -ForegroundColor Cyan
if ($env:PYTEST_TARGETS) {
    Write-Host "🎯 PYTEST_TARGETS=$($env:PYTEST_TARGETS)" -ForegroundColor Yellow
}
if ($env:MUTMUT_DEBUG) {
    Write-Host "🐞 MUTMUT_DEBUG=$($env:MUTMUT_DEBUG)" -ForegroundColor Yellow
}

$exportPytestCmd = ("export PYTEST_TARGETS='{0}'" -f ($env:PYTEST_TARGETS ?? ""))
$exportDebugCmd = ("export MUTMUT_DEBUG='{0}'" -f ($env:MUTMUT_DEBUG ?? ""))
Write-Host "🔧 export cmd (pytest): $exportPytestCmd" -ForegroundColor DarkGray
Write-Host "🔧 export cmd (debug): $exportDebugCmd" -ForegroundColor DarkGray

$dockerImage = "aipodcast-mutmut-gpu:latest"
$dockerfilePath = "docker/MutmutGpu.Dockerfile"

function Test-DockerImageExists {
    param([string]$ImageName)
    $exists = $false
    try {
        docker image inspect $ImageName *> $null
        $exists = $true
    } catch {
        $exists = $false
    }
    return $exists
}

if (-not (Test-DockerImageExists -ImageName $dockerImage)) {
    Write-Host "🔧 Building GPU-enabled mutmut image ($dockerImage)..." -ForegroundColor Yellow
    docker build -t $dockerImage -f $dockerfilePath .
}

$useGpu = $true
if ($env:MUTMUT_USE_GPU -eq "0") {
    $useGpu = $false
}

$bashCommands = @(
    "set -e",
    $exportPytestCmd,
    $exportDebugCmd,
    "echo PYTEST_TARGETS=\$PYTEST_TARGETS",
    "echo MUTMUT_DEBUG=\$MUTMUT_DEBUG",
    "export PYDUB_AUDIO_CONVERTER=ffmpeg",
    "python -m venv /tmp/mutenv",
    "source /tmp/mutenv/bin/activate",
    "python -m pip install --upgrade --quiet pip setuptools wheel",
    "pip install --quiet -r requirements-mutation.txt",
    "pip install --quiet -r requirements-dev.txt",
    "pip install --quiet --extra-index-url https://download.pytorch.org/whl/cu121 torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121",
    "python -m mutmut run $MutmutArgs",
    "python -m mutmut results"
) -join " && "

$dockerArgs = @("--rm")

# Configure Docker resource limits for maximum performance without system instability
# Detect Docker's actual available resources (may be limited by Docker Desktop settings)
try {
    # Query Docker's actual CPU limit (may be less than system CPUs)
    $dockerCpuLimit = docker info --format "{{.NCPU}}" 2>$null
    if ($dockerCpuLimit -match '^\d+$') {
        $dockerCpuLimit = [int]$dockerCpuLimit
    } else {
        # Fallback: query system CPUs
        $cpuInfo = Get-CimInstance Win32_ComputerSystem
        $dockerCpuLimit = $cpuInfo.NumberOfLogicalProcessors
        if (-not $dockerCpuLimit) {
            $dockerCpuLimit = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
        }
    }
    
    # Query Docker's memory limit
    $dockerMemInfo = docker info --format "{{.MemTotal}}" 2>$null
    $dockerMemBytes = 0
    if ($dockerMemInfo -match '^(\d+)') {
        $dockerMemBytes = [int64]$Matches[1]
    }
    
    # If Docker doesn't report memory, query system RAM
    if ($dockerMemBytes -eq 0) {
        $memInfo = Get-CimInstance Win32_ComputerSystem
        $dockerMemBytes = $memInfo.TotalPhysicalMemory
    }
    $dockerMemGB = [math]::Round($dockerMemBytes / 1GB, 1)
    
    # Calculate safe limits: 85% CPU (round down to even), reasonable RAM limit
    $safeCores = [math]::Floor($dockerCpuLimit * 0.85)
    if ($safeCores % 2 -eq 1) {
        $safeCores = [math]::Max(1, $safeCores - 1)
    }
    
    # Memory: Use reasonable limit (16GB) rather than percentage
    # Mutation testing typically uses 2-4GB, so 16GB provides plenty of headroom
    # without reserving excessive unused memory
    $safeRamGB = 16
    if ($dockerMemGB -lt 16) {
        # If Docker has less than 16GB, use 80% of available
        $safeRamGB = [math]::Floor($dockerMemGB * 0.80)
    }
    
    # Ensure we don't exceed Docker's limits
    $safeCores = [math]::Min($safeCores, $dockerCpuLimit)
    $safeRamGB = [math]::Min($safeRamGB, $dockerMemGB)
    
    Write-Host "💻 Docker Resources: $dockerCpuLimit cores, $([math]::Round($dockerMemGB, 1)) GB RAM" -ForegroundColor Cyan
    Write-Host "🚀 Container Limits: $safeCores cores, ${safeRamGB}GB RAM (85% CPU, reasonable RAM limit)" -ForegroundColor Green
    
    $dockerArgs += "--cpus=$safeCores"
    $dockerArgs += "--memory=${safeRamGB}g"
} catch {
    Write-Host "⚠️  Could not detect Docker resources, using default limits" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor DarkGray
    # Fallback: conservative defaults
    $dockerArgs += "--cpus=4"
    $dockerArgs += "--memory=8g"
}

if ($env:PYTEST_TARGETS) {
    $dockerArgs += "--env"
    $dockerArgs += "PYTEST_TARGETS=$($env:PYTEST_TARGETS)"
}

if ($env:MUTMUT_DEBUG) {
    $dockerArgs += "--env"
    $dockerArgs += "MUTMUT_DEBUG=$($env:MUTMUT_DEBUG)"
}

if ($useGpu) {
    $dockerArgs += "--gpus"
    $dockerArgs += "all"
}

$dockerArgs += @(
    "-v", "${PWD}:/workspace",
    "-w", "/workspace"
)

$dockerArgs += @(
    $dockerImage,
    "bash",
    "-lc",
    $bashCommands
)

docker run @dockerArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Mutation testing finished (results above)." -ForegroundColor Green
} else {
    Write-Host "❌ Mutmut exited with code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}
