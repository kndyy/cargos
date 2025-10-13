@echo off
echo ========================================
echo    Cargos Application for Windows
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from Microsoft Store or python.org
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if .venv exists, if not create it
if not exist ".venv" (
    echo Virtual environment not found. Creating .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import docxcompose" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
    echo.
)

REM Run the application
echo Starting Cargos Application...
echo.
python run.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    echo Check app.log for details.
    pause
) else (
    echo.
    echo Application closed successfully.
)
