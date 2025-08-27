# AI Agent Challenge: Recreate the Sports Scores Application

## Overview
This document provides comprehensive instructions for recreating a sophisticated sports scores application using Python and PyQt6. This challenge tests an AI agent's ability to combine technical depth with user experience understanding to build a complete, production-ready application.

## Project Summary
Build a cross-platform sports analysis application that provides live scores, detailed game information, team schedules, and advanced features like timezone conversion and accessibility support. The application should demonstrate enterprise-level architecture, robust error handling, and thoughtful user experience design.

## Core Requirements

### 1. Application Architecture
- **Main Entry Point**: `main.py` with command-line argument parsing for direct navigation
- **Modular Design**: Separate modules for API handling, data models, services, and UI components
- **Error Handling**: Custom exception classes with graceful fallback behavior
- **Configuration**: Support for user preferences and configurable game details

### 2. User Interface Requirements
- **Framework**: PyQt6 with accessible design principles
- **Navigation**: Stacked widget system with keyboard shortcuts (Alt+B for back, Alt+P/N for date navigation)
- **Accessibility**: Screen reader compatibility, proper ARIA labels, WCAG AA compliance
- **Responsive Design**: Adaptive layouts that work across different screen sizes

### 3. Data Integration
- **API Integration**: ESPN API wrapper with comprehensive error handling
- **Data Models**: Clean separation between raw API data and application models
- **Caching**: Intelligent caching system for API responses to improve performance
- **Real-time Updates**: Live score monitoring with change notifications

### 4. Feature Set

#### Core Sports Features
- **Multi-Sport Support**: NFL, MLB, NBA, NHL, NCAAF with sport-specific optimizations
- **Live Scores**: Real-time game updates with enhanced status information
- **Game Details**: Comprehensive game information including venue, weather, broadcasts
- **Team Schedules**: Full season schedules with smart date highlighting
- **Standings**: Sortable league standings with division organization
- **News Integration**: League news with browser integration for full articles

#### Advanced Features
- **Timezone Conversion**: Automatic conversion of game times to user's local timezone
- **Enhanced Game Display**: 
  - Baseball: Inning status, base runners, pitch counts, batter information
  - Football: Drive-by-drive breakdown, down/distance, field position
- **Audio Features**: Pitch location audio mapping for accessibility
- **Statistics**: Player and team statistics with proper formatting
- **Export Capabilities**: Game logs and statistics export functionality

### 5. Technical Specifications

#### Dependencies
```
PyQt6==6.9.1
requests==2.32.4
pytz==2024.2
pyinstaller==6.15.0  # For executable building
```

#### File Structure
```
Scores/
├── main.py                 # Application entry point
├── scores.py              # Main application logic
├── espn_api.py           # ESPN API integration
├── timezone_utils.py     # Timezone conversion utilities
├── exceptions.py         # Custom exception classes
├── accessible_table.py   # Accessible table components
├── windows_notifications.py  # OS notification system
├── models/
│   ├── game.py           # Game data model
│   ├── news.py           # News data model
│   └── standings.py      # Standings data model
├── services/
│   └── api_service.py    # API service wrapper
└── requirements.txt      # Dependencies
```

## Detailed Implementation Guide

### Phase 1: Core Infrastructure
1. **Project Setup**
   - Create virtual environment and install dependencies
   - Set up project structure with proper module organization
   - Implement basic PyQt6 application shell

2. **API Integration**
   - Build ESPN API wrapper with rate limiting and error handling
   - Implement data models for games, news, and standings
   - Create service layer for API abstraction

3. **Basic UI Framework**
   - Implement stacked widget navigation system
   - Create base classes for different view types
   - Add keyboard navigation and accessibility features

### Phase 2: Sports Features
1. **Game Display System**
   - Implement game list views with proper formatting
   - Add sport-specific display logic
   - Create game detail views with comprehensive information

2. **Live Score Integration**
   - Build real-time update system
   - Implement score change monitoring
   - Add visual indicators for live games

3. **Schedule and Standings**
   - Create team schedule views with date navigation
   - Implement sortable standings tables
   - Add division and conference organization

### Phase 3: Advanced Features
1. **Timezone Conversion**
   - Implement automatic timezone detection
   - Build conversion system for game times
   - Apply conversions throughout the application

