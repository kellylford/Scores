# Scores v0.51.0-preview Release Notes

## 🎉 Enhanced User Experience & Accessibility Update!

This release brings significant improvements to user experience, accessibility, and navigation capabilities while maintaining all the core sports analysis features from v0.5.0.

### 🚀 What's New in v0.51

#### ⚡ Command Line Interface
Launch directly to your preferred sports section:
```bash
# Quick access to any sport
Scores.exe --mlb              # Jump straight to MLB games
Scores.exe --nfl-standings    # Open NFL standings directly
Scores.exe --mlb-teams        # View MLB teams immediately

# Available for all major sports: MLB, NFL, NBA, NHL, NCAA Football
```

#### 📅 Season Selection
- **Historical Data Access**: Browse team schedules from previous seasons
- **Smart Season Detection**: Automatic handling of current vs historical seasons
- **Enhanced Date Display**: Year included for historical data clarity

#### ♿ Accessibility Enhancements
- **Screen Reader Support**: Improved compatibility with assistive technologies
- **Enhanced Focus Management**: Smart navigation that highlights today's games
- **Accessible Tables**: Better structured data presentation for screen readers
- **Proper ARIA Labels**: All UI components properly labeled for accessibility

#### 🎯 Smart Navigation
- **Today's Game Focus**: Automatically highlights and focuses on today's games
- **Next Game Detection**: Falls back to next upcoming game if no game today
- **Visual Highlighting**: Today's games shown with bold text and yellow background
- **Improved Performance**: Background loading for faster schedule access

### 🔧 Improvements & Fixes

#### Team Display
- **Correct Team Names**: Shows proper team nicknames instead of confusing abbreviations
- **Consistent Naming**: Unified team name display across all views

#### User Interface
- **Better Focus Flow**: Improved keyboard navigation throughout the application
- **Enhanced Visuals**: Better contrast and highlighting for important information
- **Responsive Loading**: Non-blocking UI updates for better user experience

### 📱 How to Use New Features

#### Command Line Navigation
1. **Download**: Get the new `Scores.exe` from the release
2. **Command Prompt**: Open Command Prompt or PowerShell
3. **Navigate**: Use any of the new CLI options for instant access

#### Season Selection
1. **Open Team Schedule**: Click on any team to view their schedule
2. **Select Season**: Use the season dropdown to browse historical data
3. **Smart Focus**: Notice how today's games are automatically highlighted

#### Accessibility Features
1. **Screen Readers**: All content now properly announced by screen readers
2. **Keyboard Navigation**: Tab through all elements with proper focus indicators
3. **High Contrast**: Better visibility for users with visual impairments

### 🎯 Who Benefits from This Release?

- **Power Users**: Command line options for rapid navigation
- **Accessibility Users**: Comprehensive screen reader and keyboard support  
- **Sports Historians**: Season selection for browsing past seasons
- **Casual Users**: Improved visual highlighting and smart focus

### 🔄 Upgrading from v0.5.0

This is a drop-in replacement for v0.5.0:
1. **Download**: New `Scores.exe` from v0.51.0-preview release
2. **Replace**: Replace your existing executable
3. **Run**: All existing functionality preserved, plus new enhancements

### 💡 Tips for New Features

#### Command Line Tips
- Use `Scores.exe --help` to see all available options
- Combine with shortcuts for even faster access
- Perfect for creating desktop shortcuts with specific startup modes

#### Schedule Navigation
- Look for yellow highlighting to quickly spot today's games
- Use season dropdown to compare current vs previous year performance
- Click on any game for detailed statistics and play-by-play

### 🏟️ Still Includes All Core Features

- **Live Game Scores** - Real-time updates for ongoing games
- **Detailed Analysis** - Complete box scores and play-by-play
- **Team Standings** - Current league standings and playoff positioning
- **Player Statistics** - Individual player performance tracking
- **News Integration** - Latest sports headlines and updates
- **Audio Features** - Unique audio feedback for baseball analysis

### 🔧 Technical Requirements

- **Operating System**: Windows 10/11 (x64)
- **Size**: ~40MB standalone executable
- **Dependencies**: None (completely self-contained)
- **Internet**: Required for live data from ESPN

### 🐛 Known Issues

- Audio features still require Windows sound system
- Internet connection required for ESPN API data
- First launch may take slightly longer due to enhanced initialization

### 📞 Support & Feedback

Found a bug or have a suggestion? Please report issues through the GitHub repository or contact the development team.

---

**This is a preview release** - please report any issues you encounter to help us improve the final release!
