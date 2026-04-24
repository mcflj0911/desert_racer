batch_content = """@echo off
title Desert Racer Setup and Launcher
echo ==========================================
echo    Desert Racer: Definitive Edition
echo ==========================================
echo.

:: Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b
)

echo [1/3] Checking and installing dependencies (Pygame)...
python -m pip install --upgrade pip >nul
python -m pip install pygame-ce
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Pygame. Please check your internet connection.
    pause
    exit /b
)

echo.
echo [2/3] Looking for game assets...
set MISSING=0
if not exist "player_car.png" set /a MISSING+=1
if not exist "obstacle_car.png" set /a MISSING+=1
if not exist "police_car.png" set /a MISSING+=1

if %MISSING% gtr 0 (
    echo [WARNING] Some image assets are missing.
    echo The game will use colored blocks as fallbacks.
)

echo.
echo [3/3] Launching Desert Racer...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [GAME CRASHED] The game script encountered an error.
    echo Ensure the file is named 'desert_racer.py'.
    pause
)

exit
"""

with open("run_game.bat", "w", encoding="utf-8") as f:
    f.write(batch_content)
"""