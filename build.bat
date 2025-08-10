@echo off
echo Building Scores application...
echo.

REM Set the virtual environment path
set VENV_PATH=C:\Users\kelly\GitHub\Scores\.venv

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "scores.spec" del "scores.spec"

REM Build the executable using full paths
echo Creating executable...
"%VENV_PATH%\Scripts\python.exe" -m PyInstaller --onefile --windowed --name=Scores scores.py

REM Check if build was successful
if exist "dist\Scores.exe" (
    echo.
    echo =====================================
    echo Build successful! 
    echo =====================================
    echo Executable created at: dist\Scores.exe
    echo File size: 
    dir dist\Scores.exe | findstr "Scores.exe"
    echo.
    echo To run the application:
    echo   1. Navigate to the dist folder
    echo   2. Double-click Scores.exe
    echo   3. Or run: dist\Scores.exe
    echo =====================================
) else (
    echo.
    echo =====================================
    echo Build failed! 
    echo =====================================
    echo Check the output above for errors.
    echo Make sure all dependencies are installed.
    echo =====================================
)

echo.
pause

REM Check if build was successful
if exist "dist\Scores.exe" (
    echo.
    echo Build successful! Executable created at: dist\Scores.exe
    echo.
    echo To run the application, navigate to the dist folder and run Scores.exe
) else (
    echo.
    echo Build failed! Check the output above for errors.
)

echo.
pause
