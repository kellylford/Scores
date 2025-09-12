@echo off
REM Code quality check script for Scores application
REM Runs all code quality tools: formatting, linting, type checking, and tests

echo Running code quality checks for Scores...

echo.
echo [1/5] Checking code formatting with Black...
black --check --diff .
if errorlevel 1 (
    echo FAILED: Code formatting issues found. Run 'black .' to fix.
    set /a errors+=1
) else (
    echo PASSED: Code formatting is correct.
)

echo.
echo [2/5] Checking import sorting with isort...
isort --check-only --diff .
if errorlevel 1 (
    echo FAILED: Import sorting issues found. Run 'isort .' to fix.
    set /a errors+=1
) else (
    echo PASSED: Import sorting is correct.
)

echo.
echo [3/5] Running code style checks with flake8...
flake8 . --max-line-length=88 --extend-ignore=E203,W503
if errorlevel 1 (
    echo FAILED: Code style issues found.
    set /a errors+=1
) else (
    echo PASSED: Code style is correct.
)

echo.
echo [4/5] Running type checks with mypy...
mypy scores.py main.py --ignore-missing-imports
if errorlevel 1 (
    echo FAILED: Type checking issues found.
    set /a errors+=1
) else (
    echo PASSED: Type checking passed.
)

echo.
echo [5/5] Running tests...
pytest tests/unit/ -v
if errorlevel 1 (
    echo FAILED: Some tests failed.
    set /a errors+=1
) else (
    echo PASSED: All tests passed.
)

echo.
if defined errors (
    echo SUMMARY: %errors% check(s) failed. Please fix the issues above.
    exit /b 1
) else (
    echo SUMMARY: All code quality checks passed!
    exit /b 0
)