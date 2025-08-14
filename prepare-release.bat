@echo off
echo =====================================
echo Scores Application Release Preparation
echo =====================================
echo.

if "%1"=="" (
    echo Usage: prepare-release.bat ^<version^>
    echo Example: prepare-release.bat 0.6.0
    echo Example: prepare-release.bat 1.0.0-beta
    exit /b 1
)

set VERSION=%1
echo Preparing release for version: %VERSION%
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Update version file
echo %VERSION% > VERSION
echo Updated VERSION file to %VERSION%

REM Build the application
echo Building application...
call build-enhanced.bat

REM Check if build was successful
if not exist "dist\Scores.exe" (
    echo Build failed! Cannot create release without executable.
    exit /b 1
)

echo.
echo =====================================
echo Release Preparation Complete!
echo =====================================
echo.
echo Version: %VERSION%
echo Executable: dist\Scores.exe
echo.
echo Next steps:
echo 1. Update CHANGELOG.md with release notes
echo 2. Test the executable: dist\Scores.exe
echo 3. Commit changes: git add . && git commit -m "Release v%VERSION%"
echo 4. Create tag: git tag -a v%VERSION% -m "Release v%VERSION%"
echo 5. Push: git push origin main && git push origin v%VERSION%
echo 6. Create GitHub release with dist\Scores.exe
echo.
echo =====================================
pause
