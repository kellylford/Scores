# ESPN API Comprehensive Reference Guide

*Generated on August 9, 2025*

This reference provides detailed documentation of ESPN's public API endpoints for MLB and NFL, including data structures, available fields, and real-world examples.

## Table of Contents

1. [Overview](#overview)
2. [Base Configuration](#base-configuration)
3. [MLB API Reference](#mlb-api-reference)
4. [NFL API Reference](#nfl-api-reference)
5. [Common Data Patterns](#common-data-patterns)
6. [Integration Examples](#integration-examples)

---

## Overview

ESPN provides a comprehensive sports API through `site.api.espn.com` that offers:

- **Real-time scores and game information**
- **Team and player statistics**
- **News articles and content**
- **Standings and rankings**
- **Historical data and schedules**
- **Detailed game summaries with play-by-play**

### Key Features
- **Free Access**: No API key required for basic endpoints
- **JSON Responses**: All data returned in JSON format
- **Real-time Updates**: Live game data and scores
- **Rich Metadata**: Extensive team, player, and game information
- **Cross-platform**: Same endpoints work for web, mobile, and desktop applications

---

## Base Configuration

### Base URL
```
https://site.api.espn.com/apis/site/v2/sports
```

### League Paths
- **MLB**: `baseball/mlb`
- **NFL**: `football/nfl`

### Common Parameters
- **dates**: Format `YYYYMMDD` for specific date queries
- **event**: Game ID for detailed game information
- **team**: Team ID for team-specific data

---

## MLB API Reference

### 1. Scoreboard Endpoint

**URL**: `{BASE_URL}/baseball/mlb/scoreboard`

**Description**: Current day's games with scores, status, and basic information

#### Key Data Structure:
```json
{
  "leagues": [...],
  "season": {"type": 2, "year": 2025},
  "day": {"date": "2025-08-09"},
  "events": [...]
}
```

#### Game Event Structure:
```json
{
  "id": "401696639",
  "name": "San Diego Padres at Pittsburgh Pirates",
  "status": {
    "type": {
      "id": "2",
      "name": "STATUS_IN_PROGRESS", 
      "description": "In Progress",
      "detail": "Bottom 8th",
      "shortDetail": "Bot 8th"
    }
  },
  "competitions": [{
    "competitors": [
      {
        "id": "25",
        "homeAway": "home",
        "team": {
          "id": "23",
          "displayName": "Pittsburgh Pirates",
          "abbreviation": "PIT",
          "location": "Pittsburgh",
          "color": "fdb827",
          "logos": [...]
        },
        "score": "3",
        "record": [{"summary": "62-75"}]
      }
    ],
    "venue": {
      "fullName": "PNC Park",
      "address": {"city": "Pittsburgh", "state": "PA"}
    },
    "weather": {
      "temperature": 78,
      "conditionId": "1",
      "description": "Fair"
    }
  }]
}
```

#### Available Fields:
- **Game Identification**: `id`, `name`, `uid`
- **Status Information**: `status.type.description`, `status.type.detail`
- **Team Information**: `team.displayName`, `team.abbreviation`, `team.color`
- **Scores**: `score` (current score)
- **Records**: `record.summary` (win-loss record)
- **Venue**: `venue.fullName`, `venue.address`
- **Weather**: `weather.temperature`, `weather.description`
- **Timing**: `date` (game start time)

### 2. Game Details/Summary Endpoint

**URL**: `{BASE_URL}/baseball/mlb/summary?event={game_id}`

**Description**: Comprehensive game information including play-by-play, statistics, and metadata

#### Key Sections Available:

##### Header Information:
```json
{
  "header": {
    "competitions": [...],
    "league": {...},
    "season": {...}
  }
}
```

##### Play-by-Play Data:
```json
{
  "plays": [
    {
      "id": "4016966390156",
      "type": {
        "id": "1",
        "text": "Pitch"
      },
      "text": "Ball 1",
      "awayScore": 2,
      "homeScore": 3,
      "period": {"number": 8},
      "clock": {"displayValue": ""},
      "scoringPlay": false,
      "pitchVelocity": 94.2,
      "pitchType": {"id": "2", "text": "Fastball"}
    }
  ]
}
```

##### Boxscore Statistics:
```json
{
  "boxscore": {
    "teams": [
      {
        "team": {...},
        "statistics": [
          {
            "name": "hits",
            "displayName": "Hits", 
            "displayValue": "8"
          }
        ]
      }
    ],
    "players": [
      {
        "team": {...},
        "statistics": [
          {
            "name": "batting",
            "athletes": [
              {
                "athlete": {...},
                "stats": ["2", "1", "1", "0", "0", "0"]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

#### Available Game Detail Fields:
- **plays**: Complete play-by-play with pitch details
- **boxscore**: Team and player statistics  
- **gameInfo**: Venue, weather, attendance
- **leaders**: Statistical leaders for the game
- **broadcasts**: TV/radio coverage information
- **news**: Game-related news articles
- **odds**: Betting lines and information
- **injuries**: Injury reports for participating teams

### 3. Standings Endpoint

**URL**: `{BASE_URL}/baseball/mlb/standings`

**Description**: Current league standings with team records and division information

#### Structure:
```json
{
  "children": [
    {
      "name": "American League",
      "children": [
        {
          "name": "AL East",
          "standings": {
            "entries": [
              {
                "team": {...},
                "stats": [
                  {"name": "wins", "value": 62},
                  {"name": "losses", "value": 75},
                  {"name": "gamesBehind", "value": 15.0},
                  {"name": "winPercent", "value": 0.453}
                ]
              }
            ]
          }
        }
      ]
    }
  ]
}
```

### 4. Teams Endpoint

**URL**: `{BASE_URL}/baseball/mlb/teams`

**Description**: All MLB teams with detailed information

#### Team Data:
```json
{
  "sports": [{
    "leagues": [{
      "teams": [
        {
          "id": "23",
          "uid": "s:1~l:10~t:23",
          "displayName": "Pittsburgh Pirates",
          "abbreviation": "PIT",
          "location": "Pittsburgh",
          "color": "fdb827",
          "alternateColor": "000000",
          "isActive": true,
          "logos": [...],
          "record": {"items": [...]},
          "venue": {...}
        }
      ]
    }]
  }]
}
```

### 5. Team Athletes Endpoint

**URL**: `{BASE_URL}/baseball/mlb/teams/{team_id}/athletes`

**Description**: Players roster for a specific team

#### Player Data:
```json
{
  "athletes": [
    {
      "id": "31094",
      "displayName": "Paul Skenes",
      "shortName": "P. Skenes",
      "position": {
        "id": "1",
        "name": "Pitcher",
        "abbreviation": "P"
      },
      "jersey": "30",
      "height": "6'6\"",
      "weight": "235",
      "age": 22,
      "birthPlace": {
        "city": "Fullerton",
        "state": "CA"
      }
    }
  ]
}
```

### 6. News Endpoint

**URL**: `{BASE_URL}/baseball/mlb/news`

**Description**: Recent MLB news articles

#### Article Structure:
```json
{
  "articles": [
    {
      "headline": "Pirates' Paul Skenes continues dominant rookie season",
      "description": "The rookie right-hander struck out 8 in 6 innings...",
      "published": "2025-08-09T02:30:00Z",
      "byline": "ESPN Staff",
      "links": {
        "web": {"href": "https://www.espn.com/..."},
        "mobile": {"href": "https://m.espn.com/..."}
      },
      "images": [...]
    }
  ]
}
```

---

## NFL API Reference

### 1. Scoreboard Endpoint

**URL**: `{BASE_URL}/football/nfl/scoreboard`

**Description**: Current day's games (primarily during NFL season)

#### Key Differences from MLB:
- **Season Structure**: Weeks instead of continuous games
- **Game Types**: Regular season, playoffs, preseason
- **Quarter/Period**: Different timing structure

#### Game Event Structure:
```json
{
  "id": "401776263",
  "name": "Buffalo Bills at Chicago Bears",
  "status": {
    "type": {
      "description": "Scheduled",
      "detail": "Sat, Aug 10 - 1:00 PM EDT"
    }
  },
  "week": {"number": 1, "text": "Preseason Week 1"},
  "season": {"type": 1, "year": 2025}
}
```

### 2. Game Details/Summary Endpoint

**URL**: `{BASE_URL}/football/nfl/summary?event={game_id}`

#### NFL-Specific Fields:

##### Drive Information:
```json
{
  "drives": {
    "previous": [
      {
        "id": "401776263001",
        "description": "14 plays, 75 yards, 7:23",
        "start": {...},
        "end": {...},
        "plays": [...]
      }
    ]
  }
}
```

##### Play Data:
```json
{
  "plays": [
    {
      "id": "40177626300101",
      "type": {"text": "Rush"},
      "text": "Justin Fields rush for 2 yards to the CHI 22",
      "down": 1,
      "distance": 10,
      "yardLine": 20,
      "yardsGained": 2,
      "scoringPlay": false
    }
  ]
}
```

### 3. Teams Endpoint

**URL**: `{BASE_URL}/football/nfl/teams`

#### NFL Team Structure:
```json
{
  "team": {
    "id": "2",
    "displayName": "Buffalo Bills",
    "conference": {"name": "AFC"},
    "division": {"name": "AFC East"},
    "color": "00338d",
    "record": {
      "items": [
        {"summary": "11-6", "type": "total"}
      ]
    }
  }
}
```

---

## Common Data Patterns

### Status Types Across Sports

#### Game Status Values:
- **`STATUS_SCHEDULED`**: Game not yet started
- **`STATUS_IN_PROGRESS`**: Game currently being played
- **`STATUS_FINAL`**: Game completed
- **`STATUS_POSTPONED`**: Game delayed/postponed
- **`STATUS_CANCELLED`**: Game cancelled

#### MLB Specific Status Details:
- `"Top 1st"`, `"Bot 3rd"`, `"Mid 7th"`
- `"Final"`, `"Final/10"` (extra innings)
- `"Delayed"`, `"Postponed"`

#### NFL Specific Status Details:
- `"1st Quarter"`, `"2nd Quarter"`, `"Halftime"`
- `"Final"`, `"Final/OT"`
- `"Scheduled"` with date/time

### Team Information Pattern:
```json
{
  "team": {
    "id": "string",
    "displayName": "Full Team Name",
    "abbreviation": "3-letter code",
    "location": "City Name", 
    "color": "hex color code",
    "logos": [...],
    "record": [...]
  }
}
```

### Competition/Game Pattern:
```json
{
  "competition": {
    "id": "game_id",
    "competitors": [
      {
        "homeAway": "home|away",
        "team": {...},
        "score": "current_score",
        "record": [...]
      }
    ],
    "venue": {...},
    "status": {...}
  }
}
```

---

## Integration Examples

### 1. Getting Today's Games:
```python
import requests

def get_todays_games(league):
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    response = requests.get(url)
    data = response.json()
    
    games = []
    for event in data.get("events", []):
        game = {
            "id": event["id"],
            "name": event["name"],
            "status": event["status"]["type"]["description"],
            "teams": [comp["team"]["displayName"] 
                     for comp in event["competitions"][0]["competitors"]]
        }
        games.append(game)
    return games
```

### 2. Getting Game Details:
```python
def get_game_details(league, game_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event={game_id}"
    response = requests.get(url)
    return response.json()
```

### 3. Available Detail Fields by Sport:

#### MLB Game Details:
- `plays` - Complete play-by-play with pitch details
- `boxscore` - Team and player statistics
- `leaders` - Game statistical leaders
- `broadcasts` - TV/radio information
- `gameInfo` - Venue, weather, attendance
- `odds` - Betting information
- `injuries` - Team injury reports
- `news` - Game-related articles

#### NFL Game Details:
- `drives` - Drive summaries and play sequences
- `plays` - Individual play details
- `boxscore` - Team and player statistics
- `leaders` - Game statistical leaders
- `broadcasts` - TV/radio information
- `gameInfo` - Venue and game information
- `odds` - Betting information
- `injuries` - Team injury reports
- `news` - Game-related articles

### 4. Rate Limiting Considerations:
- No official rate limits published
- Recommended: 1-2 requests per second maximum
- Cache data when possible
- Use appropriate User-Agent headers

### 5. Error Handling:
```python
def safe_api_request(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API Error: {e}")
        return {}
```

---

## Additional Resources

- **Live API Explorer**: Use the generated JSON files for detailed field exploration
- **ESPN_API_REFERENCE_MLB.json**: Complete MLB API structure analysis
- **ESPN_API_REFERENCE_NFL.json**: Complete NFL API structure analysis

This reference provides the foundation for building comprehensive sports applications using ESPN's API. The data is rich, real-time, and covers all major aspects of professional sports information.
