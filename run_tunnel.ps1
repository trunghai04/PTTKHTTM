param(
    [string]$FrontendDomain = "bloopai.bloop.io.vn",
    [string]$ApiDomain = "api.bloopai.bloop.io.vn",
    [string]$FrontendUrl = "http://localhost:3000",
    [string]$ApiUrl = "http://localhost:8000"
)

Set-Location $PSScriptRoot

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "❌ cloudflared chưa được cài." -ForegroundColor Red
    Write-Host "   Cài nhanh: winget install Cloudflare.cloudflared" -ForegroundColor Yellow
    exit 1
}

Write-Host "🚀 Starting Cloudflare tunnel for frontend..." -ForegroundColor Green
Write-Host "   Domain: https://$FrontendDomain -> $FrontendUrl"
Start-Process powershell -ArgumentList "-NoExit", "cloudflared tunnel --url $FrontendUrl --hostname $FrontendDomain"

Write-Host "🚀 Starting Cloudflare tunnel for backend API..." -ForegroundColor Green
Write-Host "   Domain: https://$ApiDomain -> $ApiUrl"
Start-Process powershell -ArgumentList "-NoExit", "cloudflared tunnel --url $ApiUrl --hostname $ApiDomain"

Write-Host ""
Write-Host "✅ Đã mở 2 tunnel process." -ForegroundColor Green
Write-Host "   - Frontend: https://$FrontendDomain"
Write-Host "   - API:      https://$ApiDomain"
Write-Host ""
Write-Host "⚠️ Yêu cầu trước khi chạy thành công:" -ForegroundColor Yellow
Write-Host "   1) Domain đã nằm trên Cloudflare DNS"
Write-Host "   2) Bạn đã login cloudflared: cloudflared tunnel login"
Write-Host "   3) Frontend dùng API URL tương ứng (VITE_API_URL=https://$ApiDomain)"
