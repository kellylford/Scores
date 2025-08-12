# Build instructions for Sports Scores Windows Executable

## Prerequisites
1. Python 3.8 or higher
2. All dependencies installed (see requirements.txt)
3. PyInstaller installed

## Quick Build
Simply run the batch file:
```
build_exe.bat
```

## Manual Build
If you prefer manual control:
```
pyinstaller scores.spec
```

## Build Output
- Executable will be created in: `dist\SportsScores.exe`
- This is a standalone executable that includes all dependencies
- No Python installation required on target machines

## Customization Options

### Adding an Icon
1. Create or obtain a .ico file
2. Edit `scores.spec` and change the `icon=None` line to:
   ```python
   icon='path_to_your_icon.ico'
   ```

### Console vs Windowed
- Current setting: Windowed application (no console window)
- To show console for debugging, edit `scores.spec`:
  ```python
  console=True
  ```

### File Size Optimization
- Current build uses UPX compression
- To disable compression (faster build, larger file):
  ```python
  upx=False
  ```

## Distribution
The `SportsScores.exe` file in the `dist` folder is completely portable and can be:
- Copied to any Windows machine
- Run without installing Python
- Distributed via USB, email, or download

## Troubleshooting

### Build Fails
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check that Python virtual environment is activated
3. Verify all source files are present

### Runtime Issues
1. Test the executable on the build machine first
2. Check Windows Defender/antivirus (may flag new executables)
3. Ensure target machine has Visual C++ Redistributable (usually pre-installed)

### Large File Size
- The executable will be 80-150MB due to including PyQt6 and Python runtime
- This is normal for PyQt applications
- Consider 7zip compression for distribution if needed

## Application Features Included
✅ Complete Sports Scores application
✅ ESPN API integration
✅ Play-by-play analysis with pitch details
✅ Hierarchical data organization
✅ Full accessibility support
✅ F5 refresh and F6 navigation
✅ Multi-sport support (MLB, NFL ready)
✅ Enhanced pitch details with velocity and type
