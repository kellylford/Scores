# Changelog

All notable changes to the Scores application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.53.0-preview] - 2025-08-18

### Added
- **Statistics Feature**: Complete new statistics system for comprehensive sports analysis
  - Two-dialog interface: Choose Team/Player → Select statistic → View rankings
  - Multi-sport framework supporting MLB, NFL, NBA, NHL, NCAA Football
  - Professional-grade statistical categories with official data sources
  - Accessible design with full keyboard navigation and screen reader support
- **MLB Full Season Statistics**: Official MLB Stats API integration for baseball
  - 39 comprehensive statistical categories (vs 18 from ESPN)
  - Hitting statistics: 16 categories including advanced metrics (AVG, OPS, SB, etc.)
  - Pitching statistics: 15 categories with complete season data (ERA, Saves, etc.)
  - Fielding statistics: 8 categories for defensive analysis
  - Official MLB source with full season totals
  - Parallel loading for optimal performance (6x faster: 157ms vs 953ms)
- **Enhanced Baseball Information**: Improved game details and pitch location system
  - Pitch location validation with 85.4% strike zone accuracy
  - Enhanced game details display (venue, weather, broadcast info)
  - Better configuration options for game information fields
  - Cross-game validation with real umpire call analysis

### Fixed
- **Statistics Display**: Resolved "No player stats available for mlb" error
  - Fixed data format conversion between MLB API and UI expectations
  - Proper player name, stat value, and team information display
  - Seamless integration with existing statistics interface
- **MLB Data Quality**: Eliminated misleading limited-game statistics
  - Real season totals replacing recent performance samples
  - Complete statistical picture for informed analysis

### Changed
- **Statistics Architecture**: New comprehensive statistics system implementation
- **MLB Data Source**: ESPN API → Official MLB Stats API for baseball statistics
- **Data Coverage**: Recent games → Full season comprehensive statistics
- **Performance Optimization**: Enhanced concurrent request handling for statistics
- **User Interface**: Added Statistics menu option to all major sports

### Technical Details
- **Statistics Framework**: Scalable system ready for all major sports
- **MLB API Integration**: statsapi.mlb.com/api/v1/stats/leaders endpoints
- **No Authentication Required**: Public MLB API endpoints
- **Backward Compatibility**: All existing functionality preserved
- **Enhanced Error Handling**: Robust statistics processing and display

## [0.52.0-preview] - 2025-08-16

### Added
- **Live Scores Feature**: Real-time sports monitoring with auto-refresh capabilities
  - Multiple refresh intervals: 10s, 15s, 30s, 60s, 2min, 5min
  - Continuous background updates for live game tracking
  - Resource-efficient monitoring with pause/resume functionality
- **Scoring Drive Enhancement**: Visual identification system for football scoring plays
  - Touchdown indicators with "TD 7pts" badges
  - Field goal markers with "FG 3pts" badges  
  - Missed field goal, turnover, punt, and safety indicators
  - WCAG AA compliant color coding for accessibility
  - Enhanced drive summaries with scoring context
- **Enhanced Football Display**: Comprehensive game situation awareness
  - Hybrid format showing down/distance + drive statistics
  - Redzone indicators for teams in scoring position
  - Last play information for momentum context
  - Consistent team naming and score formatting
- **Command Line Options**: Quick access for power users
  - `--live`: Shorthand to launch Live Scores directly
  - `--live-scores`: Full command option for Live Scores mode
- **Multi-Platform Research**: Comprehensive analysis document for Mac and iOS expansion
- **Windows UIA Integration**: Enhanced accessibility with notification helpers

### Fixed
- **Score Display**: Resolved missing scores in football game listings
- **Team Naming**: Fixed inconsistent team name formatting across views
- **Navigation**: Improved startup parameter handling and validation
- **Memory Management**: Enhanced cleanup for long-running Live Scores sessions

### Changed
- **ESPN API Integration**: Enhanced data extraction for scoring drive detection
- **Performance**: Optimized real-time update processing and resource usage
- **Code Organization**: Improved project structure with comprehensive testing
- **Documentation**: Expanded guides for new features and implementation details

