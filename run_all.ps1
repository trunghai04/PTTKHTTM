param(
    [switch]$UseDocker
)

# Luôn chạy script từ thư mục chứa dự án
Set-Location $PSScriptRoot

if ($UseDocker) {
    Write-Host "🚀 Starting all services with Docker Compose..." -ForegroundColor Green
    docker-compose up --build
    exit
}

Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "cd `"$PSScriptRoot\backend`"; uvicorn app.main:app --reload"

Write-Host "🚀 Starting Frontend (React)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "cd `"$PSScriptRoot\frontend`"; npm run dev"

Write-Host ""
Write-Host "✅ Đã mở 2 cửa sổ PowerShell:" -ForegroundColor Green
Write-Host "   - Backend: FastAPI (http://localhost:8000)"
Write-Host "   - Frontend: React (http://localhost:3000)"
Write-Host ""
Write-Host "Nếu muốn dùng Docker thay vì chạy thủ công:" -ForegroundColor Yellow
Write-Host "   .\run_all.ps1 -UseDocker"

