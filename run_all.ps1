param(
    [switch]$UseDocker
)

# Luôn chạy script từ thư mục chứa dự án
Set-Location $PSScriptRoot

if ($UseDocker) {
    Write-Host "⚠️ Docker mode is deprecated for this project setup." -ForegroundColor Yellow
    Write-Host "   Running local backend + frontend instead..." -ForegroundColor Yellow
}

Write-Host "🚀 Starting Backend (FastAPI, local)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "cd `"$PSScriptRoot\backend`"; python -m uvicorn app.main:app --reload"

Write-Host "🚀 Starting Frontend (React, local)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "cd `"$PSScriptRoot\frontend`"; npm run dev"

Write-Host ""
Write-Host "✅ Đã mở 2 cửa sổ PowerShell:" -ForegroundColor Green
Write-Host "   - Backend: FastAPI (http://localhost:8000)"
Write-Host "   - Frontend: React (http://localhost:3000)"
Write-Host ""
Write-Host "🔧 Nhớ cấu hình database trong backend/.env (MySQL khuyến nghị):" -ForegroundColor Yellow
Write-Host "   DATABASE_URL=mysql+pymysql://root:password@localhost:3306/text_classification"

