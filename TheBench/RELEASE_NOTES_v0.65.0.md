# Scores v0.65.0 Release Notes

## 🎯 Major Features Release

This release adds significant new sports coverage with NCAA Hockey support and comprehensive poll/ranking displays for all college sports.

### ✨ What's New

#### 🏒 NCAA Hockey Support (Men's & Women's)
**Preliminary hockey Coverage** - The start of support for NCAA Men's and Women's Hockey:
- **Live Games & Scores** - Real-time game updates for both divisions
- **Team Listings** - Browse all NCAA hockey teams (50 men's, 44 women's teams)
- **Full Game Details** - Box scores, play-by-play, and team statistics
- **Schedule Navigation** - View any date's hockey games

#### 📊 Polls & Rankings Feature
**Official Poll Tracking** - View official polls and rankings for all NCAA sports:

**NCAA Football (4 Polls):**
- College Football Playoff Rankings (25 teams)
- CFP Playoff Seedings (12 teams)
- AP Top 25 Poll
- AFCA Coaches Poll

**NCAA Basketball (2 Polls Each):**
- Men's & Women's AP Poll (25 teams)
- Men's & Women's Coaches Poll (25 teams)

**NCAA Hockey (2 Polls Each):**
- Men's & Women's USA Hockey Poll (20/15 teams)
- Men's & Women's USCHO Poll (20/15 teams)

**Poll Features:**
- Multi-tab interface when multiple polls available
- Shows rank, team, record, points, and previous rank
- Movement indicators (↑/↓) for rank changes
- Accessible table format with keyboard navigation
- Ctrl+Tab to switch between poll tabs
- Use Alt+Q (Quick List), Alt+F (Full List), or Alt+T (Table) to switch between view modes for tables

### 🎨 User Experience Improvements

#### Clearer Sport Names
League abbreviations now display with full, descriptive names throughout the app:
- NCAA Women's Hockey (NCAAWH)
- NCAA Men's Hockey (NCAAH)
- NCAA Women's Basketball (NCAAWB)
- NCAA Men's Basketball (NCAAM)
- NCAA Football (NCAAF)

Applied to: main menu, live scores headers, window titles, and all labels.

### 🚀 Getting Started

**For New Users:**
1. Download and launch Scores v0.65.0
2. Select NCAA Men's or Women's Hockey from the main menu
3. Access Polls from any NCAA sport's game view
4. Explore live games, standings, and team schedules

**For Existing Users:**
- New hockey sports appear in your league selection list
- Look for "Polls" option in NCAA sport views
- All existing features continue to work as before

### 📋 Full Change List

#### Added
- Full NCAA Men's Hockey (NCAAH) support with 50 teams across 10+ conferences
- Full NCAA Women's Hockey (NCAAWH) support with 44 teams
- Polls/Rankings display for all NCAA sports (Football, Basketball, Hockey)
- Multi-tab poll interface supporting 2-4 polls per sport
- Poll rank change indicators and movement tracking

#### Changed
- Main league selection displays full descriptive sport names
- Live scores section headers use complete league names
- Window titles show formatted sport names
- All UI labels spell out sport names with gender designation

#### Technical
- Added `get_rankings()` API endpoint integration
- Created `PollsDialog` component with accessible table support
- Implemented hockey conference structure parsing
- Added format_league_name() utility for consistent naming

### 🎯 What's Next

Future releases will continue expanding sports coverage and adding new analysis features. Stay tuned for more updates!

---

**Version**: 0.65.0  
**Release Date**: December 14, 2025  
**Build**: Stable Release
