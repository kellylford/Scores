# TheBench - Development Archive

This directory contains all the development files, test scripts, documentation, and analysis tools that were moved from the main project directory to keep it clean and focused.

## Contents Overview

### Test Scripts
- All `test_*.py` files - Unit tests and integration tests
- Development test scripts for various features

### Analysis Tools  
- All `analyze_*.py` files - Data analysis scripts
- All `debug_*.py` files - Debugging utilities
- All `check_*.py` files - Validation scripts
- Coordinate analysis and validation tools

### Documentation
- All `.md` documentation files (except main README.md)
- API guides, technical documentation, development notes
- Enhancement guides and implementation summaries

### Demo & Development Files
- Audio system development and testing files
- Interactive demos and proof-of-concepts
- HTML table helpers and accessibility demos
- Strike zone validation tools
- **Note**: Core audio system files (`simple_audio_mapper.py`, `stereo_audio_mapper.py`, `pitch_exploration_dialog.py`) were moved back to root directory as they are required by the main application

### Data Files
- All `.csv` data files from analysis
- All `.json` data files and API responses  
- All `.html` game logs and reports
- All `.txt` temporary and analysis files

### Web Application
- `web_app/` - Complete web interface
- `platforms/` - Platform-specific implementations
- `api_exploration/` - API research and testing
- `PitchData/` - Baseball pitch data analysis

## Purpose
These files are preserved here for:
- Future reference and development
- Test case preservation
- Documentation history
- Analysis tool availability

## Files Moved Back to Root Directory
The following files were initially moved to TheBench but had to be restored to the root directory because they are essential for the main application:

- ✅ `simple_audio_mapper.py` - Core audio mapping system (required by scores.py)
- ✅ `stereo_audio_mapper.py` - Stereo audio functionality (required by simple_audio_mapper.py)  
- ✅ `pitch_exploration_dialog.py` - Pitch exploration dialog (required by scores.py)

These files are critical for:
- Pitch audio exploration features
- Context menu functionality (Shift+F10)
- Strike zone audio mapping
- Stereo audio positioning

## Retrieval
If any file is needed back in the main directory, simply move it from TheBench back to the root as needed.

---
*Archive created: August 12, 2025*
*Last updated: August 12, 2025*
*Total items currently archived: 184*
*Items moved back to root: 3*
