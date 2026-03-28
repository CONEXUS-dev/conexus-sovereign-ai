# Vargas Dev Launcher — ensures Qdrant is running, then starts the bot.
# Usage: pwsh scripts/dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Vargas Dev Launcher ===" -ForegroundColor Cyan

# 1. Check if Qdrant container exists and is running
$container = docker ps -a --filter "name=vargas-qdrant" --format "{{.Status}}" 2>$null
if ($LASTEXITCODE -ne 0 -or -not $container) {
    Write-Host "Starting new Qdrant container..." -ForegroundColor Yellow
    docker run -d --name vargas-qdrant -p 6333:6333 qdrant/qdrant
} elseif ($container -notlike "Up*") {
    Write-Host "Restarting Qdrant container..." -ForegroundColor Yellow
    docker start vargas-qdrant
} else {
    Write-Host "Qdrant already running." -ForegroundColor Green
}

# 2. Wait for Qdrant to be ready
Write-Host "Waiting for Qdrant..." -NoNewline
for ($i = 0; $i -lt 15; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri "http://localhost:6333/collections" -TimeoutSec 2 -ErrorAction Stop
        Write-Host " ready." -ForegroundColor Green
        break
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
    }
}

# 3. Start Vargas
Write-Host "Starting Vargas..." -ForegroundColor Cyan
python -m project_vargas.discord.bot
