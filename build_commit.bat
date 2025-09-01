@echo off
setlocal enabledelayedexpansion

REM Get current commit hash and commit message
for /f "tokens=*" %%i in ('git rev-parse --short HEAD') do set COMMIT_HASH=%%i
for /f "tokens=*" %%i in ('git log -1 --pretty^=format:%%s') do set COMMIT_MSG=%%i

REM Clean up commit message for filename (remove special characters)
set COMMIT_MSG_CLEAN=!COMMIT_MSG: =_!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN::=!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:/=!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:\=!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:*=!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:?=!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:^<=!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:^>=!
set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:|=!

REM Truncate if too long
if "!COMMIT_MSG_CLEAN:~30!" neq "" set COMMIT_MSG_CLEAN=!COMMIT_MSG_CLEAN:~0,30!

echo Building Scores application for commit !COMMIT_HASH!...
echo Commit: !COMMIT_MSG!
echo.

REM Set the virtual environment path
set VENV_PATH=C:\Users\kelly\GitHub\Scores\.venv

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "scores.spec" del "scores.spec"

REM Build the executable with commit-specific name
set BUILD_NAME=Scores_!COMMIT_HASH!_!COMMIT_MSG_CLEAN!
echo Creating executable: !BUILD_NAME!.exe...
"%VENV_PATH%\Scripts\python.exe" -m PyInstaller --onefile --windowed --name=!BUILD_NAME! main.py

REM Check if build was successful and copy to buildtesting
if exist "dist\!BUILD_NAME!.exe" (
    echo.
    echo =====================================
    echo Build successful! 
    echo =====================================
    
    REM Copy to buildtesting folder
    if not exist "buildtesting" mkdir "buildtesting"
    copy "dist\!BUILD_NAME!.exe" "buildtesting\!BUILD_NAME!.exe"
    
    echo Executable created at: buildtesting\!BUILD_NAME!.exe
    echo File size: 
    dir "buildtesting\!BUILD_NAME!.exe" | findstr "!BUILD_NAME!.exe"
    echo =====================================
) else (
    echo.
    echo =====================================
    echo Build failed! 
    echo =====================================
    echo Check the output above for errors.
    echo =====================================
)

echo.
