# Changelog

All notable changes to the Scores application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **College basketball was missing most of the games played**, the same ESPN
  `groups=` omission just fixed for college football and proportionally worse.
  A Saturday in January returned 21 of 145 men's Division I games and 4 of 122
  women's. Both now ask for Division I explicitly. Basketball needs no coverage
  setting the way football does — ESPN has no FBS/FCS-style split below Division
  I for it — and college hockey needs no change at all, since `groups=` returns
  nothing there and the plain call is already complete.

### Added
- **MLB wild card standings.** The standings view could only show divisions, so
  the playoff race — the thing most people are actually tracking in September —
  was not visible anywhere. Each league now shows its three division leaders
  followed by the 12-team wild card race, with the teams holding the three
  berths marked "Wild card 1/2/3" rather than separated by a drawn line, so a
  screen reader speaks the playoff cut instead of relying on a visual boundary.
  On Windows this is two extra tabs, "AL Wild Card" and "NL Wild Card", beside
  the six division tabs; on iOS it is a Divisions / Wild Card control at the top
  of the standings screen. Both load only when first opened, so the divisions
  view is never held up by the extra request.

  The data comes from MLB's own API (`statsapi.mlb.com`), whose
  `wildCardWithLeaders` request returns the division leaders and the race
  together with the ranks and games-back already named for the purpose. ESPN can
  also produce wild card standings, via `type=1` on the standings endpoint the
  apps already call; that route needs a second request for the leaders. Either
  source gives the same numbers — the published rank is used rather than a
  win-percentage sort so that teams tied on record land in a deterministic,
  official order.

- **Football week views list completed games before upcoming ones.** A week spans
  played and unplayed days at once, so with upcoming first a Saturday's finished
  games sat below a hundred that had not kicked off and read as missing entirely.
  Day-based sports are unchanged and keep the conventional in progress, upcoming,
  completed order, as does the all-sports Live Scores view. Section headers now
  carry a game count ("Completed, 57 games") so the size of each section is
  audible before entering it.

- **College football coverage is changeable from the scores screen**, not only
  from Settings. It edits the same saved preference.

### Fixed
- **College football was missing most of the games played.** ESPN serves the two
  Division I halves separately through its `groups=` scoreboard parameter, and
  the app asked only for FBS (`groups=80`). That is a small fraction of an
  opening weekend, which is largely FCS: on Saturday 29 August the scoreboard
  showed 8 games out of the 48 Division I games actually played. Coverage is now
  a setting on the home page settings dialog — **All Division I (FBS and FCS)**,
  the new default at around 200 games a week, or **FBS only** at around 100.
  A team's own schedule always uses the widest coverage, since it is filtered
  down to that team anyway and FBS-only returned nothing at all for an FCS team.
  Requests also send `limit=500`; without it ESPN pages the all-Division-I
  scoreboard off at 200. The same fix landed in the iOS app.

### In Progress
- **Game Wrap Up Feature**: ESPN text processing and game story extraction (under construction)
  - Core infrastructure implemented, text processing being refined
  - Game story text placeholders currently under investigation

## [0.9.4] - 2026-08-13

### Fixed
- **Fantasy cheatsheet: the Rank column skipped numbers.** It showed ESPN's
  published rank, which orders a far larger pool than a fantasy board — roughly
  1,750 defensive players, 51 punters and the 32 "Team QB" slots. Sorted by
  rank, the board ran 1 to 2565 with 1,539 gaps in it, jumping 36 to 69 near the
  top and 519 to 978 further down. The column now counts the board itself: 1, 2,
  3 with nothing missing, in exactly the order ESPN puts them. ESPN's own number
  is still shown on the player details screen and in the CSV export, for anyone
  cross-referencing their site.

## [0.9.3] - 2026-08-10

### Fixed
- **Fantasy cheatsheet: the board was missing two-thirds of the players ESPN
  ranks.** The pool was capped at ESPN's overall draft rank, on the assumption
  that rank tracked draft relevance. It does not — Ricky Pearsall ranks 1507 and
  is rostered in a third of ESPN leagues, Tyreek Hill ranks 1899 — so the cap
  was hiding players people actually draft. The board now carries every active
  fantasy-position player ESPN publishes a rank for: 1,026 rather than 368.
  Players ESPN ranks nowhere, and players it flags as inactive, are still left
  out; every one of those is owned in 0.0% of leagues.
- **Fantasy cheatsheet: ADP no longer invents a draft position.** ESPN gives
  undrafted players a placeholder ADP just past the end of a real draft rather
  than omitting it — around 170 this season, shared by 826 of the 1,026 players.
  It read as a genuine draft slot, and because the placeholder is jittered in
  the third decimal it also broke the ADP sort: rows all displaying "170.0"
  ordered by invisible digits, putting deep camp bodies above real starters.
  Those players now show ADP as N/A and sort to the bottom by rank.
- **Fantasy cheatsheet: free agents are reachable.** The team filter gained a
  *Free Agents* entry — 212 players, including Tyreek Hill and Keenan Allen,
  previously findable only by accident.
- **Fantasy cheatsheet: filter controls are debounced** and the dialog is
  released when closed, so repeatedly opening the board no longer grows memory.

