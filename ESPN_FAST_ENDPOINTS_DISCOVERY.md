# ESPN Fast API Endpoints Discovery

## Performance Breakthrough
We discovered ESPN has dedicated fast endpoints that are 20-40x faster than the standard methods.

## Key Discovery: Fast Standings Pattern
**Pattern**: `https://site.api.espn.com/apis/v2/sports/{sport}/standings`

### Performance Comparison
- **Old method**: 30 individual team API calls = 7+ seconds
- **New method**: 1 standings endpoint call = 0.17 seconds  
- **Result**: 40x performance improvement

### Verified Fast Sports
| Sport | Endpoint | Speed | Teams/Divisions |
|-------|----------|-------|-----------------|
| MLB | `/v2/sports/baseball/mlb/standings` | 0.17s | 30 teams, 6 divisions |
| NFL | `/v2/sports/football/nfl/standings` | 0.14s | 32 teams, 2 conferences |
| NBA | `/v2/sports/basketball/nba/standings` | 0.13s | 30 teams, 2 conferences |
| NHL | `/v2/sports/hockey/nhl/standings` | 0.34s | 32 teams, 2 conferences |
| MLS | `/v2/sports/soccer/usa.1/standings` | 0.29s | Multiple divisions |
| College FB | `/v2/sports/football/college-football/standings` | 0.14s | 11 conferences |
| College BB | `/v2/sports/basketball/mens-college-basketball/standings` | 0.50s | 32 conferences |

## Other Fast Endpoints Discovered

### Team-Specific (Lightning Fast)
| Endpoint Pattern | Speed | Data Type |
|------------------|-------|-----------|
| `/teams/{id}/roster` | 0.14s | Player rosters |
| `/teams/{id}/injuries` | 0.10s | Injury reports |
| `/teams/{id}/leaders` | 0.14s | Team stat leaders |
| `/teams/{id}/schedule` | 0.45s | Full season schedule |

### League-Wide
| Endpoint | Speed | Data Type |
|----------|-------|-----------|
| `/events` | 0.14s | Current games/events |
| `/news` | 0.37s | Latest news articles |
| `/injuries` | 0.37s | League injury reports |
| `/transactions` | 0.16s | Recent transactions |

## API Patterns Discovered

### Base URLs
1. `https://site.api.espn.com/apis/v2/sports/{sport}/` - Fast standings
2. `https://site.api.espn.com/apis/site/v2/sports/{sport}/` - General endpoints

### Sport Path Formats
- Baseball: `baseball/mlb`
- Football: `football/nfl` 
- Basketball: `basketball/nba`
- Hockey: `hockey/nhl`
- Soccer: `soccer/usa.1` (MLS)
- College Football: `football/college-football`
- College Basketball: `basketball/mens-college-basketball`

## Implementation Impact

### Before Optimization
- Standings: 7+ seconds (30 API calls)
- Poor user experience with long loading times
- Needed loading indicators and progress bars

### After Optimization  
- Standings: 0.17 seconds (1 API call)
- Near-instant response times
- No loading indicators needed
- 40x performance improvement

## Usage Examples

### Fast MLB Standings
```python
url = "https://site.api.espn.com/apis/v2/sports/baseball/mlb/standings"
# Returns all 30 teams with complete standings data in 0.17s
```

### Team Roster
```python
url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/7/roster"
# Returns Brewers roster in 0.14s
```

### Current Games
```python
url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/events"  
# Returns today's games in 0.14s
```

## Future Opportunities

1. **Implement fast standings for all sports** (NFL, NBA, NHL, etc.)
2. **Add team roster views** using 0.14s roster endpoints
3. **Real-time injury tracking** using 0.10s injury endpoints  
4. **Live game events** using 0.14s events endpoint
5. **News integration** using 0.37s news endpoint

## Technical Notes

- All endpoints return JSON with consistent structure
- No authentication required
- Rate limiting unknown but appears generous
- Data includes full team stats, records, games back, streaks
- Team IDs consistent across different endpoints

This discovery opens up possibilities for a much more responsive sports app across all major leagues.
