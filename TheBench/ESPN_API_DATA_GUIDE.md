# ESPN API Data Structure Guide
**For Sports Scores GUI Development**  
**Date: July 28, 2025**  
**Updated: January 2025 - Statistics Implementation**

## 🎯 Purpose
This guide documents the ESPN API data structures to help develop proper UI controls for complex data display, particularly for accessibility with screen readers.

## 📊 ESPN Statistics API Research Findings

### Statistics Endpoints Available
ESPN provides statistical data through multiple endpoints:

1. **Leaders Endpoint**: `/leaders` - Statistical leaders by category
   - Available for: MLB, NFL, NBA, NHL, NCAAF
   - Returns hierarchical data with categories and top performers
   - Structure: `{leaders: {category: {leaders: [...]}}}`

2. **Team Statistics**: Available in game details and standings
   - Found in boxscore data for individual games
   - Team-level aggregated stats less consistently available

3. **Player Statistics**: Primarily through leaders endpoint
   - Individual player performance metrics
   - Categorized by sport-specific metrics

### Sport-Specific Statistics Categories

#### MLB (Major League Baseball)
- **Hitting**: Batting average, home runs, RBIs, hits, runs
- **Pitching**: ERA, strikeouts, wins, saves, WHIP
- **Fielding**: Errors, fielding percentage, assists

#### NFL (National Football League)  
- **Passing**: Yards, touchdowns, completions, rating
- **Rushing**: Yards, touchdowns, attempts, average
- **Receiving**: Receptions, yards, touchdowns
- **Defense**: Tackles, sacks, interceptions

#### NBA (National Basketball Association)
- **Scoring**: Points per game, field goal percentage
- **Rebounding**: Total rebounds, offensive/defensive
- **Assists**: Assists per game, assist-to-turnover ratio
- **Defense**: Steals, blocks, defensive rating

#### NHL (National Hockey League)
- **Scoring**: Goals, assists, points
- **Goaltending**: Save percentage, goals against average
- **Power Play**: PP goals, PP assists
- **Penalty**: Penalty minutes, plus/minus

### Implementation Notes
- Statistics are most reliably available during active seasons
- Some categories may be empty during off-season
- Leaders endpoint provides top 10-20 performers per category
- Team statistics require aggregation from multiple sources

## 📊 Core Data Categories

### 1. Game/Event Data Structure
```json
{
  "events": [
    {
      "id": "401671716",
      "name": "Team A at Team B",
      "date": "2025-07-28T18:00Z",
      "competitions": [
        {
          "competitors": [
            {
              "homeAway": "home|away",
              "score": "24",
              "team": {
                "displayName": "Baltimore Orioles",
                "abbreviation": "BAL",
                "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/bal.png"
              },
              "record": [
                {"summary": "63-43"}
              ]
            }
          ],
          "status": {
            "type": {
              "description": "In Progress",
              "detail": "Middle 5th"
            }
          },
          "venue": {
            "fullName": "Oriole Park at Camden Yards",
            "address": {
              "city": "Baltimore",
              "state": "Maryland"
            }
          }
        }
      ]
    }
  ]
}
```

### 2. Standings Data Structure
**Endpoint:** `/standings`
```json
{
  "standings": {
    "entries": [
      {
        "team": {
          "displayName": "Baltimore Orioles",
          "abbreviation": "BAL",
          "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/bal.png"
        },
        "stats": [
          {"name": "wins", "value": 63},
          {"name": "losses", "value": 43},
          {"name": "winPercent", "value": 0.594},
          {"name": "gamesBehind", "value": 0},
          {"name": "streak", "displayValue": "W3"}
        ]
      }
    ]
  }
}
```

### 3. Leaders/Statistics Data Structure
**Endpoint:** `/leaders`
```json
{
  "leaders": {
    "hitting": {
      "leaders": [
        {
          "athlete": {
            "displayName": "Aaron Judge",
            "team": {
              "abbreviation": "NYY"
            }
          },
          "value": 47,
          "displayValue": "47 HR"
        }
      ]
    },
    "pitching": {
      "leaders": [
        {
          "athlete": {
            "displayName": "Gerrit Cole",
            "team": {
              "abbreviation": "NYY"
            }
          },
          "value": 2.85,
          "displayValue": "2.85 ERA"
        }
      ]
    }
  }
}
```

### 4. News Data Structure
**Endpoint:** `/news`
```json
{
  "articles": [
    {
      "headline": "Trade Deadline Approaches",
      "description": "Teams making final moves...",
      "published": "2025-07-28T15:30:00Z",
      "byline": "Jeff Passan",
      "links": {
        "web": {
          "href": "https://www.espn.com/mlb/story/_/id/..."
        }
      }
    }
  ]
}
```

