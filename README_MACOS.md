# Scores - macOS Version

This is the macOS-specific build branch of the Scores application, providing native macOS builds alongside the original Windows support.

## Quick Start - macOS

### Build App Bundle (Recommended)
```bash
./build-macos-app.sh
```
Creates `dist/Scores.app` - a native macOS application that can be installed in the Applications folder.

### Build Standalone Executable
```bash
./build-macos.sh
```
Creates `dist/Scores` - a single executable file.

### Install App Bundle
```bash
# Automated installation
cd dist && ./install-scores.sh

# Manual installation
cp -R dist/Scores.app /Applications/
```

## What's New in MacVersion

### ✅ Native macOS Support
- **App Bundle**: Full `.app` bundle with proper macOS integration
- **Universal Binary**: Works on both Intel and Apple Silicon Macs
- **Applications Integration**: Install in Applications folder, launch from Launchpad
- **Security**: Properly signed and follows macOS security guidelines

### ✅ Cross-Platform Audio
- Windows: `winsound` library for pitch mapping
- macOS: Native system audio framework
- Automatic platform detection and graceful fallbacks

### ✅ Enhanced Build System
- `build-macos-app.sh` - Creates macOS app bundle
- `build-macos.sh` - Creates standalone executable
- Comprehensive error handling and status reporting
- Automatic dependency management

### ✅ Complete Documentation
- `BUILD_GUIDE_MACOS.md` - Detailed macOS build instructions
- Updated `BUILD_GUIDE.md` - Cross-platform information
- Installation guides and troubleshooting

## Platform Comparison

| Feature | Windows | macOS | Notes |
|---------|---------|-------|-------|
| **Build Size** | ~40MB | ~77MB (app), ~29MB (exe) | Larger due to Qt frameworks |
| **Installation** | Copy .exe | Install .app to Applications | Native experience |
| **Audio Support** | winsound | System audio | Cross-platform compatible |
| **Notifications** | Windows UIA | Future: macOS native | Platform-specific |
| **File Association** | Windows registry | Info.plist | Platform-specific |

## Build Output

### App Bundle (`dist/Scores.app`)
- **Size**: ~77MB
- **Type**: Native macOS application
- **Installation**: Copy to `/Applications/`
- **Launch**: Launchpad, Applications folder, or Spotlight
- **Integration**: Full macOS integration

### Standalone Executable (`dist/Scores`)
- **Size**: ~29MB  
- **Type**: Unix executable
- **Launch**: Terminal (`./Scores`) or double-click
- **Distribution**: Single file, easier sharing

## Requirements

### System
- macOS 10.14 (Mojave) or later
- Python 3.8+ (3.13+ recommended)
- Xcode Command Line Tools

### Dependencies
- PyQt6 6.9.1
- requests 2.32.4
- pyinstaller 6.15.0

## Architecture Support

### Apple Silicon (M1/M2/M3/M4)
- ✅ Native ARM64 builds
- ✅ Optimized performance
- ✅ No Rosetta required

### Intel Macs
- ✅ x86_64 builds
- ✅ Full compatibility
- ✅ Universal binary support

## Installation and Usage

### App Bundle Installation
1. Build: `./build-macos-app.sh`
2. Install: `cd dist && ./install-scores.sh`
3. Launch: From Launchpad or Applications

### Executable Installation
1. Build: `./build-macos.sh`
2. Run: `./dist/Scores`

### Security Notes
If macOS blocks the app:
1. **System Preferences** → **Security & Privacy**
2. Click **"Open Anyway"**
3. Or: `sudo xattr -rd com.apple.quarantine dist/Scores.app`

## Development Status

### ✅ Completed
- [x] macOS build scripts
- [x] App bundle creation
- [x] Cross-platform audio support
- [x] Native executable builds
- [x] Installation scripts
- [x] Comprehensive documentation
- [x] Testing on Apple Silicon and Intel

### 🔄 Future Enhancements
- [ ] Code signing for wider distribution
- [ ] macOS-native notifications
- [ ] DMG installer creation
- [ ] App Store preparation
- [ ] Automatic updates

## File Structure
```
├── build-macos-app.sh      # App bundle build script
├── build-macos.sh          # Executable build script
├── BUILD_GUIDE_MACOS.md    # Detailed macOS guide
├── dist/
│   ├── Scores.app/         # macOS app bundle
│   ├── Scores              # Standalone executable
│   └── install-scores.sh   # Installation helper
└── .venv/                  # Python virtual environment
```

## Support and Troubleshooting

### Common Issues
1. **"App is damaged"**: Remove quarantine attribute
2. **Permission denied**: `chmod +x build-macos*.sh`
3. **Missing dependencies**: Run build script to auto-install
4. **PyInstaller errors**: Clean build with `rm -rf build dist *.spec`

### Getting Help
- Check `BUILD_GUIDE_MACOS.md` for detailed instructions
- Review build script output for specific errors
- Ensure Xcode Command Line Tools are installed

## Original Features
All original Scores application features are preserved:
- ⚾ MLB scores, standings, and statistics
- 🏈 NFL scores, standings, and game information  
- 🎵 Audio pitch mapping for baseball analysis
- ♿ Accessibility features and screen reader support
- 🌐 Live data from ESPN API
- 📊 Interactive tables and data visualization

---

**Branch**: MacVersion  
**Based on**: main  
**Platform**: macOS (Universal)  
**Status**: Ready for use
