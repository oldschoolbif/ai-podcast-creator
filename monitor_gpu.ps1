# Real-time GPU Monitor using nvidia-smi
# Press Ctrl+C to stop

Write-Host "=== NVIDIA GPU Monitor ===" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

while ($true) {
    Clear-Host
    Write-Host "=== NVIDIA GPU Monitor ===" -ForegroundColor Cyan
    Write-Host "Updated: $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Gray
    
    # Get GPU stats
    $stats = nvidia-smi --query-gpu=name,utilization.gpu,utilization.memory,temperature.gpu,power.draw,memory.used,memory.total,clocks.current.graphics --format=csv,noheader,nounits
    
    $data = $stats -split ','
    
    Write-Host "GPU Name:        " -NoNewline -ForegroundColor White
    Write-Host "$($data[0].Trim())" -ForegroundColor Green
    
    Write-Host "`nUtilization:" -ForegroundColor Yellow
    Write-Host "  GPU Compute:   " -NoNewline -ForegroundColor White
    $gpuUtil = [int]$data[1].Trim()
    $color = if ($gpuUtil -lt 20) { "Green" } elseif ($gpuUtil -lt 60) { "Yellow" } else { "Red" }
    Write-Host "$gpuUtil%" -ForegroundColor $color
    
    Write-Host "  Memory:        " -NoNewline -ForegroundColor White
    $memUtil = [int]$data[2].Trim()
    $color = if ($memUtil -lt 20) { "Green" } elseif ($memUtil -lt 60) { "Yellow" } else { "Red" }
    Write-Host "$memUtil%" -ForegroundColor $color
    
    Write-Host "`nTemperature:     " -NoNewline -ForegroundColor White
    $temp = [int]$data[3].Trim()
    $color = if ($temp -lt 60) { "Green" } elseif ($temp -lt 80) { "Yellow" } else { "Red" }
    Write-Host "$temp°C" -ForegroundColor $color
    
    Write-Host "Power Draw:      " -NoNewline -ForegroundColor White
    Write-Host "$($data[4].Trim())W" -ForegroundColor Cyan
    
    Write-Host "GPU Clock:       " -NoNewline -ForegroundColor White
    Write-Host "$($data[7].Trim())MHz" -ForegroundColor Cyan
    
    Write-Host "`nVRAM Usage:      " -NoNewline -ForegroundColor White
    $vramUsed = [int]$data[5].Trim()
    $vramTotal = [int]$data[6].Trim()
    $vramPercent = [math]::Round(($vramUsed / $vramTotal) * 100, 1)
    Write-Host "$vramUsed MB / $vramTotal MB ($vramPercent%)" -ForegroundColor Magenta
    
    Write-Host "`n" + ("=" * 50) -ForegroundColor Gray
    Write-Host "Status: " -NoNewline -ForegroundColor White
    if ($gpuUtil -eq 0 -and $data[4].Trim() -lt 10) {
        Write-Host "IDLE (No workload)" -ForegroundColor Green
    } elseif ($gpuUtil -lt 20) {
        Write-Host "Light Load" -ForegroundColor Yellow
    } elseif ($gpuUtil -lt 80) {
        Write-Host "Active" -ForegroundColor Yellow
    } else {
        Write-Host "Heavy Load" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1
}