### 5. Injuries Data Structure
**Endpoint:** Part of game summary
```json
{
  "injuries": [
    {
      "athlete": {
        "displayName": "Ronald Acuña Jr.",
        "position": {
          "abbreviation": "OF"
        }
      },
      "status": "Out",
      "type": "Knee",
      "description": "Torn ACL",
      "details": "Expected to miss remainder of season"
    }
  ]
}
```

### 6. Boxscore Data Structure
**Endpoint:** `/summary?event={gameId}` → boxscore section
```json
{
  "boxscore": {
    "teams": [
      {
        "team": {
          "displayName": "Baltimore Orioles"
        },
        "statistics": [
          {"name": "hits", "displayValue": "12"},
          {"name": "runs", "displayValue": "8"},
          {"name": "errors", "displayValue": "1"},
          {"name": "leftOnBase", "displayValue": "7"}
        ]
      }
    ],
    "players": [
      {
        "team": {
          "displayName": "Baltimore Orioles"
        },
        "statistics": [
          {
            "athlete": {
              "displayName": "Adley Rutschman"
            },
            "stats": ["3", "1", "2", "1", "0"] // AB, R, H, RBI, HR
          }
        ]
      }
    ]
  }
}
```

### 7. Odds/Betting Data Structure
**Endpoint:** Part of game summary
```json
{
  "odds": [
    {
      "provider": {
        "name": "DraftKings"
      },
      "details": "BAL -1.5",
      "overUnder": "8.5",
      "homeTeamOdds": {
        "favorite": true,
        "spread": "-1.5",
        "moneyLine": "-150"
      },
      "awayTeamOdds": {
        "favorite": false,
        "spread": "+1.5",
        "moneyLine": "+130"
      }
    }
  ]
}
```

### 8. Broadcasts Data Structure
```json
{
  "broadcasts": [
    {
      "names": ["ESPN", "ESPN2"],
      "type": {
        "shortName": "TV"
      }
    },
    {
      "names": ["ESPN Radio"],
      "type": {
        "shortName": "Radio"
      }
    }
  ]
}
```

### 9. Game Info Data Structure
```json
{
  "gameInfo": {
    "venue": {
      "fullName": "Oriole Park at Camden Yards",
      "address": {
        "city": "Baltimore",
        "state": "MD"
      }
    },
    "attendance": 45678,
    "weather": {
      "displayValue": "Partly Cloudy",
      "temperature": 82
    },
    "officials": [
      {
        "displayName": "John Smith",
        "position": "Home Plate Umpire"
      }
    ]
  }
}
```

## 🎨 UI Implementation Recommendations

### For Standings (Table/Grid Control)
**Use:** QTableWidget with sortable columns
```python
# Headers: Team, Wins, Losses, PCT, GB, Streak
standings_table = QTableWidget(len(teams), 6)
standings_table.setHorizontalHeaderLabels(['Team', 'W', 'L', 'PCT', 'GB', 'Streak'])
```

### For Leaders (List Control with Categories)
**Use:** QTreeWidget with expandable categories
```python
leaders_tree = QTreeWidget()
leaders_tree.setHeaderLabels(['Category', 'Player', 'Team', 'Stat'])
# Top level: "Hitting Leaders", "Pitching Leaders"
# Children: Individual player stats
```

### For Boxscore (Tabbed Table View)
**Use:** QTabWidget with QTableWidget for each team
```python
boxscore_tabs = QTabWidget()
# Tab 1: Team Stats, Tab 2: Player Stats
```

### For News (List Control)
**Use:** QListWidget with rich text items
```python
news_list = QListWidget()
# Each item shows: Headline, Author, Time
# Enter key opens full article in browser
```

### For Injuries (List Control)
**Use:** QListWidget with structured text
```python
injuries_list = QListWidget()
# Format: "Player Name (Position): Status - Description"
```

## 🔄 Data Refresh Patterns

### Real-time Data (Refresh every 30 seconds)
- Live game scores
- Game status updates
- Current period/inning

### Semi-static Data (Refresh every 5 minutes)
- Standings
- Team records
- Statistical leaders

### Static Data (Refresh once per session)
- Team logos
- Venue information
- Historical data

## 🎯 Sport-Specific Considerations

### Baseball (MLB)
- **Innings:** Show current inning and half (Top/Bottom)
- **Pitch Count:** Available in live games
- **RBI Leaders:** Important offensive stat
- **ERA Leaders:** Key pitching stat

### Football (NFL)
- **Quarters:** 1st, 2nd, 3rd, 4th, OT
- **Down and Distance:** Available in live games
- **Rushing/Passing Leaders:** Key offensive stats
- **Sack Leaders:** Important defensive stat

