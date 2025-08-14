@echo off
echo Building Sports Scores Windows Executable...
echo.

REM Clean previous builds
if exist "dist" (
    echo Cleaning previous build...
    rmdir /s /q "dist"
)

if exist "build" (
    rmdir /s /q "build"
)

echo.
echo Starting PyInstaller build...
echo This may take a few minutes...
echo.

REM Build the executable using the spec file
pyinstaller Scores.spec

if %ERRORLEVEL% equ 0 (
    echo.
    echo ================================
    echo BUILD SUCCESSFUL!
    echo ================================
    echo.
    echo Executable created: dist\SportsScores.exe
    echo.
    echo You can now run the application by double-clicking:
    echo %CD%\dist\SportsScores.exe
    echo.
    pause
) else (
    echo.
    echo ================================
    echo BUILD FAILED!
    echo ================================
    echo.
    echo Please check the error messages above.
    echo.
    pause
)
