# Sports Scores GUI - Comprehensive Bug Fixes

## Issues Fixed

### 1. Start Times Not Showing
**Problem**: Games weren't displaying start times for scheduled games.
**Root Cause**: The ESPN API extraction was looking for `status.shortDetail` but the actual field is `status.type.shortDetail`.
**Solution**: Updated `espn_api.py` to correctly extract start times from `status.type.shortDetail` and fallback to `status.type.detail`.

### 2. Focus Management Not Working
**Problem**: Focus wasn't automatically going to lists after navigation, requiring manual Tab navigation.
**Root Cause**: UI focus was being set before the widgets were fully rendered and added to the layout.
**Solution**: Added `QTimer.singleShot(50, lambda: widget.setFocus())` calls to delay focus setting until after UI updates complete.

### 3. News Functionality Not Discoverable
**Problem**: News wasn't visible or accessible to users.
**Root Cause**: The scoreboard API doesn't include news data.
**Solution**: 
- Added separate `get_news()` function to fetch news from ESPN's news API endpoint
- News headlines now appear as "--- News ---" entry at the bottom of each league's scores list
- Improved news dialog with better formatting and scrollable list

## Technical Changes Made

### espn_api.py
- Fixed start time extraction to use `status.type.shortDetail`
- Added `get_news(league_key)` function for fetching news headlines
- Simplified scores data structure (removed unused news field)

### main.py
- Added `QTimer` import for delayed focus management
- Implemented proper focus timing with 50ms delays
- Updated news loading to use separate news API
- Improved news dialog with scrollable list and better layout
- Added news availability check before showing dialog
- Fixed missing `load_game_details()` method
- Corrected method call from `open_game` to `open_scores_item`

## Current Functionality

✅ **Start Times**: Now correctly display for all scheduled games  
✅ **Focus Management**: Lists automatically receive focus after navigation  
✅ **News Access**: News headlines available via "--- News ---" entry in each league  
✅ **Navigation**: Back button, refresh, and keyboard shortcuts work properly  
✅ **Game Details**: Detailed view with configurable fields  

## Testing Results

- Start times are now showing correctly (e.g., "7/31 - 8:00 PM EDT")
- Focus automatically goes to the appropriate list after each navigation
- News headlines are fetched and displayed properly (6+ headlines per league)
- All navigation and refresh functionality works as expected

## User Experience Improvements

1. **Clear News Indication**: "--- News ---" entry makes news easily discoverable
2. **Immediate Focus**: No need to manually Tab to lists after navigation
3. **Consistent Start Times**: All scheduled games show user-friendly start times
4. **Better News Dialog**: Scrollable list with proper sizing for multiple headlines