### Basketball (NBA)
- **Quarters:** 1st, 2nd, 3rd, 4th, OT
- **Points/Assists/Rebounds:** Key individual stats
- **Team Stats:** FG%, 3P%, FT%

### Hockey (NHL)
- **Periods:** 1st, 2nd, 3rd, OT, SO
- **Power Play:** Man advantage situations
- **Goals/Assists/Points:** Key individual stats
- **Save Percentage:** Important goalie stat

## 🛠️ Implementation Priority

### Phase 1: Core Data Display
1. ✅ Team information and scores
2. ✅ Game status and timing
3. ✅ Basic venue and weather

### Phase 2: Enhanced Views (Current Focus)
1. 🔄 Standings table with sortable columns
2. 🔄 Leaders tree view with categories
3. 🔄 News list with browser integration
4. 🔄 Injuries list with proper formatting

### Phase 3: Advanced Features
1. ⏭️ Boxscore tables with player stats
2. ⏭️ Live play-by-play updates
3. ⏭️ Historical team records
4. 🔄 Statistics view with player and team stats (Current)
5. ⏭️ Advanced statistical comparisons

## 🔗 API Endpoint Reference

### Core Endpoints by Sport
```
# Scoreboards
/football/nfl/scoreboard
/basketball/nba/scoreboard  
/baseball/mlb/scoreboard
/hockey/nhl/scoreboard

# Standings
/football/nfl/standings
/basketball/nba/standings
/baseball/mlb/standings
/hockey/nhl/standings

# News
/football/nfl/news
/basketball/nba/news
/baseball/mlb/news
/hockey/nhl/news

# Game Details
/football/nfl/summary?event={gameId}
/basketball/nba/summary?event={gameId}
/baseball/mlb/summary?event={gameId}
/hockey/nhl/summary?event={gameId}
```

### Query Parameters
```
?dates=YYYYMMDD          # Specific date
?season=2025             # Season year
?seasontype=2            # Regular season
?week=1                  # Week number (NFL)
```

## 🎯 Next Development Steps

1. **Implement QTableWidget for standings** - Replace current text display
2. **Add QTreeWidget for leaders** - Hierarchical display with categories
3. **Create dedicated news dialog** - Better than current popup
4. **Enhance injury display** - Structured list instead of basic text
5. **Add boxscore tables** - Full game statistics in tabbed view
6. **Statistics view implementation** - League-level statistics with player/team separation

## 📊 Statistics Implementation Plan

### ESPN API Statistics Research
Based on ESPN API exploration, statistics are available via:
- `/leaders` endpoint - Returns statistical leaders by category
- Game details include player and team statistics in boxscore data
- Leaders data includes hitting, pitching, fielding categories for MLB
- Similar patterns exist for NFL (passing, rushing, receiving, defense)
- NBA follows similar pattern (scoring, rebounding, assists, etc.)

### Navigation Structure for Statistics
```
Statistics (main menu item)
├── Player Statistics
│   ├── Hitting (MLB) / Passing (NFL) / Scoring (NBA)
│   ├── Pitching (MLB) / Rushing (NFL) / Rebounding (NBA) 
│   └── Fielding (MLB) / Receiving (NFL) / Assists (NBA)
└── Team Statistics
    ├── Offensive Stats
    ├── Defensive Stats
    └── Overall Performance
```

### Implementation Approach
1. ✅ Add `get_statistics()` to espn_api.py and ApiService
2. ✅ Create StatisticsDialog with QTabWidget for Player/Team separation
3. ✅ Use QTreeWidget for category hierarchy (similar to leaders)
4. ✅ Use QTableWidget for final statistical tables
5. ✅ Follow accessibility patterns from existing dialogs
6. ✅ Support for MLB, NFL, NBA, NHL, NCAAF leagues

### Technical Implementation Details
- **API Layer**: `espn_api.get_statistics(league)` calls `/leaders` endpoint
- **Service Layer**: `ApiService.get_statistics(league)` wrapper with error handling
- **UI Layer**: `StatisticsDialog` with player/team tabs
- **Data Structure**: Hierarchical categories with player lists
- **Accessibility**: QTreeWidget with proper navigation and screen reader support

### Usage in Application
Statistics are accessible via the main league view menu:
1. Select a league (MLB, NFL, NBA, NHL, NCAAF)
2. Navigate to "--- Statistics ---" menu item
3. Choose from Player Statistics or Team Statistics tabs
4. Browse hierarchical categories (Hitting, Pitching, etc.)
5. View individual player statistics in accessible tables

This guide will be updated as we discover new data structures and implement enhanced UI controls.
