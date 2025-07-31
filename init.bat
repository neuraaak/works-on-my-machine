@echo off
title Dev Tools - Smart Init
echo 🚀 Smart Init Dev Tools (Windows)
echo.

python "%~dp0init.py"

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors de l'initialisation
    echo 💡 Vérifiez que Python est installé et accessible
    pause
    exit /b 1
)

echo.
echo ✅ Processus d'initialisation terminé
echo 💡 Si une nouvelle fenêtre s'est ouverte, attendez qu'elle se termine
pause