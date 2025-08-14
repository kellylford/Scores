@echo off
echo =====================================
echo Scores Application Build Script
echo =====================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment!
        echo Make sure Python is installed and accessible.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "Scores.spec" del "Scores.spec"

REM Build the executable
echo.
echo =====================================
echo Building executable...
echo =====================================
python -m PyInstaller --onefile --windowed --name=Scores main.py

REM Check if build was successful
if exist "dist\Scores.exe" (
    echo.
    echo =====================================
    echo Build SUCCESSFUL! 
    echo =====================================
    echo.
    echo Executable created at: dist\Scores.exe
    echo File size: 
    for %%I in (dist\Scores.exe) do echo %%~zI bytes (%%~zI / 1024 / 1024 MB^)
    echo.
    echo To run the application:
    echo   1. Navigate to the dist folder
    echo   2. Double-click Scores.exe
    echo   3. Or run from command line: dist\Scores.exe
    echo.
    echo The executable includes all dependencies and can be
    echo distributed to other Windows machines without requiring
    echo Python or any additional installations.
    echo =====================================
) else (
    echo.
    echo =====================================
    echo Build FAILED! 
    echo =====================================
    echo Check the output above for errors.
    echo Common issues:
    echo   - Missing dependencies (check requirements-minimal.txt)
    echo   - PyInstaller not installed
    echo   - Python path issues
    echo =====================================
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
pause
