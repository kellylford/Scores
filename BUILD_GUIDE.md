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

### Option 1: build.py (Recommended)
```bash
.venv\Scripts\activate
python build.py
```

This is what CI runs, so it is the definition of a Scores build. It produces both
distributables:

- `dist/Scores/` — one-dir build; the input to the installer
- `dist/Scores.exe` — one-file portable build

Pass `--onedir` or `--onefile` to build just one of them.

### Option 2: Manual Build
```bash
# Activate virtual environment
source .venv/Scripts/activate

# Portable one-file build only
pyinstaller --onefile --windowed --name=Scores --add-data "user_guide.html;." main.py
```

### Option 3: Original Build Scripts
```bash
build-enhanced.bat
build.bat
```
These predate `build.py` and only produce the one-file exe.

## Building the Installer
```powershell
python build.py
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion=0.8.0 installer\scores.iss
# -> installer\Output\Scores-0.8.0-Setup.exe
```
The installer packages the **one-dir** output, never the one-file exe — see the
comment at the top of `build.py` for why. Full detail on the installer, the in-app
updater and code signing is in [docs/INSTALLER.md](docs/INSTALLER.md).

## Build Output
- **Installer input**: `dist/Scores/` (~73MB on disk)
- **Portable executable**: `dist/Scores.exe` (~28MB)
- **Installer**: `installer/Output/Scores-<version>-Setup.exe` (~22MB)
- **Build artifacts**: `build/onedir/` and `build/onefile/`

## Distribution
Both builds are completely standalone and include:
- Python runtime
- PyQt6 GUI framework
- All application dependencies
- Application code and assets

They can be distributed to other Windows machines without requiring Python
installation. Releases are code-signed by CI; local builds are not, so Windows
SmartScreen will warn on them.

## Releasing
Bump `version.py` **and** `VERSION`, write `docs/release-notes-v<version>.md`,
update `CHANGELOG.md`, then push a `v<version>` tag. The workflow verifies those
match, builds, signs, packages the installer and publishes the release. See
[docs/INSTALLER.md](docs/INSTALLER.md#cutting-a-release).

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
