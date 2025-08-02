Write-Host "🚀 Smart Init Dev Tools (PowerShell)" -ForegroundColor Blue
Write-Host ""

# Execute the Python script
$scriptPath = Join-Path $PSScriptRoot "womm.py"
python $scriptPath install

if ($LASTEXITCODE -eq 0) {
    Write-Host "" 
    Write-Host "✅ Initialization process completed" -ForegroundColor Green
Write-Host "💡 If a new window opened, wait for it to finish" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de l'initialisation" -ForegroundColor Red
    Write-Host "💡 Make sure Python is installed and accessible" -ForegroundColor Yellow
}

Read-Host "Press Enter to continue"