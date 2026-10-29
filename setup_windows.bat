@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher not found. Install Python 3.11 or 3.12 for Windows, then retry.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo Creating a Python 3.12 virtual environment...
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo Python 3.12 unavailable. Trying Python 3.11...
        py -3.11 -m venv .venv
        if errorlevel 1 (
            echo Neither Python 3.12 nor 3.11 is available. Install one of them.
            pause
            exit /b 1
        )
    )
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)
echo Setup complete. Run run_project.bat to start Shongwe Motors.
pause
endlocal