2. **Enhanced Game Experience**
   - Add sport-specific enhanced displays
   - Implement detailed play-by-play for baseball and football
   - Create audio mapping system for accessibility

3. **User Experience Polish**
   - Add comprehensive error handling with user-friendly messages
   - Implement caching for improved performance
   - Create export functionality for data

### Phase 4: Production Features
1. **Accessibility**
   - Ensure full screen reader compatibility
   - Implement proper focus management
   - Add audio feedback systems

2. **Build System**
   - Create executable building scripts
   - Implement version management
   - Add release documentation

## Key Technical Challenges

### 1. Timezone Conversion
**Challenge**: Convert ESPN's Eastern Time game times to user's local timezone
**Solution**: 
- Detect user's timezone automatically
- Parse ESPN time formats (e.g., "7:00 PM EDT")
- Convert and display in local time (e.g., "6:00 PM CDT")
- Handle edge cases like "TBD" and live game statuses

### 2. Sport-Specific Display Logic
**Challenge**: Each sport has different data structures and display requirements
**Solution**:
- Create flexible data models that adapt to different sports
- Implement sport-specific formatting in display logic
- Handle varying API response formats gracefully

### 3. Real-time Updates
**Challenge**: Provide live score updates without overwhelming the API
**Solution**:
- Implement intelligent polling based on game status
- Use background threads for updates
- Cache responses to minimize API calls

### 4. Accessibility
**Challenge**: Make the application fully accessible to screen reader users
**Solution**:
- Use proper PyQt6 accessibility APIs
- Implement custom accessible table widgets
- Provide audio feedback for complex data like pitch locations

## Success Criteria

### Technical Excellence
- [ ] Clean, modular code architecture
- [ ] Comprehensive error handling
- [ ] Efficient API usage with caching
- [ ] Cross-platform compatibility
- [ ] Memory and performance optimization

### User Experience
- [ ] Intuitive navigation system
- [ ] Responsive design across screen sizes
- [ ] Accessibility compliance
- [ ] Informative error messages
- [ ] Smooth real-time updates

### Feature Completeness
- [ ] Multi-sport support with sport-specific features
- [ ] Comprehensive game information display
- [ ] Timezone conversion working correctly
- [ ] Enhanced game displays (baseball/football)
- [ ] Export and sharing capabilities

### Production Readiness
- [ ] Executable building system
- [ ] Version management
- [ ] Documentation
- [ ] Error logging and debugging
- [ ] User configuration system

## Evaluation Framework

### Code Quality (25%)
- Architecture and modularity
- Error handling and edge cases
- Performance and efficiency
- Code documentation and clarity

### User Experience (25%)
- Interface design and usability
- Accessibility implementation
- Error messaging and feedback
- Feature discoverability

### Technical Implementation (25%)
- API integration robustness
- Data model design
- Real-time update system
- Cross-platform compatibility

### Innovation and Polish (25%)
- Advanced features implementation
- User-centric improvements
- Creative problem solving
- Production readiness

## Notes for AI Agents

This challenge tests your ability to:
1. **Understand Complex Requirements**: Parse user needs and translate them into technical specifications
2. **System Design**: Create scalable, maintainable architecture
3. **User-Centric Development**: Balance technical implementation with user experience
4. **Problem Solving**: Handle edge cases and technical challenges creatively
5. **Production Mindset**: Build software that works reliably in real-world scenarios

The original development process emphasized iterative improvement based on user feedback, with a focus on accessibility and real-world usability. The timezone conversion feature, for example, emerged from a simple user request but required deep technical implementation across multiple layers of the application.

Success in this challenge requires not just technical proficiency, but the ability to think holistically about user needs, system architecture, and production considerations. The resulting application should feel polished and professional, not just functionally complete.

## Reference Implementation

The reference implementation can be found at: https://github.com/kellylford/Scores

Key commits to study:
- `feat: Add automatic timezone conversion for game times` - Demonstrates feature implementation across multiple layers
- `Complete team navigation infrastructure implementation` - Shows complex UI state management
- `fix: Apply timezone conversion in GameData model` - Illustrates debugging and problem-solving approach

Good luck, and may the best AI implementation win! 🚀
