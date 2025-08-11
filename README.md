# Sports Scores Application

A comprehensive sports scores application with enhanced accessibility features and detailed game analysis.

## Enhanced NFL Drive Display
The application now includes detailed NFL drive analysis with contextual play information:
- **Yardage information**: Displays actual yards gained or lost for each play
- **Play type identification**: Clear labeling of pass, rush, and special teams plays
- **Situational context**: Automatic highlighting of red zone, goal line, and critical down situations
- **Improved organization**: Special teams plays properly separated from offensive drives

This provides comprehensive context for following game flow and understanding play impact.

## Purpose
A fully accessible sports application providing real-time scores, detailed game information, and comprehensive play-by-play analysis for multiple sports leagues.

## Key Features
- **Multi-Sport Support**: NFL, MLB, NBA, and more
- **Enhanced NFL Drives**: Detailed play-by-play with statistical context
- **Complete Accessibility**: Screen reader compatible with full keyboard navigation
- **Live Updates**: Real-time scores and game status
- **Detailed Analysis**: Player stats, standings, injury reports
- **News Integration**: Latest headlines and stories

## Files in This Branch

### Core Application
- `scores.py` - Main application entry point and UI
- `espn_api.py` - ESPN API integration
- `exceptions.py` - Custom error handling
- `accessible_table.py` - Accessible table widgets
- `main.py` - Alternative entry point

### Data Layer
- `models/game.py` - Game data model
- `models/news.py` - News data model  
- `models/standings.py` - Standings data model
- `services/api_service.py` - API service abstraction

### Configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore patterns
- `LICENSE` - Software license

### Documentation
- `README.md` - This file
- `DISTRIBUTION.md` - Files needed for distribution
- `ARCHITECTURE_REFACTORING_PLAN.md` - Refactoring roadmap

## Running the Application
```bash
pip install -r requirements.txt
python scores.py
```

## Next Steps
Follow the `ARCHITECTURE_REFACTORING_PLAN.md` to implement the modular architecture while keeping this working version as a reference.

## Branches
- `main` - Complete working application with all files
- `refactor` - Clean starting point for architecture improvements

### Screens & Navigation

1. **Home Screen (Leagues List):**
   - Displays available leagues (NFL, NBA, MLB, etc.)
   - Press Enter to select a league

2. **League Screen (Scores List):**
   - Shows active games with scores and start times
   - Displays "--- News (X stories) ---" entry for league news
   - Press Enter to select a game or view news
   - Back (Alt+B) and Escape to return to Home
   - Refresh button to reload scores

3. **Game Details Screen:**
   - **🏈 ENHANCED NFL EXPERIENCE**: Revolutionary drive-by-drive display!
     - Each play shows yardage: `PASS: (+8 yards) Complete to receiver`
     - Situational highlights: `RED ZONE 3rd & 2`, `GOAL LINE 4th & 1`
     - Special teams separated: Kickoffs, punts, field goals distinct
     - Feel the game flow: See momentum shifts and critical moments!
   
   - **⚾ MLB Play-by-Play**: Detailed pitch information
     - Pitch velocity and type: `Ball 1 (95 mph Fastball)`
     - Strike/ball tracking with context
   
   - **Game Information**: Team records, venue, weather, injuries, broadcasts
   - **Additional Sections**: News, leaders, standings, boxscore, odds
   - Back (Alt+B) and Escape to return to League
   - Config button for customizable details

4. **Config Screen:**
   - Checkboxes for selecting game detail sections
   - Per-league configuration
   - Back (Alt+B) and Escape to return

5. **News Dialog:**
   - League headlines with author bylines
   - Double-click to open stories in browser
   - "Open Selected Story" button for keyboard users

### Controls
- **Enter:** Select item (games or news).
- **Double-click:** In news dialog, opens story in web browser.
- **Escape:** Go back one level.
- **Alt+B:** Back button.
- **Refresh:** Reload current view.
- **Config:** Open configuration for game details.

### API Integration
- Uses ESPN API endpoints for leagues, scores, and game details.
- Configurable details per league.

### Accessibility
- Keyboard navigation for all actions.
- Clear focus management.

## File Structure
- `main.py`: Main application code.
- `espn_api.py`: ESPN API integration.
- `README.md`: App design and documentation.
- `requirements.txt`: Python package dependencies.

## Requirements
- Python 3.9+
- PyQt6
- requests

## Quick Start Guide

### Installation
```bash
# Clone the repository
git clone https://github.com/kellylford/Scores.git
cd Scores

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application
```bash
python scores.py
```

## NFL Drive Display Features

### Enhanced Play Information
The NFL drive display provides comprehensive context for each play:

**Standard Display:**
```
[1st & 10 from GB 25] Love pass complete to Watson
```

**Enhanced Display:**
```
[1st & 10 from GB 25] PASS: (+8 yards) Love complete to Watson
[RED ZONE 3rd & 2 from GB 18] RUSH: (+1 yard) Jones up the middle  
[GOAL LINE 4th & 1 from GB 3] TOUCHDOWN: Pass complete for touchdown (7-14)
```

### Key Features:
- **Yardage Display**: Shows exact yards gained or lost on each play
- **Play Type Labels**: Clear identification of pass, rush, sack, punt, etc.
- **Situational Context**: Highlights red zone, goal line, and fourth down situations
- **Special Teams**: Kickoffs, punts, and field goals properly organized
- **Game Flow**: Complete context for understanding drive momentum

### Implementation Notes
- Text-based enhancements for full screen reader compatibility
- Keyboard navigation maintained throughout
- Information provided without relying on visual indicators

## Technical Documentation

### Core Files
- `scores.py` - Main application with enhanced NFL display
- `espn_api.py` - ESPN API integration  
- `accessible_table.py` - Accessible table widgets
- `models/` - Data models for games, standings, news
- `services/` - API service abstraction

### Dependencies
- Python 3.9+
- PyQt6 - GUI framework
- requests - HTTP client
- ESPN API - Live sports data

### Configuration
- Per-league detail configuration
- Customizable display options
- Accessibility preferences
