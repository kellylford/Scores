# Sports Scores Application

A comprehensive sports scores application with enhanced accessibility features, detailed game analysis, and innovative pitch audio exploration for baseball.

## 🏟️ What is Scores?

Scores is a desktop application that provides real-time access to:
- **Live Game Scores** - Current and completed games for MLB, NFL and more
- **Detailed Game Analysis** - Box scores, play-by-play, team statistics
- **Team Standings** - Complete league standings and division rankings  
- **Player Statistics** - Individual player performance data
- **News & Updates** - Latest sports news and headlines
- **Audio Features** - Unique audio feedback for baseball pitch analysis

### 🎯 Who Should Use Scores?

- **Sports Fans**: Stay updated with your favorite MLB and NFL teams with real-time scores and detailed analysis
- **Baseball Enthusiasts**: Experience unique audio pitch mapping and spatial strike zone exploration
- **Accessibility-Focused Users**: Enjoy comprehensive screen reader support and keyboard navigation
- **Developers**: Contribute to an open-source sports analysis platform with modern Python architecture

## Key Features

### Enhanced MLB Statistics 🎯
**NEW**: Revolutionary MLB statistics powered by the official MLB Stats API:
- **Full Season Data**: Real season totals, not limited recent performance
- **39 Statistical Categories**: Hitting (16), Pitching (15), Fielding (8) 
- **50 Players Per Category**: Comprehensive leaderboards for all statistics
- **6x Faster Performance**: 157ms response time vs 953ms from ESPN
- **Official MLB Source**: Direct from statsapi.mlb.com for authoritative data

### Multi-Sport Coverage
- **Live scores and updates** for NFL, MLB, NBA, NHL, and more
- **Detailed play-by-play analysis** with contextual information
- **Real-time game status** and statistical tracking
- **News integration** with latest headlines and stories

### Baseball Pitch Audio System
Experience baseball like never before with spatial audio mapping that converts pitch locations into sound:

- **Spatial Audio Mapping**: Each pitch location is mapped to unique audio frequencies
- **Strike Zone Exploration**: Audio feedback helps understand pitch placement relative to the strike zone
- **Stereo Positioning**: Left/right audio channels represent inside/outside pitch locations
- **Interactive Controls**: 
    - **Shift+F10** for keyboard context menu access, also supports right click
  - Pitch exploration dialog with detailed coordinate information
- **Educational Tool**: Learn to "hear" the strike zone and understand pitch patterns

### Enhanced NFL Drive Analysis
- **Detailed play information** with actual yards gained/lost
- **Situational context** including red zone and goal line situations  
- **Play type identification** for passes, rushes, and special teams
- **Drive momentum tracking** to follow game flow

## Quick Start

### For End Users (Recommended)
The easiest way to get started is with the standalone executable:

1. **Download**: Get `Scores.exe` from the [latest release](https://github.com/kellylford/Scores/releases) (no installation needed!)
2. **Run**: Double-click or press Enter on the executable to launch
3. **Explore**: Choose your sport (MLB/NFL) and start browsing games
4. **Navigate**: Use mouse or keyboard to explore scores, standings, and statistics

**System Requirements:**
- Windows 10/11 (64-bit)
- Internet connection (required for live sports data)
- 100MB RAM minimum, 50MB storage space

### For Developers
If you want to run from source or contribute to development:

```bash
# Clone the repository
git clone https://github.com/kellylford/Scores.git
cd Scores

# Use the automated build setup (recommended)
build-enhanced.bat

# OR manual setup:
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python scores.py
```

## Application Structure

### Core Application Files
- `scores.py` - Main application entry point and UI
- `espn_api.py` - **Enhanced with MLB Stats API integration** for comprehensive baseball statistics
- `accessible_table.py` - Accessible table widgets for screen readers
- `exceptions.py` - Custom error handling
- `main.py` - Alternative entry point

### MLB API Integration
- **Official MLB Stats API**: Direct integration with statsapi.mlb.com
- **39 Statistical Categories**: Complete hitting, pitching, and fielding statistics
- **Parallel Processing**: Concurrent API requests for optimal performance
- **Data Format Conversion**: Seamless UI integration with enhanced statistics

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

### Basic Navigation
- **League Selection**: Choose between MLB and NFL on the home screen
- **Date Navigation**: Use Previous/Next Day buttons or press **Ctrl+G** to jump to any date
- **Game Details**: Click on any game to see detailed statistics and play-by-play
- **Refresh Data**: Press **F5** to update scores and statistics

### Screen Flow
1. **Home Screen**: Select from available leagues (NFL, NBA, MLB, etc.)
2. **League Screen**: View games with scores, times, and news
3. **Game Details**: Comprehensive play-by-play with enhanced features
4. **News Dialog**: League headlines and stories

### Keyboard Controls
- **Enter**: Select items (games, news, menu options)
- **Escape** or **Alt+B**: Navigate back to previous screen
- **Shift+F10**: Open context menu for audio features (baseball)
- **Ctrl+G**: Jump to specific date
- **F5**: Refresh current data
- **Double-click**: Open news stories in browser

### Baseball Audio Features
When viewing MLB games with play-by-play data:
- **Right-click** on any pitch in the plays list to hear its location
- **Shift+F10** opens audio context menu for keyboard users
- **Alt+P**: Audio feedback for individual pitch locations
- **Alt+S**: Audio feedback for pitch sequences
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

### For End Users
- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: 100MB RAM minimum
- **Storage**: 50MB available space
- **Network**: Internet connection required for live sports data
- **Audio**: Windows sound system (optional, for audio features)

### For Developers
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

## Frequently Asked Questions

**Q: Is this free?**  
A: Yes! Scores is completely free to use and open source.

**Q: Do I need to install Python?**  
A: No! The standalone executable includes everything needed to run. Developers can also run from source.

**Q: Can I use this without internet?**  
A: No, live sports data requires an internet connection.

**Q: Why is the executable file so large (40MB)?**  
A: The executable includes the entire GUI framework and Python runtime for portability.

**Q: Does this work on Mac or Linux?**  
A: Currently Windows only, but cross-platform versions are planned for future releases.

**Q: How do I report bugs or request features?**  
A: Visit the [GitHub Issues page](https://github.com/kellylford/Scores/issues) to report bugs or request features.

## Support & Contributing

- **Issues**: Report bugs through the [GitHub repository](https://github.com/kellylford/Scores/issues)
- **Feature Requests**: Let us know what sports data you'd like to see
- **Accessibility**: Help us improve accessibility features
- **Contributing**: This project focuses on accessibility and comprehensive sports data presentation

Contributions that enhance accessibility features or expand sports coverage are welcome.

## License
See `LICENSE` file for license information.
