# Sports Scores GUI App (PyQt6)

## Overview
This application provides a desktop GUI for browsing live sports scores using the ESPN API. Built with PyQt6, it features accessible navigation and configurable game details.

## App Design

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
