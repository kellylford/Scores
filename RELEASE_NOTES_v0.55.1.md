# Scores v0.55.1 Release Notes

## 🐛 Bug Fixes

### Home/Away Team Display Fix
**Critical fix for team ordering across all sports**

**Issue**: Teams were displayed in arbitrary order from the ESPN API, making it unclear which team was home and which was away. For example, in NHL games, Seattle appeared as the away team when they were actually playing at home.

**Fix**: 
- Teams now always display in consistent order: **Away at Home**
- Changed separator from "vs" to "at" for clarity
- Applies to all sports: NFL, NCAAF, NHL, NBA, MLB, WNBA, NCAA Basketball
- Modified display in:
  - Live scores list
  - Game details window titles
  - Game data objects

**Technical Details**:
- Updated `espn_api.py` to properly identify home/away teams using the `homeAway` field
- Modified `models/game.py` `GameData.get_display_text()` to sort teams correctly
- Updated `scores.py` game details display to maintain proper ordering

### NFL Week Detection Restored
**Fix for NFL/NCAAF opening to wrong week**

**Issue**: NFL and NCAAF were defaulting to Week 1 instead of the current week.

**Root Cause**: The `services/football_calendar.py` file was accidentally deleted in commit 7816336 during audio feature cleanup, even though it provided core functionality for week detection.

**Fix**:
- Restored `services/football_calendar.py` 
- NFL now correctly opens to Week 13 (current week as of November 26, 2025)
- NCAAF also benefits from proper week detection

## 📦 Files Changed
- `espn_api.py` - Team ordering logic
- `models/game.py` - Display text formatting  
- `scores.py` - Game details display
- `services/football_calendar.py` - Restored for week detection

## 🙏 Acknowledgments
Thanks to users who reported the team ordering issue, helping improve accuracy across all sports!

---

**Full Changelog**: v0.55.0...v0.55.1