### Technical Details
- **NFL & NCAAF Support**: Scoring drive enhancement works with both professional and college football
- **Accessibility Compliance**: Full WCAG AA compliance for visual indicators
- **Background Processing**: Efficient real-time updates without blocking UI
- **Cross-Platform Planning**: Research completed for future Mac and iOS versions

### Build Artifacts
- `dist/Scores.exe` - Enhanced Windows executable (~43MB due to new features)
- Improved startup performance and resource management

## [0.51.0-preview] - 2025-08-15

### Added
- **Season Selection**: Enhanced team schedule dialogs with season dropdown for viewing historical data
- **Command Line Interface**: Comprehensive CLI options for direct navigation to specific sport sections
  - Game views: `--mlb`, `--nfl`, `--nba`, `--nhl`, `--ncaaf`
  - Teams views: `--mlb-teams`, `--nfl-teams`, etc.
  - Standings views: `--mlb-standings`, `--nfl-standings`, etc.
- **Accessibility Improvements**: 
  - Replaced QListWidget with AccessibleTable in teams dialogs for better screen reader support
  - Enhanced focus management in team schedule dialogs
  - Added proper accessible names and descriptions to UI components
- **Smart Navigation**: Enhanced team schedule dialogs now focus on today's games or next upcoming games
- **Visual Enhancements**: Today's games are highlighted with bold text and light yellow background

### Fixed
- **Team Name Display**: Fixed team names to show proper team nicknames instead of abbreviations
- **Date Display**: Enhanced date formatting for historical seasons to include year
- **Cache Management**: Cleaned up Python cache files from repository
- **Tab Accessibility**: Added setAccessibleName and setAccessibleDescription to all QTabWidget instances

### Changed
- **Schedule Loading**: Improved team schedule loading with background threading for better performance
- **Season Handling**: Enhanced season availability ranges for different sports leagues
- **UI Focus**: Improved focus management in schedule dialogs to highlight relevant games

### Technical Details
- **Enhanced CLI Support**: Full argument parsing with help documentation
- **Improved Data Display**: Better handling of historical vs current season data
- **Accessibility Standards**: Compliance improvements for screen reader compatibility

### Build Artifacts
- Same as 0.5.0: `dist/Scores.exe` - Standalone Windows executable
- Enhanced command line capabilities for power users

## [0.5.0-preview] - 2025-08-13

### Added
- Complete virtual environment setup with Python 3.13.6
- Comprehensive build system with PyInstaller
- Windows executable generation (standalone ~40MB)
- Enhanced build script (`build-enhanced.bat`) with error handling
- Minimal and complete requirements files
- Comprehensive build documentation (`BUILD_GUIDE.md`)
- Setup completion guide (`SETUP_COMPLETE.md`)

### Fixed
- Fixed `main.py` import issues - now works as alternative entry point
- Resolved PyQt6 6.9.1 compatibility
- Fixed dependency management with proper virtual environment isolation

### Changed
- Updated build process to use virtual environment
- Improved error handling in build scripts
- Enhanced documentation structure

### Technical Details
- **Python Version**: 3.13.6
- **GUI Framework**: PyQt6 6.9.1
- **HTTP Library**: requests 2.32.4
- **Build Tool**: PyInstaller 6.15.0
- **Target Platform**: Windows 10/11 (x64)

### Build Artifacts
- `dist/Scores.exe` - Standalone Windows executable
- `.venv/` - Isolated Python virtual environment
- `requirements.txt` - Complete dependency list
- `requirements-minimal.txt` - Essential dependencies only

### Installation
1. Download `Scores.exe` from releases
2. Run directly (no installation required)
3. For development: use virtual environment setup

### Known Issues
- Audio features require Windows sound system
- Application requires internet connection for ESPN API data
- First launch may take longer due to PyQt6 initialization

### Notes
This is a preview release focusing on build system improvements and deployment preparation. The core sports scoring functionality remains stable from previous versions.
