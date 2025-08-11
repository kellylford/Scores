# Sports Scores Application - User Guide

**Version:** 1.0.0  
**Last Updated:** August 10, 2025  
**Platform:** Windows Desktop (PyQt6)

## Enhanced NFL Drive Display

The NFL drive display now provides detailed contextual information for each play, including yardage gained or lost, play types, and field position awareness:

```
[RED ZONE 3rd & 2 from OPP 18] PASS: (+15 yards) TOUCHDOWN! (14-7)
[GOAL LINE 4th & 1 from OPP 3] RUSH: (+1 yard) Conversion for first down!
```

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Enhanced NFL Features](#enhanced-nfl-features)
3. [General Navigation](#general-navigation)
4. [Keyboard Shortcuts & Hotkeys](#keyboard-shortcuts--hotkeys)
5. [Main Features](#main-features)
6. [Baseball (MLB) Features](#baseball-mlb-features)
7. [Football (NFL) Features](#football-nfl-features)
8. [Export Game Log Feature](#export-game-log-feature)
9. [Accessibility Features](#accessibility-features)
10. [What Works Well](#what-works-well-)
11. [Known Areas for Improvement](#known-areas-for-improvement-)
12. [Tips for Best Experience](#tips-for-best-experience)

---

## Getting Started

### First Launch
1. **Run the application:** Launch `SportsScores.exe` from your downloads folder
2. **Home Screen:** You'll see a list of available sports leagues (NFL, MLB, NBA, NHL, etc.)
3. **Select a League:** Use arrow keys to navigate, press Enter to select

### Basic Flow
```
Home (Leagues) → League (Games List) → Game Details → Specific Views (Plays/Drives)
```

---

## Enhanced NFL Features

### Detailed Drive Display
The NFL experience includes comprehensive drive information that provides context for each play's impact on the game.

#### Play Information Elements

**Yardage Analysis:**
```
PASS: (+8 yards) - Yards gained on the play
RUSH: (-2 yards) - Yards lost  
SACK: (-7 yards) - Quarterback sack
```

**Play Type Identification:**
```
PASS: - Passing plays (complete, incomplete, interception)
RUSH: - Running plays
SACK: - Quarterback sacks
PUNT: - Punting situations
FIELD GOAL: - Kicking plays
KICKOFF: - Special teams kickoffs
```

**Field Position Context:**
```
RED ZONE - Within 20 yards of goal line
GOAL LINE - Within 5 yards of scoring
4TH DOWN - Fourth down situations
```

#### Example Drive Display
```
DRIVE 3 - Chicago Bears (7 plays, 68 yards, 3:42)
[1st & 10 from CHI 32] PASS: (+12 yards) Williams complete to Moore
[1st & 10 from CHI 44] RUSH: (+3 yards) Swift up the middle  
[2nd & 7 from CHI 47] PASS: (+8 yards) Williams to Allen
[RED ZONE 1st & 10 from OPP 15] PASS: (+9 yards) Completion to tight end
[GOAL LINE 2nd & 1 from OPP 6] RUSH: (+2 yards) Swift powers forward
[GOAL LINE 3rd & Goal from OPP 4] PASS: (+4 yards) TOUCHDOWN! (14-7)
```

#### Key Improvements
- **Play Context:** Field position and down/distance clearly indicated
- **Statistical Information:** Actual yardage gained or lost on each play
- **Play Type Clarity:** Immediate identification of play types
- **Special Teams Separation:** Kickoffs and punts properly distinguished from offensive drives
- **Critical Situations:** Field position alerts for scoring opportunities

### Using Enhanced NFL Display
1. Start the application
2. Select NFL from league list
3. Choose any active or completed game
4. Navigate to the "Drives" section
5. Review drive-by-drive breakdown with detailed play information

---

## General Navigation

### Screen Structure
The application uses a **stacked navigation system** where you can move between different views:

1. **Home Screen (League Selection)**
   - Lists all available sports leagues
   - Shows league abbreviations (NFL, MLB, NBA, etc.)

2. **League Screen (Games List)**
   - Shows today's games for the selected league
   - Displays scores, game status, and start times
   - Includes news section at bottom: "--- News (X stories) ---"

3. **Game Details Screen**
   - Comprehensive game information
   - Team records, venue, weather, broadcast info
   - Configurable additional details (standings, leaders, injuries, etc.)

4. **Specialized Views**
   - **Baseball:** Play-by-play details with pitching information
   - **Football:** Drive-by-drive breakdown with play details

### Navigation Principles
- **Linear Navigation:** Use Tab/Shift+Tab to move between controls
- **List Navigation:** Use arrow keys in lists, Enter to select
- **Back Navigation:** Multiple ways to go back (see shortcuts below)
- **Date Navigation:** Browse games from different dates

---

## Keyboard Shortcuts & Hotkeys

### Global Shortcuts (Work Everywhere)
| Shortcut | Action | Description |
|----------|---------|-------------|
| **Escape** | Go Back | Returns to previous screen |
| **Alt+B** | Go Back | Same as Escape, returns to previous screen |
| **Enter** | Select/Open | Activates selected item |
| **Tab** | Next Control | Move to next interactive element |
| **Shift+Tab** | Previous Control | Move to previous interactive element |
| **Arrow Keys** | Navigate Lists | Move up/down in lists and tables |

### Date Navigation (League Screen)
| Shortcut | Action | Description |
|----------|---------|-------------|
| **Alt+P** | Previous Day | Go to previous day's games |
| **Alt+N** | Next Day | Go to next day's games |
| **Ctrl+G** | Go to Date | Open date picker dialog |

### In Date Picker Dialog
- **Type in Month field:** Can type month name or use dropdown
- **Type in Day field:** Can type day number directly
- **Type in Year field:** Can type year directly
- **Enter:** Confirm date selection
- **Escape:** Cancel date picker

### Table Navigation
| Shortcut | Action | Description |
|----------|---------|-------------|
| **Arrow Keys** | Navigate Cells | Move between table cells |
| **Home** | First Column | Jump to first column of current row |
| **End** | Last Column | Jump to last column of current row |
| **Page Up/Down** | Scroll Table | Scroll through large tables |

---

## Main Features

### 1. Live Scores & Game Status
- **Real-time updates:** Scores update when you refresh
- **Game status:** Pre-game, In Progress, Final, Postponed, etc.
- **Detailed timing:** Inning/quarter, time remaining, etc.

### 2. News Integration
- **League News:** Access news stories from the league screen
- **Story Links:** Press Enter on headlines to open full articles in browser
- **Author Information:** Shows bylines when available

### 3. Game Details
- **Team Information:** Records, rankings, home/away status
- **Venue Details:** Stadium name, city, state
- **Weather:** Temperature and conditions (when available)
- **Broadcast Info:** TV networks and radio stations

### 4. Configurable Information
Access additional details via the **Config** button:
- ✅ **Standings:** Current team standings and records
- ✅ **Leaders:** Top player statistics
- ✅ **Injuries:** Detailed injury reports
- ✅ **News:** Recent headlines related to teams
- ✅ **Broadcasts:** Complete network information
- ✅ **Boxscore:** Game statistics (when available)

---

## Baseball (MLB) Features

### Play-by-Play Navigation
1. **Access:** From game details, look for "Plays" section
2. **Structure:** Organized by innings
3. **Content:** Each play shows:
   - Batter information
   - Pitch count and details
   - Play outcome
   - Runners and scoring

### Enhanced Pitch Details
- **Pitch Type:** Fastball, Slider, Curveball, etc.
- **Velocity:** MPH for each pitch
- **Location:** Strike zone details
- **Count:** Balls and strikes progression

### Example Navigation Flow
```
MLB League → Game → Plays → Inning 1 → Individual Plays → Pitch Details
```

### Baseball-Specific Information
- **Batting Statistics:** Real-time AVG, RBI, HR stats
- **Pitching Statistics:** ERA, strikeouts, pitch counts
- **Defensive Plays:** Double plays, errors, assists

---

## Football (NFL) Features

### Enhanced Drive Display
The NFL section provides comprehensive drive information with detailed play context.

#### Drive Organization
1. **Access:** From game details, navigate to "Drives" section
2. **Structure:** Organized by quarters, then individual drives
3. **Content:** Each drive includes:
   - Starting and ending field position
   - Drive summary (time, plays, yards)  
   - Drive outcome (touchdown, field goal, punt, etc.)
   - Individual play details with enhanced information

#### Detailed Play Information
Each play now includes multiple data points:

**Yardage Analysis:**
- `(+8 yards)` - Yards gained on successful plays
- `(-3 yards)` - Yards lost on unsuccessful plays
- `(+0 yards)` - No gain situations

**Play Type Classification:**
- `PASS:` - All passing plays (complete, incomplete, interception)
- `RUSH:` - Running plays
- `SACK:` - Quarterback sacks with yardage lost
- `PUNT:` - Punting situations
- `FIELD GOAL:` - Kicking attempts with distance
- `KICKOFF:` - Special teams plays (properly separated from drives)

**Situational Context:**
- `RED ZONE` - Scoring opportunities within 20 yards
- `GOAL LINE` - Immediate scoring threats within 5 yards  
- `4TH DOWN` - Critical conversion attempts

#### Example Enhanced Drive
```
DRIVE 2 - Buffalo Bills (9 plays, 64 yards, 1:35)
[1st & 10 from BUF 35] PASS: (+8 yards) Allen complete to Diggs
[2nd & 2 from BUF 43] RUSH: (+15 yards) Cook breaks tackle
[RED ZONE 1st & 10 from OPP 18] PASS: (+9 yards) Allen to Davis
[RED ZONE 2nd & 1 from OPP 9] RUSH: (+3 yards) Cook powers forward  
[GOAL LINE 3rd & Goal from OPP 6] PASS: (+6 yards) TOUCHDOWN! (14-7)
```

#### Information Benefits
- **Game Flow Understanding:** See drive momentum and efficiency
- **Strategic Context:** Field position awareness for critical moments
- **Play Impact:** Statistical significance of each play
- **Special Teams Clarity:** Proper separation of kickoffs and punts from offensive drives

### Traditional NFL Information
- **Team Statistics:** Total yards, time of possession
- **Scoring Summary:** All touchdowns, field goals, safeties  
- **Key Players:** Leading rushers, passers, receivers
- **Game Situation:** Clock, quarter, weather conditions

---

## Export Game Log Feature

### ⭐ **NEW Feature:** Professional HTML Export
Export complete game logs to beautifully formatted HTML files for sharing or archival.

### How to Export
1. **Navigate to Game Details:** Select any completed game
2. **Access Plays/Drives:** Go to the detailed plays (baseball) or drives (football) view
3. **Select Export Button:** Navigate to "Export Game Log" button and press Enter
4. **Choose Location:** Save the HTML file to your desired location

### What Gets Exported

#### Baseball Games
- **Game Header:** Teams, final score, date, venue
- **Complete Play-by-Play:** Every inning, every play
- **Pitch Details:** Enhanced pitching information where available
- **Professional Formatting:** Clean, readable HTML structure

#### Football Games  
- **Game Header:** Teams, final score, date, venue
- **Drive-by-Drive Breakdown:** Organized by quarters
- **Play Details:** Individual plays within each drive
- **Drive Summaries:** Time, plays, yards for each drive

### Export File Format
- **File Type:** HTML (.html)
- **Naming:** `game_log_TeamA_vs_TeamB_YYYYMMDD.html`
- **Structure:** Semantic HTML with proper headings and accessibility
- **Styling:** Professional CSS for clean presentation
- **Compatibility:** Opens in any web browser

### Example Export Files
The app generates files like:
- `game_log_Mets_vs_Brewers_20250810.html` (Baseball)
- `game_log_Jets_vs_Packers_20250810.html` (Football)

---

## Accessibility Features

### Screen Reader Support
- **Screen Reader Compatible:** Tested with multiple screen readers including JAWS and NVDA
- **Proper Focus Management:** Tab order follows logical sequence
- **Descriptive Labels:** All controls have meaningful names
- **Status Announcements:** Important changes are announced

### Keyboard-Only Operation
- **No Mouse Required:** Every feature accessible via keyboard
- **Consistent Navigation:** Same shortcuts work across all screens
- **Clear Focus Indicators:** Easy to see where you are

### Table Accessibility
- **Enhanced Tables:** Improved table navigation for statistics
- **Header Association:** Column headers properly associated with data
- **Row/Column Context:** Screen readers announce position in tables

### Visual Accessibility
- **High Contrast:** Clear visual distinction between elements
- **Readable Fonts:** Standard system fonts for consistency
- **Logical Layout:** Information organized in logical reading order

---

## What Works Well ✅

### 🏆 **Excellent Areas**

#### Navigation & Usability
- **Keyboard Navigation:** Complete keyboard control with logical shortcuts
- **Back Navigation:** Multiple intuitive ways to go back (Escape, Alt+B)
- **Date Navigation:** Easy browsing of past/future game dates
- **Focus Management:** Proper focus restoration after dialogs

#### Live Data Integration
- **Real-time Scores:** Accurate, up-to-date game information
- **Comprehensive Coverage:** All major sports leagues supported
- **Game Status:** Detailed timing and status information
- **News Integration:** Direct access to ESPN news stories

#### Game Details & Information
- **Rich Information:** Team records, venue, weather, broadcasts
- **Configurable Display:** Choose what information to show per league
- **Clean Formatting:** Well-organized, readable information layout
- **Professional Presentation:** Stadium info, weather, broadcast details

#### Baseball Features
- **Detailed Play-by-Play:** Complete inning-by-inning coverage
- **Enhanced Pitch Information:** Velocity, type, count details
- **Statistical Integration:** Real-time batting and pitching stats
- **Export Functionality:** Professional HTML game logs

#### Football Features  
- **Drive Organization:** Clear quarter and drive structure
- **Play Details:** Down, distance, yardage information
- **Export Functionality:** Complete drive-by-drive HTML exports
- **Game Flow:** Easy to follow game progression

#### Export System
- **Universal Support:** Works for all sports with plays/drives data
- **Professional Output:** Clean, semantic HTML formatting
- **Accessibility:** Exported files maintain proper structure
- **Easy Sharing:** Generated files work in any browser

---

## Known Areas for Improvement 🔧

### 🚧 **Current Limitations**

#### Table Navigation
- **Limited Screen Reader Support:** Tables don't fully activate advanced screen reader table navigation features
- **Basic Navigation:** Currently uses standard arrow key navigation
- **Future Goal:** Working toward enhanced screen reader table functionality

#### Export Feature Scope
- **Limited Sports:** Currently works for MLB and NFL only
- **Future Expansion:** Planning support for basketball and hockey
- **Data Dependency:** Export quality depends on available ESPN data

#### Search and Organization
- **No Search:** Cannot search for specific teams or players
- **No Favorites:** Cannot bookmark favorite teams for quick access
- **Basic Sorting:** Tables use default sorting only

#### Data Completeness
- **API Dependent:** Some game data may be incomplete
- **Variable Quality:** Play-by-play detail varies by game and league
- **Live Data Only:** No offline storage for previously viewed games

---

## Tips for Best Experience

### For Screen Reader Users
1. **Start with Tab:** Always begin navigation with Tab to establish focus
2. **Use Arrow Keys:** In lists and tables, arrow keys provide better navigation
3. **Learn the Shortcuts:** Alt+B and Escape are your primary back buttons
4. **Export Feature:** Use the export feature to create accessible HTML versions

### For Keyboard Users
1. **Date Navigation:** Alt+P/Alt+N are faster than manual date selection
2. **Direct Selection:** Enter key always selects/opens the focused item
3. **Quick Configuration:** Learn which details you want and configure once per league
4. **Back Stack:** The app remembers where you came from - back always works

### For All Users
1. **Refresh Regularly:** Live scores update when you refresh
2. **Explore Configuration:** Each league can show different information
3. **Try Different Dates:** Historical games often have more complete data
4. **Use Export:** Save interesting games for later reference

---

**Need Help?** See the [Technical Guide](TECHNICAL_GUIDE.md) for troubleshooting and advanced information.

**Application Version:** 0.8.0 Beta  
**User Guide Version:** 2.0  
**Last Updated:** August 10, 2025

*This is a beta release. Features and functionality may change as development continues.*
