# Kitchen Sink Feature Implementation

## Overview
The "Kitchen Sink" feature has been successfully implemented to display additional MLB data that's available from the ESPN API but not shown in the main application views.

## What It Does
When viewing MLB game details, if additional data is available, a new option called **"Kitchen Sink (Additional MLB Data)"** will appear in the game details list. Selecting this option opens a comprehensive dialog with tabbed views of all the extra features.

## Features Included

### 🧑‍🤝‍🧑 **Rosters & Lineups**
- Complete team rosters for both teams
- Player positions, names, jersey numbers, and status
- Starting lineups and bench players

### 🗓️ **Season Series**  
- Head-to-head records between the teams
- Series summary (e.g., "PIT leads series 3-1")
- Individual game results in the season series

### 📰 **Game Articles**
- Game recaps, previews, and analysis
- Professional sports journalism content
- Headlines and full article text

### 🎰 **Against The Spread (ATS)**
- Team performance vs betting lines
- ATS records for betting context
- Team reliability indicators

### 🎯 **Expert Picks**
- Professional predictions and analysis
- Spread predictions and over/under picks
- Expert betting insights

### 📊 **Win Probability** *(when available)*
- Live probability tracking throughout the game
- Home/away team win percentages
- Probability changes with each play

### 🎥 **Video Highlights** *(when available)*
- Game highlight videos
- Key play footage
- Video duration and descriptions

## Technical Implementation

### Detection Logic
The Kitchen Sink only appears when the game has additional data available:
- Checks for presence of: `rosters`, `seasonseries`, `article`, `againstTheSpread`, `pickcenter`, `winprobability`, `videos`
- Only shows tabs for fields that actually contain data
- Automatically adapts to available content

### User Interface
- **Accessible Design**: All tables use the AccessibleTable class for screen reader support
- **Keyboard Navigation**: F6 key cycles between tabs
- **Responsive Layout**: Scrollable content areas for large datasets
- **Consistent Styling**: Matches existing application design patterns

### Data Handling
- Robust error handling for missing or malformed data
- Graceful degradation when fields are empty
- Flexible data structure parsing (handles lists, dicts, nested objects)

## Usage Instructions

1. **Open MLB Game Details**: Navigate to any MLB game and select it
2. **Look for Kitchen Sink**: If additional data is available, you'll see "Kitchen Sink (Additional MLB Data)" in the details list
3. **Explore Tabs**: Use mouse clicks or F6 key to navigate between different data categories
4. **View Details**: Each tab contains tables and formatted displays of the specific data type

## Data Sources
All data comes directly from ESPN's API and includes the same high-quality information used across ESPN's platforms:
- Real-time roster information
- Official game statistics and records
- Professional sports journalism
- Expert analysis and predictions

## Benefits to Users
- **Comprehensive Game Context**: See full picture beyond basic scores
- **Strategic Insights**: Access to expert predictions and betting information  
- **Historical Context**: Season series records and head-to-head performance
- **Rich Content**: Professional articles and video highlights
- **Accessibility**: Full screen reader support for all data

The Kitchen Sink feature transforms the application from a simple score viewer into a comprehensive MLB game analysis tool, providing users with the same depth of information available on ESPN's full website.
