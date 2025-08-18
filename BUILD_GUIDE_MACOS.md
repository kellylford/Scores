# Scores Application - macOS Build Guide

## Overview
This guide covers building the Scores application for macOS. The application supports both MLB and NFL data and is built with PyQt6. Two build options are available:

1. **macOS App Bundle** (.app) - Recommended for distribution
2. **Standalone Executable** - For terminal/command-line users

## Prerequisites

### System Requirements
- macOS 10.14 (Mojave) or later
- Python 3.8 or later (Python 3.13+ recommended)
- Xcode Command Line Tools (for PyInstaller)

### Install Xcode Command Line Tools
```bash
xcode-select --install
```

## Quick Build

### Option 1: App Bundle (Recommended)
```bash
# Create and build .app bundle
./build-macos-app.sh
```

### Option 2: Standalone Executable
```bash
# Create standalone executable
./build-macos.sh
```

## Manual Setup and Build

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install application dependencies
pip install -r requirements-minimal.txt
```

### 3. Build Options

#### App Bundle (.app)
```bash
pyinstaller \
    --onedir \
    --windowed \
    --name=Scores \
    --osx-bundle-identifier=com.kellylford.scores \
    --add-data="README.md:." \
    main.py
```

#### Standalone Executable
```bash
pyinstaller --onefile --windowed --name=Scores main.py
```

## Build Output

### App Bundle Build
- **Location**: `dist/Scores.app`
- **Size**: ~77MB
- **Type**: macOS Application Bundle
- **Installation**: Copy to Applications folder
- **Launch**: Double-click or via Launchpad

### Standalone Build
- **Location**: `dist/Scores`
- **Size**: ~29MB
- **Type**: Unix Executable
- **Launch**: Double-click or `./Scores` in terminal

## Installation and Distribution

### App Bundle Installation
1. **Automated**: Run `dist/install-scores.sh`
2. **Manual**: Copy `dist/Scores.app` to `/Applications/`

### Running the Application
1. **From Applications**: Launch via Launchpad or Applications folder
2. **From Terminal**: 
   ```bash
   open dist/Scores.app
   # or
   ./dist/Scores
   ```

### Security Settings
If macOS prevents the app from running:
1. Go to **System Preferences > Security & Privacy**
2. Click **"Open Anyway"** when prompted
3. Or use: `sudo spctl --master-disable` (not recommended for security)

## Cross-Platform Features

### Audio Support
- **macOS**: Uses system audio framework
- **Windows Audio**: Gracefully disabled on macOS
- **Sound Effects**: Pitch mapping audio works on macOS

### Platform Detection
The application automatically detects macOS and:
- Disables Windows-specific features (winsound, Windows notifications)
- Uses macOS-native audio systems
- Applies appropriate UI styling

## Architecture Support

### Apple Silicon (M1/M2/M3)
- Native ARM64 support
- Optimized performance
- Universal binary compatible

### Intel Macs
- x86_64 support
- Full compatibility
- May require Rosetta for dependencies

## Development and Testing

### Running from Source
```bash
# Activate virtual environment
source .venv/bin/activate

# Run application
python main.py

# Or directly
python scores.py
```

### Testing Build
```bash
# Test app bundle
open dist/Scores.app

# Test executable
./dist/Scores
```

## Troubleshooting

### Common Build Issues

#### PyInstaller Errors
```bash
# Clean build artifacts
rm -rf build dist *.spec

# Rebuild
./build-macos-app.sh
```

#### Missing Dependencies
```bash
# Reinstall dependencies
pip install -r requirements-minimal.txt --force-reinstall
```

#### Permission Issues
```bash
# Make scripts executable
chmod +x build-macos.sh
chmod +x build-macos-app.sh
```

### Runtime Issues

#### "App is damaged" Error
```bash
# Remove quarantine attribute
sudo xattr -rd com.apple.quarantine dist/Scores.app
```

#### High DPI Display Issues
- Application should auto-scale on Retina displays
- If issues persist, try running in low-resolution mode

#### Network Connectivity
- Ensure internet connection for ESPN API
- Check firewall settings if needed

## Distribution Considerations

### Code Signing (Optional)
For wider distribution:
```bash
# Sign the app (requires Apple Developer account)
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/Scores.app
```

### Notarization (Optional)
For App Store or wider distribution:
```bash
# Submit for notarization
xcrun notarytool submit dist/Scores.app --keychain-profile "notarytool-profile" --wait
```

### DMG Creation (Optional)
```bash
# Create disk image for distribution
hdiutil create -volname "Scores" -srcfolder dist/Scores.app -ov -format UDZO dist/Scores.dmg
```

## File Structure

### Build Scripts
- `build-macos.sh` - Simple executable build
- `build-macos-app.sh` - App bundle build
- `dist/install-scores.sh` - Installation helper

### Build Artifacts
- `build/` - Temporary build files
- `dist/` - Final built applications
- `*.spec` - PyInstaller configuration

## Performance Notes

### Startup Time
- App bundle: ~2-3 seconds
- Executable: ~1-2 seconds
- From source: <1 second

### Memory Usage
- Typical: 50-80MB RAM
- With active data: 80-120MB RAM
- UI framework overhead: ~30MB

### Network Usage
- Initial load: 1-5MB (depending on active games)
- Periodic updates: 100KB-1MB
- No data stored locally

## Compatibility

### macOS Versions
- **Minimum**: macOS 10.14 (Mojave)
- **Recommended**: macOS 11.0 (Big Sur) or later
- **Tested**: macOS 12.0 (Monterey) through macOS 15.0 (Sequoia)

### Hardware
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for app bundle, 50MB for executable
- **Network**: Required for live data

## Support

### Logs and Debugging
```bash
# Run with verbose output
./dist/Scores --verbose

# Check system logs
log show --predicate 'process == "Scores"' --last 1h
```

### Known Limitations
1. Windows-specific audio features disabled
2. Windows notifications not available
3. Some UI elements may look different from Windows version

This macOS build provides full functionality equivalent to the Windows version while respecting macOS design patterns and security requirements.
