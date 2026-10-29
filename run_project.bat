@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Python virtual environment not found. Run setup_windows.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "main.py"
if errorlevel 1 (
    echo Shongwe Motors exited with an error.
    pause
    exit /b 1
)
endlocal
