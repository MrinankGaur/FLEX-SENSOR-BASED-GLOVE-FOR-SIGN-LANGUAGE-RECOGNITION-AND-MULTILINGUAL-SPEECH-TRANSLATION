@echo off
setlocal enabledelayedexpansion

set VENV_DIR=venv
set PYTHON_EXE=python

echo 🔧 Setting up Python environment...

REM Step 1: Check if Python exists
where %PYTHON_EXE% >nul 2>nul
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3 and ensure it's in PATH.
    exit /b 1
)

REM Step 2: Create venv if not exists
if not exist "%VENV_DIR%" (
    echo 🛠️ Creating virtual environment...
    %PYTHON_EXE% -m venv %VENV_DIR%
) else (
    echo ✅ Virtual environment already exists.
)

REM Step 3: Activate venv
call "%VENV_DIR%\Scripts\activate.bat"

REM Step 4: Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Step 5: Install dependencies
if exist requirements.txt (
    echo 📦 Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo ⚠️ requirements.txt not found. Skipping dependency installation.
)

echo.
echo ✅ Environment setup complete!
echo To activate manually later, run:
echo     call %VENV_DIR%\Scripts\activate.bat

endlocal
pause

