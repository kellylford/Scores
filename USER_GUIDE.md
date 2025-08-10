# Sports Scores Application - User Guide

**Version:** 2.0 (Current Development)  
**Last Updated:** August 10, 2025  
**Platform:** Windows Desktop (PyQt6)

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [General Navigation](#general-navigation)
3. [Keyboard Shortcuts & Hotkeys](#keyboard-shortcuts--hotkeys)
4. [Main Features](#main-features)
5. [Baseball (MLB) Features](#baseball-mlb-features)
6. [Football (NFL) Features](#football-nfl-features)
7. [Export Game Log Feature](#export-game-log-feature)
8. [Accessibility Features](#accessibility-features)
9. [What Works Well](#what-works-well-)
10. [Known Areas for Improvement](#known-areas-for-improvement-)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Launch
1. **Run the application:** Double-click `scores.py` or run `python scores.py` from command line
2. **Home Screen:** You'll see a list of available sports leagues (NFL, MLB, NBA, NHL, etc.)
3. **Select a League:** Use arrow keys to navigate, press Enter to select

### Basic Flow
```
Home (Leagues) → League (Games List) → Game Details → Specific Views (Plays/Drives)
```

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
- **Story Links:** Double-click headlines to open full articles in browser
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

### Drive-by-Drive Navigation
1. **Access:** From game details, look for "Drives" section
2. **Structure:** Organized by quarters, then drives
3. **Content:** Each drive shows:
   - Starting field position
   - Drive summary (time, plays, yards)
   - Drive outcome (touchdown, field goal, punt, etc.)
   - Individual play details

### Play Details in Drives
- **Play Type:** Rush, pass, penalty, etc.
- **Yardage:** Gain/loss on each play
- **Down and Distance:** 1st & 10, 3rd & 7, etc.
- **Field Position:** Yard line locations

### Example Navigation Flow
```
NFL League → Game → Drives → 1st Quarter → Drive 1 → Individual Plays
```

### Football-Specific Information
- **Team Statistics:** Total yards, time of possession
- **Scoring Summary:** All touchdowns, field goals, safeties
- **Key Players:** Leading rushers, passers, receivers

---

## Export Game Log Feature

### ⭐ **NEW Feature:** Professional HTML Export
Export complete game logs to beautifully formatted HTML files for sharing or archival.

### How to Export
1. **Navigate to Game Details:** Select any completed game
2. **Access Plays/Drives:** Go to the detailed plays (baseball) or drives (football) view
3. **Click Export Button:** Look for "Export Game Log" button
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
- **JAWS Compatible:** Tested with JAWS screen reader
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

### 🚧 **Development Priorities**

#### Table Accessibility (High Priority)
- **Limited Table Navigation:** Tables don't activate JAWS virtual cursor mode
- **Missing Table Commands:** Can't use Ctrl+Alt+Arrow for table navigation
- **Workaround:** Currently using enhanced QTableWidget with improved accessibility
- **Goal:** Full HTML table functionality for screen readers

#### Data Completeness (Medium Priority)
- **Inconsistent Play Details:** Some games have limited play-by-play data
- **API Limitations:** Dependent on ESPN's data availability
- **Missing Information:** Some fields occasionally empty
- **Timing:** Data completeness varies by league and game status

#### User Interface Enhancements (Medium Priority)
- **Search Functionality:** No search for specific teams or players
- **Favorites:** Can't bookmark favorite teams
- **Customization:** Limited theme or display options
- **Sorting:** Tables don't support custom sorting

#### Technical Improvements (Low Priority)
- **Caching:** No offline data storage for previously viewed games
- **Performance:** Large datasets can be slow to load
- **Error Recovery:** Limited graceful handling of API failures
- **Configuration:** Settings could be more granular

### 🎯 **Specific Improvement Areas**

#### Export Enhancements
- **More Sports:** Expand export to basketball, hockey
- **Format Options:** PDF, CSV, or text export options
- **Batch Export:** Export multiple games at once
- **Scheduling:** Automatic export of favorite team games

#### Accessibility Refinements
- **Table Navigation:** Working toward full virtual cursor support
- **Voice Commands:** Potential voice navigation integration
- **Screen Reader Optimization:** Enhanced announcements and descriptions
- **Custom Shortcuts:** User-configurable keyboard shortcuts

#### Data Presentation
- **Advanced Statistics:** More detailed player and team analytics
- **Historical Data:** Access to past seasons and records
- **Comparative Views:** Side-by-side team or player comparisons
- **Trend Analysis:** Statistical trends over time

---

## Troubleshooting

### Common Issues & Solutions

#### Application Won't Start
```
Problem: "ModuleNotFoundError" or similar
Solution: Ensure PyQt6 is installed: pip install PyQt6 requests
```

#### No Games Showing
```
Problem: Empty game lists
Solution: 
1. Check internet connection
2. Try different date (Alt+P/Alt+N)
3. Refresh the view
4. ESPN API may be temporarily unavailable
```

#### Export Not Working
```
Problem: Export button missing or fails
Solution:
1. Ensure you're in a game's plays/drives view
2. Check if game has detailed play data
3. Verify write permissions in save location
4. Try a different save location
```

#### Keyboard Navigation Issues
```
Problem: Tab/arrow keys not working
Solution:
1. Click in the main window area first
2. Check if focus is in a text field
3. Use Alt+B to return to main navigation
4. Try Escape to reset focus
```

#### Screen Reader Problems
```
Problem: Screen reader not announcing properly
Solution:
1. Ensure JAWS/NVDA is running before starting app
2. Tab through interface to establish focus
3. Use arrow keys in lists and tables
4. Check screen reader's application-specific settings
```

### Getting Help
- **Documentation:** Check project README.md for technical details
- **Issues:** Report problems via GitHub issues
- **Development Status:** See DEVELOPMENT_STATUS_CURRENT.md for latest updates

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

**Application Version:** 2.0 Development  
**User Guide Version:** 1.0  
**Last Updated:** August 10, 2025

*This guide reflects the current state of development. Features and functionality may change as development continues.*
