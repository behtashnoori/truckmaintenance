# PowerShell script to start both backend and frontend servers

Write-Host "🚀 Starting TruckMaintenance Servers..." -ForegroundColor Green
Write-Host ""

# Start Backend in new window
Write-Host "Starting Backend (Flask)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$env:FLASK_APP='backend.app:create_app()'; `$env:FLASK_ENV='development'; python -m flask run --port 5000"

Start-Sleep -Seconds 2

# Start Frontend in new window  
Write-Host "Starting Frontend (Vite)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run frontend"

Write-Host ""
Write-Host "✅ Servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