## [0.9.2] - 2026-08-09

### Added
- **Fantasy cheatsheet: rookie filters.** The position filter gains *Rookies*
  plus *Rookie QB / RB / WR / TE*. Rookies are identified from the fantasy feed
  itself — a player with no stat line from any earlier season — which also
  catches undrafted rookies that a draft-list lookup would miss.
- **Fantasy cheatsheet: export to CSV.** *Export to CSV* saves the whole board,
  not just what the filters currently show: both rank boards, player, position,
  team, rookie flag, injury, ADP, auction value, projected points in all three
  scoring formats, and whether you have marked the player drafted.

## [0.9.1] - 2026-08-09

### Added
- **Fantasy football cheatsheet**: a draft board on the NFL screen with every
  draftable player plus all 32 team defenses — ESPN consensus rank, average draft
  position, auction value and projected season points. Search by player or team,
  filter by position (including FLEX) or team, sort by any column, and switch
  between Standard, Half-PPR and PPR scoring without a refetch. Space marks a
  player drafted, *Hide drafted players* clears them off the board, and both the
  drafted set and the scoring format persist between sessions. Kickers and team
  defenses show no projection: ESPN's published numbers for those two positions
  are unusable, so the board shows N/A rather than a wrong number.

### Fixed
- **NFL preseason games and weeks now appear.** The NFL screen only ever showed
  regular-season weeks, so during August it opened on the September opener
  labelled "Week: 1" and there was no way to reach the preseason at all. Weeks
  are now resolved from ESPN's season calendar and carry their season type, the
  Previous/Next Week buttons roll over between preseason, regular season and
  postseason, and weeks are named as ESPN names them — "Hall of Fame Weekend",
  "Preseason Week 1", "Wild Card" — instead of a bare, ambiguous week number.
- **Football weeks no longer include the next week's games.** ESPN marks the end
  of a week at 23:59 Pacific, which reads as the following day in UTC; the extra
  day pulled the next week's Thursday games into the current week. Affected the
  regular season too, and was most visible in the preseason.

## [0.9.0] - 2026-08-05

### Added
- **Windows installer**: `Scores-<version>-Setup.exe`, a per-user install into
  `%LocalAppData%\Programs\Scores` that needs no administrator rights and adds a
  Start Menu shortcut (desktop shortcut optional). Built with Inno Setup from
  `installer/scores.iss`.
- **Automatic updates**: Scores checks GitHub for a newer release at startup and
  can download and install it for you; *Check for Updates* on the home page runs
  the same check on demand. The startup check can be turned off in Settings.
  Portable copies update too — the installer relocates them.
- **Code signing**: releases are Authenticode-signed with Azure Artifact Signing
  via GitHub OIDC, so downloads no longer trip SmartScreen.
- `build.py` builds both distributables (one-dir installer input plus the portable
  one-file exe) and is what CI runs.
- `docs/INSTALLER.md` documents the installer, the updater and the signing setup.

### Changed
- The application version now lives in `version.py`, and the release workflow
  refuses to build a `v*` tag that disagrees with it or with the VERSION file.

## [0.65.0] - 2025-12-14

### Added
- **NCAA Hockey Support**: Complete Men's and Women's Hockey coverage
  - NCAA Men's Hockey (NCAAH): 50 teams across 10+ conferences
  - NCAA Women's Hockey (NCAAWH): 44 teams with conference standings
  - Live games, scores, and play-by-play details
  - Full team listings with schedule navigation
  - Conference-based standings (Hockey East, Big Ten, ECAC, NCHC, CCHA, CHA, Atlantic Hockey America, etc.)
  - Hockey-specific record format handling (W-L-T)

- **Polls & Rankings Feature**: Official poll tracking for all NCAA sports
  - NCAA Football: CFP Rankings, CFP Seedings, AP Poll, Coaches Poll (4 polls)
  - NCAA Men's Basketball: AP Poll, Coaches Poll (2 polls)
  - NCAA Women's Basketball: AP Poll, Coaches Poll (2 polls)
  - NCAA Men's Hockey: USA Hockey Poll, USCHO Poll (2 polls)
  - NCAA Women's Hockey: USA Hockey Poll, USCHO Poll (2 polls)
  - Multi-tab interface for sports with multiple polls
  - Rank change indicators (↑/↓) showing movement from previous week
  - Displays rank, team, record, points, and previous rank
  - Accessible table format with keyboard navigation (Ctrl+Tab between polls)

### Changed
- **Enhanced League Name Display**: All league abbreviations now display with full, descriptive names
  - Main league selection screen shows complete sport names with gender designation
  - Live scores section headers use formatted league names
  - Window titles display full sport names in breadcrumb navigation
  - Applied to: NCAA Women's Hockey, NCAA Men's Hockey, NCAA Women's Basketball, NCAA Men's Basketball, NCAA Football

### Technical
- Added `get_rankings()` API endpoint integration for poll data
- Created `PollsDialog` component with multi-tab support
- Implemented hockey conference structure parsing
- Added `format_league_name()` utility function for consistent name formatting
- Internal API calls maintain efficient abbreviation codes for performance

