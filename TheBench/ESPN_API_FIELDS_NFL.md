# NFL API Field Reference

Generated from live API data on 2025-08-09T00:37:58.052186

## Available Endpoints

### Scoreboard Today

**URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard`
**Description**: Current day's games, scores, and basic information

**Key Fields**: events, season, week, leagues

**Sample Data**:
```json
{
  "top_level_keys": [
    "leagues",
    "season",
    "week",
    "events"
  ],
  "sample_event": {
    "id": "401776263",
    "name": "New York Giants at Buffalo Bills",
    "status": "Scheduled",
    "teams": [
      "Buffalo Bills",
      "New York Giants"
    ]
  }
}...
```

### Standings

**URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/standings`
**Description**: League standings and team records

**Key Fields**: 

**Sample Data**:
```json
{
  "top_level_keys": [
    "fullViewLink"
  ]
}...
```

### Teams

**URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams`
**Description**: All teams in the league with detailed information

**Key Fields**: 

**Sample Data**:
```json
{
  "top_level_keys": [
    "sports"
  ]
}...
```

### News

**URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/news`
**Description**: Recent news articles for the league

**Key Fields**: header, results

**Sample Data**:
```json
{
  "top_level_keys": [
    "header",
    "link",
    "articles"
  ],
  "sample_article": {
    "headline": "Lions-Falcons preseason game ends early after Morice Norris injury",
    "description": "The preseason game between the Lions and Falcons was suspended in the fourth quarter Friday night af...",
    "published": "2025-08-09T05:09:40Z"
  }
}...
```

### Game Details Examples

**Multiple Examples Available**: 2 examples

#### Example 1
**URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=401776263`
**Description**: Detailed game information for game 401776263

#### Example 2
**URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=401773012`
**Description**: Detailed game information for game 401773012

### Schedule Historical

**URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=20250808`
**Description**: Games for specific date (20250808)

**Key Fields**: events, season, week, leagues

**Sample Data**:
```json
{
  "top_level_keys": [
    "leagues",
    "events"
  ],
  "sample_event": {
    "id": "401773016",
    "name": "Detroit Lions at Atlanta Falcons",
    "status": "Final",
    "teams": [
      "Atlanta Falcons",
      "Detroit Lions"
    ]
  }
}...
```

## Field Categories

The following fields are available across various endpoints:

### Identification Fields
```
keys
keys.againstTheSpread
keys.againstTheSpread.item_type
keys.againstTheSpread.item_type.keys
keys.againstTheSpread.item_type.keys.records
keys.againstTheSpread.item_type.keys.records.truncated
keys.againstTheSpread.item_type.keys.records.type
keys.againstTheSpread.item_type.keys.team
keys.againstTheSpread.item_type.keys.team.truncated
keys.againstTheSpread.item_type.keys.team.type
keys.againstTheSpread.item_type.type
keys.againstTheSpread.length
keys.againstTheSpread.type
keys.articles
keys.articles.item_type
keys.articles.item_type.keys
keys.articles.item_type.keys.byline
keys.articles.item_type.keys.byline.sample
keys.articles.item_type.keys.byline.type
keys.articles.item_type.keys.categories
... and 466 more
```

### Other Fields
```
type
```

