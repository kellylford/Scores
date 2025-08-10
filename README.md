# Sports Scores Application - Refactor Branch

This is the clean refactor branch containing only the essential files needed for the working sports scores application.

## Purpose
This branch serves as the starting point for the architecture refactoring outlined in `ARCHITECTURE_REFACTORING_PLAN.md`. It contains only the minimal set of files required to run the application, providing a clean foundation for restructuring.

## What's Included
- Essential Python files for the working application
- Required data models and services  
- Core dependencies and configuration
- Architecture planning documents

## What's Removed
- All test files (`test_*.py`)
- Sample data and exploration files (`*.json`, `api_exploration/`)
- Web application files (`web_app/`)
- Utility and debugging scripts
- Most documentation (kept only essential files)
- Build artifacts and PyInstaller specs

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
   - Displays a list of available leagues (e.g., NFL, NBA).
   - Press Enter to select a league.

2. **League Screen (Scores List):**
   - Shows active games and scores for the selected league with start times.
   - Displays "--- News (X stories) ---" entry at the bottom for league news.
   - Press Enter to select a game or view news.
   - Back button (Alt+B) and Escape to return to Home.
   - Refresh button to reload scores.

3. **News Dialog:**
   - Lists current news headlines for the selected league.
   - Double-click any headline to open the full story in your web browser.
   - Shows author bylines when available.
   - "Open Selected Story" button for keyboard users.

4. **Game Details Screen:**
   - Presents detailed information for the selected game:
     - Team names, records, and home/away status
     - Game status and timing
     - Venue information (stadium, city, state)
     - Weather conditions and temperature
     - Injury reports summary
     - Broadcast networks
   - Additional configurable details with smart formatting:
     - **News**: Shows recent headlines
     - **Leaders**: Top player statistics
     - **Standings**: Current team standings
     - **Injuries**: Detailed injury reports
     - **Broadcasts**: Complete network information
     - **Odds**: Betting lines and information
     - **Boxscore**: Game statistics (when available)
   - Back button (Alt+B) and Escape to return to League.
   - Refresh button to reload details.
   - Config button to open configuration.

5. **Config Screen:**
   - List of checkboxes for selecting which details to show for games in the current league.
   - Back button (Alt+B) and Escape to return to Game Details.

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

## Setup

### Using Virtual Environment (Recommended)
```bash
# Navigate to the sports_scores_gui directory
cd sports_scores_gui

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Manual Installation
```bash
pip install pyqt6 requests
```

## Usage
```bash
python main.py
```
