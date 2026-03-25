@echo off
SETLOCAL

REM --- AntennaForge Portable Launcher ---

REM 1. Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found in PATH.
    echo Please install Python 3.10+ or use an embeddable distribution.
    pause
    exit /b 1
)

REM 2. Check/Prepare Wheels
IF NOT EXIST "wheels" (
    IF NOT EXIST "offline_wheels.zip" (
        echo [Setup] Wheels not found. Checking internet connection...
        ping -n 1 8.8.8.8 >nul 2>&1
        IF %ERRORLEVEL% EQU 0 (
            echo [Setup] Internet detected. Downloading dependencies...
            python scripts\fetch_wheels.py
        ) ELSE (
            echo [Setup] No internet detected.
        )
    )

    IF EXIST "offline_wheels.zip" (
        echo [Setup] Unzipping offline wheels...
        powershell -command "Expand-Archive -Path 'offline_wheels.zip' -DestinationPath '.' -Force"
    ) ELSE (
        echo Error: 'wheels' folder or 'offline_wheels.zip' not found.
        echo Please run scripts/fetch_wheels.py on an internet-connected machine.
        pause
        exit /b 1
    )
)

REM 3. Check/Create Virtual Environment
IF NOT EXIST ".venv" (
    echo [Setup] Creating virtual environment...
    python -m venv .venv
)

REM 4. Check if dependencies are installed (using customtkinter as proxy)
.venv\Scripts\python -c "import customtkinter" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [Setup] Installing dependencies from local wheels...
    
    REM Upgrade pip in venv first
    .venv\Scripts\python -m pip install --no-index --find-links wheels pip setuptools
    
    REM Install project deps
    .venv\Scripts\python scripts\install_offline.py
)

REM 5. Launch App
echo [Launch] Starting AntennaForge...
.venv\Scripts\python AntennaForge.py

IF %ERRORLEVEL% NEQ 0 (
    echo Application exited with error.
    pause
)