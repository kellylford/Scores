# Sports Scores Application

A comprehensive sports scores application with enhanced accessibility features, detailed game analysis, and innovative pitch audio exploration for baseball.

## Key Features

### Multi-Sport Coverage
- **Live scores and updates** for NFL, MLB, NBA, NHL, and more
- **Detailed play-by-play analysis** with contextual information
- **Real-time game status** and statistical tracking
- **News integration** with latest headlines and stories

### Accessibility & Navigation
- **Full keyboard navigation** with screen reader compatibility
- **Clear focus management** for visually impaired users
- **Accessible table widgets** with proper markup
- **Intuitive interface** designed for all users

### Baseball Pitch Audio System
Experience baseball like never before with spatial audio mapping that converts pitch locations into sound:

- **Spatial Audio Mapping**: Each pitch location is mapped to unique audio frequencies
- **Strike Zone Exploration**: Audio feedback helps understand pitch placement relative to the strike zone
- **Stereo Positioning**: Left/right audio channels represent inside/outside pitch locations
- **Interactive Controls**: 
  - Right-click on any pitch for audio playback
  - **Shift+F10** for keyboard context menu access
  - Pitch exploration dialog with detailed coordinate information
- **Educational Tool**: Learn to "hear" the strike zone and understand pitch patterns

### Enhanced NFL Drive Analysis
- **Detailed play information** with actual yards gained/lost
- **Situational context** including red zone and goal line situations  
- **Play type identification** for passes, rushes, and special teams
- **Drive momentum tracking** to follow game flow

## Quick Start

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

### Running the Application
```bash
python scores.py
```

## Application Structure

### Core Application Files
- `scores.py` - Main application entry point and UI
- `espn_api.py` - ESPN API integration and data fetching
- `accessible_table.py` - Accessible table widgets for screen readers
- `exceptions.py` - Custom error handling
- `main.py` - Alternative entry point

### Audio System Files
- `simple_audio_mapper.py` - Core pitch-to-audio mapping system
- `stereo_audio_mapper.py` - Stereo audio positioning for pitch locations
- `pitch_exploration_dialog.py` - Interactive pitch exploration interface

### Data Models & Services
- `models/game.py` - Game data model and structure
- `models/news.py` - News data model
- `models/standings.py` - Standings data model
- `services/api_service.py` - API service abstraction layer

### Development Archive
- `TheBench/` - Contains all development files, tests, documentation, and analysis tools

## Navigation & Usage

### Screen Flow
1. **Home Screen**: Select from available leagues (NFL, NBA, MLB, etc.)
2. **League Screen**: View games with scores, times, and news
3. **Game Details**: Comprehensive play-by-play with enhanced features
4. **News Dialog**: League headlines and stories

### Controls
- **Enter**: Select items (games, news, menu options)
- **Escape** or **Alt+B**: Navigate back to previous screen
- **Shift+F10**: Open context menu for audio features (baseball)
- **Double-click**: Open news stories in browser
- **Refresh**: Reload current data

### Baseball Audio Features
When viewing MLB games with play-by-play data:
- **Right-click** on any pitch in the plays list to hear its location
- **Shift+F10** opens audio context menu for keyboard users
- Select "Explore Pitch Locations" for detailed audio mapping
- Use stereo headphones for best spatial audio experience

### NFL Drive Analysis
Enhanced play-by-play display shows:
```
[1st & 10 from GB 25] PASS: (+8 yards) Love complete to Watson
[RED ZONE 3rd & 2 from GB 18] RUSH: (+1 yard) Jones up the middle  
[GOAL LINE 4th & 1 from GB 3] TOUCHDOWN: Pass complete for touchdown
```

## Technical Requirements
- **Python 3.9+**
- **PyQt6** - GUI framework
- **requests** - HTTP client for API calls
- **ESPN API** - Live sports data source
- **Audio system** (Windows: winsound, cross-platform: PyAudio optional)

## Development & Testing
All development files, test scripts, documentation, and analysis tools have been organized in the `TheBench/` directory to keep the main project clean and focused. This includes:

- Test scripts and unit tests
- API analysis and debugging tools  
- Development documentation and guides
- Data analysis tools and sample data
- Web application prototype
- Audio system development files

See `TheBench/README_TheBench.md` for a complete index of archived development materials.

## License
See `LICENSE` file for license information.

## Contributing
This project focuses on accessibility and comprehensive sports data presentation. Contributions that enhance accessibility features or expand sports coverage are welcome.
