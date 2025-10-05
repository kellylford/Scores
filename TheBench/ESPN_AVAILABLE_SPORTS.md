# ESPN API Available Sports

## Currently Implemented in Scores App

### American Sports
- **MLB** - Major League Baseball ✅
- **NFL** - National Football League ✅
- **NBA** - National Basketball Association ✅
- **NHL** - National Hockey League ✅
- **NCAAF** - NCAA Football (College Football) ✅
- **NCAAM** - NCAA Men's Basketball ✅
- **NCAAWB** - NCAA Women's Basketball ✅

### Currently Defined but Not Fully Implemented
- **WNBA** - Women's National Basketball Association (defined in LEAGUES dict)
- **Soccer** - English Premier League (eng.1) (defined in LEAGUES dict)

## Additional Sports Available via ESPN API

### Basketball
| Code | Name | Status | API Path |
|------|------|--------|----------|
| WNBA | Women's National Basketball Association | ✅ Available | `basketball/wnba` |

### Football (American)
| Code | Name | Status | API Path |
|------|------|--------|----------|
| XFL | XFL (Spring Football) | ✅ Available | `football/xfl` |

### Soccer/Football ⚽
| Code | Name | League | API Path |
|------|------|--------|----------|
| MLS | Major League Soccer | USA | `soccer/usa.1` |
| EPL | English Premier League | England | `soccer/eng.1` |
| EFL | English Football League Championship | England | `soccer/eng.2` |
| La Liga | Spanish LALIGA | Spain | `soccer/esp.1` |
| Bundesliga | German Bundesliga | Germany | `soccer/ger.1` |
| Serie A | Italian Serie A | Italy | `soccer/ita.1` |
| Ligue 1 | French Ligue 1 | France | `soccer/fra.1` |
| Liga MX | Mexican Primera División | Mexico | `soccer/mex.1` |
| UCL | UEFA Champions League | International | `soccer/uefa.champions` |

**Note:** All soccer leagues tested and confirmed working with ESPN API (HTTP 200)

### Racing 🏎️
| Code | Name | Status | API Path |
|------|------|--------|----------|
| F1 | Formula 1 | ✅ Available | `racing/f1` |
| NASCAR | NASCAR | ❌ Not Available | `racing/nascar` (400 error) |

### Combat Sports
| Code | Name | Status | API Path |
|------|------|--------|----------|
| UFC | Ultimate Fighting Championship | ❌ Not Available | `fighting/ufc` (400 error) |

### Individual Sports
| Sport | Status | API Path |
|-------|--------|----------|
| Tennis | ❌ Not Available | `tennis` (404 error) |
| Golf | ❌ Not Available | `golf` (404 error) |

## API Endpoint Patterns

ESPN uses consistent URL patterns for sports data:

### Scoreboard/Games
```
https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard
```

### Teams
```
https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams
```

### Standings
```
https://site.api.espn.com/apis/v2/sports/{sport}/{league}/standings
```

### Team Schedule
```
https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{id}/schedule
```

## Implementation Recommendations

### High Priority - Easy Wins

These sports use the same API structure as already-implemented sports:

1. **WNBA** (Women's Basketball)
   - Same structure as NBA
   - Has standings, teams, statistics
   - Active season: May-September
   - **Effort: Low** - Copy NBA patterns

2. **MLS** (Major League Soccer)
   - Already partially defined in app
   - Has standings, teams, statistics
   - Active season: February-November
   - **Effort: Medium** - Soccer has different stats structure

### Medium Priority - Popular Sports

3. **XFL** (Spring Football)
   - Same structure as NFL
   - Seasonal (spring season)
   - **Effort: Low** - Copy NFL patterns

4. **International Soccer Leagues**
   - La Liga, Bundesliga, Serie A, Ligue 1, Liga MX
   - Same structure as EPL/MLS
   - **Effort: Medium** - Reuse soccer implementation
   - High fan interest

5. **UEFA Champions League**
   - Tournament format (not full season)
   - High fan interest
   - **Effort: Medium-High** - Tournament bracket structure

### Low Priority

6. **Formula 1**
   - Different data structure (races, not games)
   - Different stats (lap times, qualifying, etc.)
   - **Effort: High** - New paradigm

## Feature Parity Checklist

For each new sport implementation, ensure:

- [ ] Add to `LEAGUES` dictionary in `espn_api.py`
- [ ] Implement `get_standings()` function
- [ ] Add to `_add_common_sections()` in `scores.py`
- [ ] Add command line arguments in `main.py`
- [ ] Test team schedules work correctly
- [ ] Test standings display with divisions/conferences
- [ ] Verify game details work
- [ ] Test statistics if applicable
- [ ] Update documentation

## Soccer-Specific Considerations

Soccer has some differences from American sports:

### Terminology
- **Matches** instead of games
- **Fixtures** instead of schedule
- **Tables** instead of standings
- **Draws** in addition to wins/losses

### Statistics
- Goals, assists, clean sheets
- Yellow/red cards
- Possession, shots on target
- Different from American sports stats

### Season Structure
- European leagues: August-May
- MLS: February-November
- Multiple competitions simultaneously (league, cup, European)

### Standings Format
- Points system (3 for win, 1 for draw, 0 for loss)
- Goal difference instead of games back
- Promotion/relegation in some leagues

## Current App Capacity

The Scores app architecture can support additional sports easily:

✅ **Ready for:**
- Any sport with games/matches format
- Team-based sports
- Sports with standings/rankings
- Sports with detailed game statistics

❌ **Not designed for:**
- Individual athletes (tennis, golf) - would need major refactor
- Race-based sports (F1, NASCAR) - different data model
- Combat sports (UFC) - event-based, not season-based

## Recommendations for Next Steps

### Immediate (Low Effort, High Value)
1. **Add WNBA** - Many requests, easy implementation
2. **Complete MLS/Soccer** - Already partially implemented

### Short Term (Medium Effort, Good Value)
3. **Add XFL** - Spring football content
4. **Add major European soccer leagues** - Huge fan bases

### Long Term (High Effort)
5. **Formula 1** - Would require new UI paradigm for races
6. **Tournament brackets** - For Champions League, March Madness, etc.

## Testing Endpoints

To test if a sport/league is available:

```bash
# Test scoreboard endpoint
curl -s "https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard" \
  -o /dev/null -w "%{http_code}\n"

# 200 = Available
# 400 = Bad Request (league may not exist)
# 404 = Not Found (endpoint doesn't exist)
```

## Soccer League Codes Reference

| Country/Region | League | Code |
|----------------|--------|------|
| USA | MLS | usa.1 |
| England | Premier League | eng.1 |
| England | Championship | eng.2 |
| Spain | La Liga | esp.1 |
| Germany | Bundesliga | ger.1 |
| Italy | Serie A | ita.1 |
| France | Ligue 1 | fra.1 |
| Mexico | Liga MX | mex.1 |
| Europe | Champions League | uefa.champions |

## Summary

ESPN's API provides comprehensive data for:
- ✅ **7 American sports** currently implemented
- ✅ **1 American sport** (WNBA) ready to implement
- ✅ **9+ soccer leagues** available to implement
- ✅ **1 racing sport** (F1) available with different structure
- ✅ **1 spring football** (XFL) available

The app's architecture is well-suited for adding team-based sports with season structures. WNBA and MLS would be the easiest next additions with the highest user value.
