@echo off
REM Development setup script for Scores application
REM Installs development dependencies and sets up the environment

echo Setting up development environment for Scores...

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo Installing development dependencies...
pip install -e .[dev]

if errorlevel 1 (
    echo Error: Failed to install development dependencies
    exit /b 1
)

echo Running basic tests to verify setup...
pytest tests/unit/test_simple.py -v

if errorlevel 1 (
    echo Warning: Some tests failed, but setup is complete
) else (
    echo Development environment setup complete!
)

echo.
echo Available commands:
echo   pytest                 - Run all tests
echo   pytest tests/unit/     - Run unit tests only
echo   black .                - Format code
echo   isort .                - Sort imports
echo   flake8 .               - Check code style
echo   mypy scores.py         - Type checking

pause