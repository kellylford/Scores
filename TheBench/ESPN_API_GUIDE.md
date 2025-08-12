# ESPN API Integration Guide

## Overview
This guide documents the ESPN API endpoints and data structures used in the Sports Scores GUI application. The API provides comprehensive sports data including scores, game details, standings, statistics, and news.

## Base URL
```
https://site.api.espn.com/apis/site/v2/sports
```

## Supported Leagues
| League Code | API Path | Description |
|-------------|----------|-------------|
| NFL | football/nfl | National Football League |
| NBA | basketball/nba | National Basketball Association |
| MLB | baseball/mlb | Major League Baseball |
| NHL | hockey/nhl | National Hockey League |
| WNBA | basketball/wnba | Women's National Basketball Association |
| NCAAF | football/college-football | College Football |
| NCAAM | basketball/mens-college-basketball | Men's College Basketball |
| Soccer | soccer/eng.1 | English Premier League |

## API Endpoints

### 1. Scoreboard
**Endpoint:** `/{league_path}/scoreboard`
**Optional Parameters:** `?dates=YYYYMMDD`
**Purpose:** Get current or historical scores for a league

#### Response Structure
```json
{
  "events": [
    {
      "id": "game_id",
      "name": "Team A vs Team B",
      "competitions": [
        {
          "competitors": [
            {
              "team": {
                "displayName": "Team Name",
                "abbreviation": "ABC"
              },
              "score": "10",
              "homeAway": "home",
              "record": [{"summary": "10-5"}]
            }
          ],
          "status": {
            "type": {
              "description": "Final",
              "detail": "Final",
              "shortDetail": "Final"
            }
          }
        }
      ]
    }
  ]
}
```

### 2. Game Summary
**Endpoint:** `/{league_path}/summary?event={game_id}`
**Purpose:** Get detailed information about a specific game

#### Available Data Categories
- **header**: Basic game information (teams, status, scores)
- **boxscore**: Detailed game statistics
- **leaders**: Top performers and statistics
- **standings**: Current league standings
- **odds**: Betting lines and information
- **injuries**: Injury reports
- **broadcasts**: TV/radio broadcast information
- **news**: Related news articles
- **gameInfo**: Venue, weather, officials

### 3. News
**Endpoint:** `/{league_path}/news`
**Purpose:** Get news headlines for a league

#### Response Structure
```json
{
  "articles": [
    {
      "headline": "Article Title",
      "description": "Article summary",
      "published": "2025-01-01T12:00:00Z",
      "byline": "Author Name",
      "links": {
        "web": {"href": "https://..."},
        "mobile": {"href": "https://..."}
      }
    }
  ]
}
```

## Data Categories Deep Dive

### Boxscore Data
Contains detailed game statistics organized by teams and players.

**Structure:**
- Team statistics (shooting, rebounds, turnovers, etc.)
- Player statistics (points, assists, minutes played, etc.)
- Play-by-play data (for some sports)

**UI Considerations:**
- Best displayed in a table/grid format
- Should be navigable with keyboard
- Consider separate views for team vs player stats

### Leaders Data
Statistical leaders for various categories (scoring, assists, rebounds, etc.).

**Structure:**
```json
{
  "categories": {
    "scoring": {
      "leaders": [
        {
          "athlete": {"displayName": "Player Name"},
          "value": "25.5",
          "displayValue": "25.5 PPG"
        }
      ]
    }
  }
}
```

**UI Considerations:**
- List format works well
- Group by statistical category
- Show player name and statistical value

### Standings Data
Current league standings with team records and rankings.

**Structure:**
```json
{
  "entries": [
    {
      "team": {"displayName": "Team Name"},
      "stats": [
        {"name": "wins", "value": 15},
        {"name": "losses", "value": 5},
        {"name": "winPercent", "value": 0.750}
      ]
    }
  ]
}
```

**UI Considerations:**
- Table format ideal for standings
- Sort by wins/losses or percentage
- Include key stats (W-L record, percentage)

### Injuries Data
Player injury reports and status updates.

**Structure:**
```json
[
  {
    "athlete": {"displayName": "Player Name"},
    "status": "Questionable",
    "type": "Knee",
    "description": "Left knee soreness"
  }
]
```

**UI Considerations:**
- List format appropriate
- Show player name, injury type, and status
- Group by team if multiple teams involved

### Odds Data
Betting lines and over/under information.

**Structure:**
```json
[
  {
    "provider": {"name": "Sportsbook"},
    "details": "Team A -3.5",
    "overUnder": "45.5"
  }
]
```

### Broadcasts Data
TV and radio broadcast information.

**Structure:**
```json
[
  {
    "names": ["ESPN", "ABC"],
    "type": "tv"
  }
]
```

### GameInfo Data
Venue, weather, attendance, and officials information.

**Structure:**
```json
{
  "venue": {
    "fullName": "Stadium Name",
    "address": {
      "city": "City",
      "state": "State"
    }
  },
  "weather": {
    "displayValue": "Partly Cloudy",
    "temperature": 75
  },
  "attendance": 45000,
  "officials": [...]
}
```

## Implementation Best Practices

### 1. Error Handling
- Always check response status codes
- Handle empty or malformed data gracefully
- Provide meaningful error messages to users

### 2. Data Formatting
- Format complex data structures for screen reader accessibility
- Use consistent formatting across data types
- Provide context for numerical values (units, categories)

### 3. Performance
- Cache frequently accessed data when appropriate
- Use date parameters to avoid unnecessary data transfer
- Implement loading indicators for slower API calls

### 4. Accessibility
- Ensure all data is keyboard navigable
- Use proper list/table structures for screen readers
- Provide clear headings and labels for data sections

## Sport-Specific Considerations

### Baseball (MLB)
- Inning-by-inning scoring in boxscore
- Pitching statistics are prominent
- Weather affects outdoor games significantly

### Football (NFL/NCAAF)
- Quarter-by-quarter scoring
- Extensive statistical categories
- Injury reports are crucial for fantasy/betting

### Basketball (NBA/WNBA/NCAAM)
- Real-time scoring updates
- Shot charts and advanced analytics
- Player efficiency metrics

### Hockey (NHL)
- Period-by-period scoring
- Power play/penalty kill statistics
- Goaltender statistics are unique

### Soccer
- Minimal scoring, emphasis on possession
- Player booking/card information
- Match events (goals, cards, substitutions)

## Future Enhancements

### Potential Features
1. **Real-time Updates**: WebSocket connections for live scoring
2. **Historical Data**: Season/career statistics
3. **Advanced Analytics**: Team efficiency ratings, player impact metrics
4. **Social Features**: Share scores/highlights
5. **Customization**: User-defined statistical preferences

### API Expansion
- Additional leagues (MLS, international soccer, etc.)
- Minor league data
- College sports beyond football/basketball
- Olympic and international competitions

## Technical Notes

### Rate Limiting
- ESPN API doesn't publish official rate limits
- Implement reasonable delays between requests
- Cache data to minimize API calls

### Data Freshness
- Scores update every 30-60 seconds during games
- Standings update after game completion
- News updates throughout the day

### Error Codes
- 200: Success
- 404: Game/league not found
- 500: Server error (retry with exponential backoff)

## Sample API Calls

### Get MLB Scores for Today
```
GET https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard
```

### Get Specific Game Details
```
GET https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event=123456
```

### Get NBA News
```
GET https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news
```

---

*This guide is a living document and will be updated as new features are implemented and API patterns are discovered.*
