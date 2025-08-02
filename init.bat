@echo off
title Dev Tools - Smart Init
echo 🚀 Smart Init Dev Tools (Windows)
echo.

python "%~dp0womm.py" install

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors de l'initialisation
    echo 💡 Make sure Python is installed and accessible
    pause
    exit /b 1
)

echo.
echo ✅ Initialization process completed
echo 💡 If a new window opened, wait for it to finish
pause