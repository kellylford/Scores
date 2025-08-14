# Scores Application - Build and Deployment Guide

## Overview
The Scores application is a comprehensive sports analysis tool supporting MLB and NFL data. It's built with PyQt6 and can be packaged as a standalone Windows executable.

## Project Structure
- `scores.py` - Main application file (primary entry point)
- `main.py` - Alternative entry point (imports and runs scores.py)
- `requirements.txt` - Complete dependency list with versions
- `requirements-minimal.txt` - Essential dependencies only
- `build-enhanced.bat` - Automated build script
- `build.bat` - Original build script

## Dependencies
### Core Requirements
- **PyQt6** (6.9.1) - GUI framework
- **requests** (2.32.4) - HTTP requests for API calls

### Build Requirements
- **PyInstaller** (6.15.0) - For creating Windows executable

### Optional Audio Dependencies
- **winsound** (built-in on Windows) - Audio feedback for pitch mapping

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# Or in bash
source .venv/Scripts/activate
```

### 3. Install Dependencies
```bash
# Install minimal requirements
pip install -r requirements-minimal.txt

# Or install full requirements
pip install -r requirements.txt
```

## Running the Application

### From Source
```bash
# Option 1: Direct execution
python scores.py

# Option 2: Via main.py
python main.py
```

### From Executable
```bash
# After building (see below)
dist/Scores.exe
```

## Building Windows Executable

### Option 1: Automated Build (Recommended)
```bash
build-enhanced.bat
```

This script will:
- Create virtual environment if needed
- Install dependencies
- Clean previous builds
- Build the executable
- Provide detailed status information

### Option 2: Manual Build
```bash
# Activate virtual environment
source .venv/Scripts/activate

# Build executable
pyinstaller --onefile --windowed --name=Scores scores.py
```

### Option 3: Original Build Script
```bash
build.bat
```

## Build Output
- **Executable**: `dist/Scores.exe` (~40MB)
- **Spec file**: `Scores.spec` (PyInstaller configuration)
- **Build artifacts**: `build/` directory

## Distribution
The built executable (`dist/Scores.exe`) is completely standalone and includes:
- Python runtime
- PyQt6 GUI framework
- All application dependencies
- Application code and assets

It can be distributed to other Windows machines without requiring Python installation.

## Entry Points Comparison

### scores.py (Primary)
- Main application file
- Contains the complete SportsScoresApp class
- Direct PyQt6 application instantiation
- **Recommended for building executable**

### main.py (Alternative)
- Wrapper entry point
- Imports SportsScoresApp from scores.py
- Provides consistent entry point interface
- Useful for development and testing

## Build Configuration
The PyInstaller build uses these options:
- `--onefile`: Creates single executable file
- `--windowed`: Removes console window (GUI-only)
- `--name=Scores`: Sets executable name

## Troubleshooting

### Common Build Issues
1. **PyQt6 import errors**: Ensure PyQt6 is installed in virtual environment
2. **Missing modules**: Check all imports are available in virtual environment
3. **Large executable size**: This is normal for PyQt6 applications (~40MB)

### Runtime Issues
1. **API connectivity**: Application requires internet connection for sports data
2. **Audio issues**: Audio features require Windows sound system
3. **Display scaling**: May need adjustment on high-DPI displays

## Development Notes
- Application supports both MLB and NFL data
- Features audio feedback for baseball pitch mapping
- Includes accessibility features for screen readers
- Uses ESPN API for sports data
- Caches data for improved performance