## [0.55.0] - 2025-08-31

### 🚀 BREAKTHROUGH ACCESSIBILITY FEATURES
- **Dynamic Window Titles for Screen Readers**: **FIRST-IN-CLASS** window title management system
  - **Contextual Titles**: Window titles dynamically reflect user location in the application
  - **Screen Reader Optimized**: "MLB - Sports Scores", "MLB, Standings - Sports Scores", "Yankees vs Red Sox - MLB - Sports Scores"
  - **Hierarchical Navigation**: Most specific information first, following accessibility best practices
  - **Universal Coverage**: All views, dialogs, and navigation contexts included
  - **Cross-Platform**: Both desktop (PyQt6) and web (JavaScript) implementations
  - **Zero Breaking Changes**: Enhances existing functionality without disruption

- **Multiple View Modes for All Tables**: **INDUSTRY-FIRST** accessible data presentation system
  - **Three View Modes**: Table, Quick List, Full List for every tabular data display
  - **Universal Keyboard Shortcuts**: Alt+V (cycle), Alt+T (table), Alt+Q (quick), Alt+F (full)
  - **Seamless Focus Management**: Maintains position when switching between view modes
  - **Real-time Data Sync**: All views reflect live data updates immediately
  - **Universal Integration**: Automatically available for standings, statistics, leaders, box scores, injuries
  - **Screen Reader Optimized**: Proper ARIA attributes and view change announcements
  - **Zero Breaking Changes**: All existing functionality preserved and enhanced

### Added
- **Comprehensive Conference/Division Support**: Restored and expanded sports organization
  - College Football (NCAAF): Full conference tabs (SEC, Big Ten, Big 12, ACC, Pac-12, etc.)
  - College Basketball (NCAAB/NCAAM/NCAAW): Major conference support with priority ordering
  - WNBA: Eastern/Western conference organization
  - All sports now properly display natural divisions/conferences as tabs

- **Enhanced Accessibility Infrastructure**: Foundation improvements for screen reader support
  - Removed problematic view selector combo box that caused focus conflicts
  - Default expanded view for comprehensive data presentation
  - Improved Ctrl+Tab navigation between division tabs
  - Consistent keyboard navigation patterns across all table types

### Enhanced
- **Expanded Standings Feature**: Toggle between basic and expanded standings views
  - Basic View: Traditional 7-column standings (Position, Team, W, L, PCT, GB, Streak)
  - Expanded View: Sport-specific additional columns with advanced statistics
  - MLB Expanded: Runs For/Against, Run Differential, Home/Road Records, Playoff %, Magic Numbers
  - NFL Expanded: Points For/Against, Point Differential, Division Record, Playoff Seed
  - NBA Expanded: PPG, Opponent PPG, Point Differential, Division Win %, Playoff Seed
  - NHL Expanded: Points, OT Losses, Goals For/Against, Goal Differential, Playoff Seed
  - Toggle buttons in standings dialog for supported sports (MLB, NFL, NBA, NHL)

- **News Articles**: Increased news article retrieval from 6 to 20 articles per league
  - Added configurable limit parameter (max 50 articles available from ESPN)
  - Better news coverage with more comprehensive headlines
  - Maintains same user interface with enhanced content

### Fixed  
- **MLB Standings**: Fixed incorrect "American League" tab appearing alongside proper divisions
  - Corrected Chicago White Sox abbreviation mapping (CHW vs CWS)
- **Text Processing**: Enhanced ESPN news text name replacement and pattern detection
  - Now displays exactly 6 division tabs as expected

## [0.54.0-preview] - 2025-08-27

### Added
- **Venue Browsing Feature**: Complete stadium/venue exploration system
  - Browse stadiums and venues by league (NFL, MLB, NBA, NHL, NCAA Football)
  - Comprehensive venue details including capacity, surface type, location, and facts
  - Home team information for each venue
  - NCAAF venue support through proper college-football API mapping
- **Enhanced Team Navigation Infrastructure**: Robust system for navigating between games and team schedules
  - Smart team ID resolution with multiple fallback mechanisms
  - College football team mapping for major programs ensuring reliable navigation
  - Improved back navigation with context preservation
- **Automatic Timezone Conversion**: All game times converted to user's local timezone
  - ESPN timezone data processing and local time conversion
  - Cross-platform timezone handling with verification tools
- **UI Consistency Improvements**: Unified interface design across all dialogs
  - Venue details use consistent QListWidget format matching rest of application
  - Text-based indicators ([Indoor, Grass]) replacing emoji decorations
  - Clean "--- Section ---" headers for organized information display

### Changed
- **Venue Service Architecture**: New venue service with efficient API usage and smart caching
- **Code Organization**: Test and demo files properly organized in TheBench directory
- **Interface Design**: Standardized on list-based UI elements for consistency and accessibility

### Fixed
- **NCAAF Venue Access**: Added proper "ncaaf" to "college-football" league mapping
- **Case Sensitivity**: Fixed venue dialog league case sensitivity for reliable data access
- **Team Navigation**: Enhanced team ID resolution prevents navigation failures in college football

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
