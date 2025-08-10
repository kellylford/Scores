# Sports Scores Application - Technical Guide

**Version:** 0.8.0 Beta  
**For Developers, Power Users, and Troubleshooting**

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation & Setup](#installation--setup)
3. [Troubleshooting](#troubleshooting)
4. [Technical Architecture](#technical-architecture)
5. [API Information](#api-information)
6. [Accessibility Technical Details](#accessibility-technical-details)
7. [Building from Source](#building-from-source)
8. [Known Technical Issues](#known-technical-issues)

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 10 (64-bit) or newer
- **Memory:** 4GB RAM
- **Storage:** 50MB free space
- **Network:** Internet connection for live data
- **Dependencies:** None (standalone executable)

### Recommended
- **OS:** Windows 11 (64-bit)
- **Memory:** 8GB RAM
- **Network:** Stable broadband connection
- **Screen Reader:** JAWS 2020+, NVDA 2021+, or Windows Narrator

---

## Installation & Setup

### Standalone Executable
1. Download `SportsScores.exe` from GitHub releases
2. No installation required - run directly
3. Windows may show security warning (normal for unsigned executables)
4. Allow through Windows Defender if prompted

### Running from Source Code
```bash
# Clone repository
git clone https://github.com/kellylford/Scores.git
cd Scores

# Install dependencies
pip install PyQt6 requests

# Run application
python scores.py
```

---

## Troubleshooting

### Application Won't Start

#### Problem: "Application failed to start"
**Causes:**
- Missing Visual C++ Redistributables
- Antivirus blocking execution
- Corrupted download

**Solutions:**
1. Download Microsoft Visual C++ Redistributable (latest)
2. Add exception in antivirus software
3. Re-download executable from GitHub releases
4. Run as administrator (temporary test)

#### Problem: "ModuleNotFoundError" (source code)
**Solution:**
```bash
pip install PyQt6 requests
```

### Network & Data Issues

#### Problem: No games showing / Empty lists
**Causes:**
- No internet connection
- ESPN API temporarily unavailable
- Firewall blocking application

**Solutions:**
1. Check internet connection
2. Try different date (Alt+P/Alt+N)
3. Refresh the view (F5 or refresh button)
4. Check firewall settings
5. Wait and retry (API may be temporarily down)

#### Problem: Incomplete game data
**Explanation:** 
- ESPN API doesn't always have complete data
- Live games may have partial information
- Historical games usually have more complete data

**Workaround:**
- Try games from previous days
- Check multiple games to verify API status

### Navigation & Interface Issues

#### Problem: Keyboard navigation not working
**Solutions:**
1. Press Tab to establish focus in main window
2. Check if focus is trapped in a text field
3. Use Alt+B to return to main navigation
4. Press Escape to reset focus
5. Restart application if persistent

#### Problem: Export button missing
**Causes:**
- Not in correct view (must be in plays/drives view)
- Game doesn't have detailed play data
- Network error during data fetch

**Solutions:**
1. Navigate to game details first
2. Select "Plays" (baseball) or "Drives" (football) section
3. Ensure game has completed and has play data
4. Try a different game with confirmed play data

### Screen Reader Issues

#### Problem: Screen reader not announcing content
**Solutions:**
1. Ensure screen reader is running before starting application
2. Use Tab key to establish focus
3. Try arrow keys for list navigation
4. Check screen reader's application-specific settings
5. Restart both screen reader and application

#### Problem: Table navigation limited
**Explanation:**
- Current limitation of Qt framework integration
- Working toward enhanced table accessibility
- Basic arrow key navigation available

**Workaround:**
- Use arrow keys for basic table navigation
- Use exported HTML files for advanced table features

---

## Technical Architecture

### Framework & Dependencies
- **GUI Framework:** PyQt6
- **HTTP Client:** requests library
- **Data Source:** ESPN API (unofficial endpoints)
- **Export Format:** HTML5 with semantic markup
- **Platform:** Windows desktop application

### Key Components
- **Main Application:** `scores.py` - Entry point and main UI
- **API Service:** `services/api_service.py` - ESPN API integration
- **Data Models:** `models/` - Game, news, standings data structures
- **Accessibility:** `accessible_table.py` - Enhanced table components
- **Exception Handling:** `exceptions.py` - Custom error types

### Data Flow
```
ESPN API → API Service → Data Models → UI Components → User
```

---

## API Information

### Data Source
- **Provider:** ESPN (unofficial API endpoints)
- **Base URL:** `https://site.api.espn.com/apis/site/v2/sports/`
- **Rate Limiting:** None observed, but application implements reasonable delays
- **Data Freshness:** Real-time for live games, static for completed games

### Supported Leagues
- **MLB** - Major League Baseball
- **NFL** - National Football League  
- **NBA** - National Basketball Association
- **NHL** - National Hockey League
- **NCAAF** - College Football
- **NCAAB** - College Basketball

### API Reliability
- **Uptime:** Generally high (ESPN production infrastructure)
- **Data Quality:** Varies by sport and game status
- **Completeness:** Play-by-play data not available for all games
- **Historical Data:** Available but may be limited for older games

---

## Accessibility Technical Details

### Screen Reader Compatibility
- **JAWS:** Basic compatibility, enhanced table features limited
- **NVDA:** Good compatibility with standard navigation
- **Windows Narrator:** Basic functionality supported
- **VoiceOver (macOS):** Not supported (Windows application)

### Qt Accessibility Framework
- **Implementation:** Uses Qt's built-in accessibility APIs
- **Focus Management:** Custom focus restoration after dialogs
- **Role Mapping:** Standard Qt widget roles
- **Property Setting:** Accessible names and descriptions

### Known Limitations
- **Virtual Cursor:** Qt tables don't activate screen reader virtual cursor mode
- **Table Navigation:** Limited to basic arrow key navigation
- **Complex Widgets:** Some custom widgets may have limited accessibility

### Future Improvements
- Investigating QWebEngineView for enhanced table accessibility
- Custom accessibility providers for complex widgets
- ARIA-style attribute mapping

---

## Building from Source

### Prerequisites
```bash
# Python 3.9+ required
python --version

# Install build dependencies
pip install PyQt6 requests pyinstaller
```

### Build Process
```bash
# Clone and setup
git clone https://github.com/kellylford/Scores.git
cd Scores

# Install dependencies
pip install -r requirements.txt

# Build executable
python -m PyInstaller SportsScores_Fixed.spec

# Output location
# dist/SportsScores.exe
```

### Build Configuration
- **Spec File:** `SportsScores_Fixed.spec`
- **Hidden Imports:** PyQt6 modules, project modules
- **Excluded Modules:** Optimization for size
- **Console:** Disabled (windowed application)

---

## Known Technical Issues

### High Priority
1. **Table Accessibility:** Limited screen reader table navigation features
2. **API Dependencies:** Application reliability tied to ESPN API availability
3. **Error Recovery:** Limited graceful handling of network failures

### Medium Priority
1. **Memory Usage:** Large datasets can consume significant memory
2. **Startup Time:** Cold start can be slow on some systems
3. **File Permissions:** Export may fail in restricted directories

### Low Priority
1. **Window Scaling:** May not handle high DPI displays optimally
2. **Theme Support:** Limited visual customization options
3. **Localization:** English language only

---

## Development Status

### Current Version: 0.8.0 Beta
- **Feature Complete:** Core functionality implemented
- **Known Issues:** Table accessibility, export scope
- **Performance:** Acceptable for typical usage
- **Stability:** Good for daily use

### Roadmap to 1.0
1. **Enhanced table accessibility** - Priority 1
2. **Export expansion** to all sports - Priority 2
3. **Search and favorites** - Priority 3
4. **Performance optimization** - Priority 4
5. **Error handling improvements** - Priority 5

---

## Getting Help

### Documentation
- **User Guide:** `USER_GUIDE_v2.md` - End user instructions
- **Quick Reference:** `QUICK_REFERENCE_v2.md` - Essential shortcuts
- **GitHub Issues:** Report bugs and feature requests

### Support Channels
- **GitHub Repository:** https://github.com/kellylford/Scores
- **Issue Tracker:** For bug reports and feature requests
- **Documentation:** Always check latest docs for solutions

---

**Technical Guide Version:** 1.0  
**Application Version:** 0.8.0 Beta  
**Last Updated:** August 10, 2025

*This guide covers technical aspects, troubleshooting, and development information.*
