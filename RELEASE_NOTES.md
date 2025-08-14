# Scores v0.5.0-preview Release Notes

## 🎉 What's New in v0.5.0-preview

This preview release focuses on **build system improvements** and **deployment preparation**, making the Scores application easier to build, distribute, and run on Windows machines.

### 🚀 Key Improvements

#### Enhanced Build System
- **Virtual Environment Setup**: Complete Python 3.13.6 isolated environment
- **Automated Building**: New `build-enhanced.bat` script with comprehensive error handling
- **Standalone Executable**: Single-file `Scores.exe` (~40MB) with all dependencies included
- **No Installation Required**: Executable runs on any Windows machine without Python

#### Developer Experience
- **Fixed Entry Points**: Both `scores.py` and `main.py` now work correctly
- **Clean Dependencies**: Separate minimal and complete requirements files
- **Comprehensive Documentation**: Detailed build guides and setup instructions
- **Improved Error Handling**: Better feedback during build process

#### Distribution Ready
- **Portable Executable**: `dist/Scores.exe` includes PyQt6, Python runtime, and all dependencies
- **Easy Deployment**: Copy single executable to any Windows machine
- **Version Tracking**: Added version file and changelog

### 📁 What's Included

#### Core Application
- `scores.py` - Main application (unchanged functionality)
- `main.py` - Alternative entry point (fixed import issues)
- All supporting modules and services

#### Build System
- `.venv/` - Python 3.13.6 virtual environment
- `build-enhanced.bat` - Automated build script
- `requirements.txt` - Complete dependency list (15 packages)
- `requirements-minimal.txt` - Essential dependencies (3 packages)

#### Documentation
- `BUILD_GUIDE.md` - Comprehensive setup and build instructions
- `SETUP_COMPLETE.md` - Setup verification and usage guide
- `CHANGELOG.md` - Detailed change history
- `VERSION` - Version tracking file

#### Distribution
- `dist/Scores.exe` - Ready-to-run Windows executable

### 💻 System Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: 100MB RAM minimum
- **Storage**: 50MB available space
- **Network**: Internet connection required for ESPN API data
- **Audio**: Windows sound system (optional, for audio features)

### 🎯 How to Use

#### End Users
1. Download `Scores.exe` from the release
2. Double-click to run (no installation needed)
3. Application will connect to ESPN API for live sports data

#### Developers
1. Clone the repository
2. Run `build-enhanced.bat` to set up environment and build
3. Use `source .venv/Scripts/activate` for development

### 🔧 Technical Details

| Component | Version |
|-----------|---------|
| Python | 3.13.6 |
| PyQt6 | 6.9.1 |
| requests | 2.32.4 |
| PyInstaller | 6.15.0 |

### 🐛 Known Issues

- Audio features require Windows sound system
- First launch may take 3-5 seconds (PyQt6 initialization)
- Large executable size (~40MB) due to bundled GUI framework

### 🔄 Upgrade Notes

- This version maintains compatibility with previous save files
- No configuration changes required
- Executable can replace previous versions directly

### 📝 What's Next

- Performance optimizations
- Additional sports league support
- Enhanced audio features
- Cross-platform builds (macOS, Linux)

### 🙋 Support

For issues or questions:
1. Check `BUILD_GUIDE.md` for setup help
2. Review `CHANGELOG.md` for known issues
3. Submit issues through the repository

---

**Download**: `Scores.exe` (39.9 MB)  
**Checksum**: Available in release assets  
**Build Date**: August 13, 2025
