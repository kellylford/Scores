# NCAA Basketball Implementation Summary

## Overview
Added complete support for NCAA Men's Basketball (NCAAM) and NCAA Women's Basketball (NCAAWB) to the Scores application, matching the feature set available for other major sports.

## Implementation Date
October 4, 2025

## Features Implemented

### 1. League Support
- ✅ **NCAAM** (Men's College Basketball) - Added to LEAGUES dictionary
- ✅ **NCAAWB** (Women's College Basketball) - Added to LEAGUES dictionary

### 2. Team Schedules
Both leagues now support full team schedule fetching with:
- **Season Format**: Uses year+1 format like NBA/NHL (2026 = 2025-26 season)
- **Complete Season Coverage**: Fetches all season types:
  - Preseason games (seasontype=1)
  - Regular season games (seasontype=2)
  - Postseason/Tournament games (seasontype=3)
- **Date Sorting**: All games sorted chronologically
- **Same API Structure**: Uses ESPN's team schedule endpoint matching other sports

### 3. Conference Standings
Implemented fast standings endpoints for both leagues:
- **NCAAM**: 32 conferences, ~380 teams
- **NCAAWB**: 31 conferences, ~362 teams

Standings include:
- Team name and logo
- Win-loss record
- Win percentage
- Conference grouping
- Sorted by conference, then by record

### 4. Command Line Arguments
Added comprehensive CLI support:

**Games Views:**
- `--ncaam` - Launch to NCAA Men's Basketball games view
- `--ncaawb` - Launch to NCAA Women's Basketball games view

**Teams Views:**
- `--ncaam-teams` - Launch to NCAA Men's Basketball teams view
- `--ncaawb-teams` - Launch to NCAA Women's Basketball teams view

**Standings Views:**
- `--ncaam-standings` - Launch to NCAA Men's Basketball standings view
- `--ncaawb-standings` - Launch to NCAA Women's Basketball standings view

## Technical Details

### File Changes

**espn_api.py:**
1. Added `"NCAAWB": "basketball/womens-college-basketball"` to LEAGUES dict
2. Added schedule handling for both NCAAM and NCAAWB in `get_team_schedule()`
3. Added conference filter logic in standings dispatcher
4. Created `_get_ncaam_standings_fast()` function
5. Created `_get_ncaawb_standings_fast()` function

**main.py:**
1. Added 6 new command line arguments (3 for each sport)
2. Updated `determine_startup_params()` to handle both sports in all view types

### API Endpoints Used

**Standings:**
- NCAAM: `https://site.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/standings`
- NCAAWB: `https://site.api.espn.com/apis/v2/sports/basketball/womens-college-basketball/standings`

**Team Schedules:**
- NCAAM: `https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{id}/schedule?season={year}&seasontype={type}`
- NCAAWB: `https://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/teams/{id}/schedule?season={year}&seasontype={type}`

### Season Type Handling
Like NBA/NHL, both NCAA basketball leagues now fetch all three season types:
- **1 = Preseason** (Exhibition games, early tournaments)
- **2 = Regular Season** (Conference and non-conference games)
- **3 = Postseason** (Conference tournaments, NCAA Tournament)

### Season Year Format
- Uses **year+1 format** (same as NBA/NHL)
- 2026 = 2025-26 season
- Default: 2026 for current season
- Historical seasons can be specified

## Testing Results

### NCAAM (Men's Basketball)
- ✅ Standings: 32 conferences, 380 teams successfully retrieved
- ✅ Schedule: Duke Blue Devils schedule shows 31 games (regular season)
- ✅ API Response: Fast response times (<1s)

### NCAAWB (Women's Basketball)
- ✅ Standings: 31 conferences, 362 teams successfully retrieved
- ✅ Schedule: UConn Huskies schedule shows 31 games (regular season)
- ✅ API Response: Fast response times (<1s)

## Integration with Existing Features

The implementation seamlessly integrates with existing features:
- ✅ Teams dialog (conference/division navigation)
- ✅ Standings display (conference-based grouping)
- ✅ Team schedule viewing
- ✅ Game details navigation
- ✅ Command line startup options

## Data Structure

### Standings Record Format
```python
{
    "team_name": "Duke Blue Devils",
    "team_id": "150",
    "abbreviation": "DUKE",
    "wins": 18,
    "losses": 5,
    "win_percentage": "0.783",
    "games_back": "—",  # Not used in college basketball
    "division": "ACC",  # Conference name
    "streak": "",
    "logo": "https://..."
}
```

### Schedule Event Format
Same structure as other sports:
- Event date and time
- Opponent information
- Home/Away designation
- Venue details
- Game status
- Scores (when available)

## Future Enhancements

Potential additions for NCAA basketball:
- [ ] Conference tournament bracket display
- [ ] NCAA Tournament bracket integration
- [ ] Rankings/polls display (AP Poll, Coaches Poll)
- [ ] Detailed team statistics
- [ ] Player statistics
- [ ] NET rankings and quad records

## Notes

1. **Conference Structure**: Unlike pro leagues with divisions, college basketball uses conferences
2. **Games Back**: Not applicable for college basketball standings
3. **Schedule Variability**: College teams play varying numbers of games (typically 30-35)
4. **Postseason**: Includes both conference tournaments and NCAA Tournament games
5. **Season Timing**: Season runs November through April (overlaps with NBA)

## Related Documentation
- [ESPN API Guide](ESPN_API_GUIDE.md)
- [NCAA Team Name Enhancement](NCAA_TEAM_NAME_ENHANCEMENT_SUMMARY.md)
- [Build Guide](../BUILD_GUIDE.md)

## Success Criteria

✅ All success criteria met:
- Both men's and women's basketball fully supported
- Team schedules show complete season (all game types)
- Conference standings display correctly
- Command line arguments functional
- Integration with existing UI components
- Fast API response times
- No breaking changes to existing functionality
