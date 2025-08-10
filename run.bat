@echo off
REM Quick launcher for the Scores application
echo Starting Scores application...
if exist "dist\Scores.exe" (
    start "Scores App" "dist\Scores.exe"
) else (
    echo.
    echo Scores.exe not found in dist folder.
    echo Please run build.bat first to create the executable.
    echo.
    pause
)
