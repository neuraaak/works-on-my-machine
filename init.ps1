Write-Host "🚀 Smart Init Dev Tools (PowerShell)" -ForegroundColor Blue
Write-Host ""

# Exécuter le script Python
$scriptPath = Join-Path $PSScriptRoot "init.py"
python $scriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "" 
    Write-Host "✅ Processus d'initialisation terminé" -ForegroundColor Green
    Write-Host "💡 Si une nouvelle fenêtre s'est ouverte, attendez qu'elle se termine" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de l'initialisation" -ForegroundColor Red
    Write-Host "💡 Vérifiez que Python est installé et accessible" -ForegroundColor Yellow
}

Read-Host "Appuyez sur Entrée pour continuer"