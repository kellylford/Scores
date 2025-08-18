# Sports Scores - VoiceOver and Accessibility Guide

## Overview
The Sports Scores application now includes comprehensive macOS accessibility support, including full VoiceOver compatibility and enhanced keyboard navigation.

## VoiceOver Support

### Getting Started
1. **Enable VoiceOver**: System Preferences > Accessibility > VoiceOver > Enable VoiceOver
2. **Launch the app**: Open Scores.app from Applications or Launchpad
3. **Initial focus**: The app will automatically set focus to the main interface

### VoiceOver Navigation

#### Basic Navigation
- **VO + Arrow Keys**: Navigate between elements
- **VO + Space**: Activate buttons and controls
- **VO + F5**: Start reading from current position
- **VO + A**: Start reading entire window

#### Table Navigation
- **Arrow Keys**: Move between table cells
- **VO + C**: Hear column header
- **VO + R**: Hear row information
- **VO + T**: Hear table summary

### Keyboard Navigation

#### Application-Wide
- **Tab**: Move between major interface elements
- **Shift + Tab**: Move backwards between elements
- **Enter**: Activate buttons and open items
- **Escape**: Close dialogs and return to previous view

#### Within Lists and Tables
- **Up/Down Arrows**: Navigate between items/rows
- **Left/Right Arrows**: Navigate between columns (in tables)
- **Home/End**: Jump to first/last item
- **Page Up/Page Down**: Scroll through large lists

## Accessible Features

### Screen Reader Announcements
- **Navigation**: Current location and available options announced
- **Data Updates**: New information automatically announced
- **Status Changes**: Loading states and errors clearly communicated
- **Table Content**: Row and column positions with content

### Keyboard Shortcuts
- **Command + R**: Refresh current data
- **Command + H**: Return to home screen
- **Command + L**: Go to Live Scores
- **Command + 1-9**: Quick navigation to different sports (if available)

### Focus Management
- **Logical Tab Order**: Navigate through interface in logical sequence
- **Focus Indicators**: Clear visual focus indicators for sighted users
- **Return Focus**: Focus returns to logical position after closing dialogs

## Interface Elements

### Main Screen
- **Sports List**: List of available sports leagues
  - Use arrow keys to navigate
  - Press Enter to open a league
  
### League Views
- **Game Tables**: Live scores and game information
  - Navigate with arrow keys
  - Column headers automatically announced
  - Game details available with Enter key

- **Standings Tables**: Team standings and statistics
  - Sortable columns (announced when changed)
  - Team information accessible via Enter

### Live Scores
- **Multi-Sport View**: All active games across sports
  - Organized by sport (announced as groups)
  - Time-based organization (current, upcoming, completed)

## Troubleshooting

### VoiceOver Issues

#### App Not Speaking
1. **Check VoiceOver**: Ensure VoiceOver is enabled in System Preferences
2. **Restart VoiceOver**: VO + F8 twice to restart VoiceOver
3. **Check Focus**: VO + F3 to hear current focus
4. **Restart App**: Close and reopen Scores app

#### Navigation Problems
1. **Reset Navigation**: VO + F3 + F3 to reset VoiceOver navigation
2. **Check Interaction**: VO + Shift + Down Arrow to start interacting with tables
3. **Stop Interaction**: VO + Shift + Up Arrow to stop interacting

#### Table Reading Issues
1. **Navigate to Table**: Use VO + Arrow keys to find table
2. **Start Interaction**: VO + Shift + Down Arrow
3. **Use Table Commands**: VO + C for columns, VO + R for rows
4. **Exit Table**: VO + Shift + Up Arrow when done

### Keyboard Navigation Issues

#### Focus Lost
1. **Reset Focus**: Click in app window or use Command + Tab to return focus
2. **Find Focus**: Press Tab repeatedly to locate current focus
3. **Use Mouse**: Click on desired element to set focus

#### Keys Not Working
1. **Check App Focus**: Ensure Scores app is the active application
2. **Check Interaction Mode**: Some elements require entering interaction mode
3. **Try Alternative**: Use VoiceOver commands as alternative

## Advanced Features

### Custom Announcements
- **Score Updates**: Automatic announcements when scores change
- **Game Status**: Start, end, and status changes announced
- **Data Loading**: Loading states and completion announced

### Contextual Information
- **Current Selection**: Always announced when navigating
- **Available Actions**: What you can do with current selection
- **Help Text**: Additional context for complex interface elements

## Performance Tips

### For Best VoiceOver Experience
1. **Reduce Speech Rate**: Lower VoiceOver speech rate for complex data
2. **Use Table Navigation**: Learn VO + arrow key combinations for tables
3. **Bookmark Favorites**: Use VoiceOver bookmarks for frequently used sections

### For Better Performance
1. **Close Other Apps**: Reduce system load for smoother VoiceOver
2. **Regular Updates**: Keep app updated for latest accessibility improvements
3. **Report Issues**: Contact support for accessibility problems

## Getting Help

### VoiceOver Help
- **VoiceOver Tutorial**: System Preferences > Accessibility > VoiceOver > Open VoiceOver Training
- **Quick Help**: VO + H for context-sensitive help
- **Commands Help**: VO + H + H for VoiceOver commands

### App-Specific Help
- **Interface Help**: Available within app (context-dependent)
- **Keyboard Shortcuts**: Command + / for available shortcuts
- **Documentation**: This guide and included documentation

## Feedback and Support

### Reporting Accessibility Issues
When reporting accessibility problems, please include:
1. **VoiceOver Version**: Found in System Preferences > Accessibility > VoiceOver > Open VoiceOver Utility > General
2. **macOS Version**: Apple menu > About This Mac
3. **Specific Issue**: Detailed description of the problem
4. **Steps to Reproduce**: How to recreate the issue
5. **Expected Behavior**: What should happen

### Feature Requests
We welcome suggestions for accessibility improvements:
- Additional keyboard shortcuts
- Better VoiceOver announcements
- Enhanced navigation options
- Integration with other assistive technologies

---

**Note**: This app is designed to be fully accessible to VoiceOver users. If you encounter any barriers to accessing content or functionality, please report them so we can address them promptly.

**Version**: MacVersion branch with comprehensive accessibility support  
**Last Updated**: August 17, 2025
