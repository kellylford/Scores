# MLB API Field Reference

Generated from live API data on 2025-08-09T00:37:55.260444

## Available Endpoints

### Scoreboard Today

**URL**: `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard`
**Description**: Current day's games, scores, and basic information

**Key Fields**: events, season, week, leagues

**Sample Data**:
```json
{
  "top_level_keys": [
    "leagues",
    "season",
    "day",
    "events"
  ],
  "sample_event": {
    "id": "401696639",
    "name": "Cincinnati Reds at Pittsburgh Pirates",
    "status": "Final",
    "teams": [
      "Pittsburgh Pirates",
      "Cincinnati Reds"
    ]
  }
}...
```

### Standings

**URL**: `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/standings`
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

**URL**: `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams`
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

**URL**: `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/news`
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
    "headline": "Kershaw, Dodgers best Scherzer, Jays in duel of 3,000-K greats",
    "description": "Clayton Kershaw outpitched Max Scherzer in a matchup for the ages, and Mookie Betts homered and drov...",
    "published": "2025-08-09T05:35:07Z"
  }
}...
```

### Game Details Examples

**Multiple Examples Available**: 2 examples

#### Example 1
**URL**: `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event=401696639`
**Description**: Detailed game information for game 401696639

#### Example 2
**URL**: `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event=401696640`
**Description**: Detailed game information for game 401696640

### Schedule Historical

**URL**: `https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates=20250808`
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
    "id": "401696639",
    "name": "Cincinnati Reds at Pittsburgh Pirates",
    "status": "Final",
    "teams": [
      "Pittsburgh Pirates",
      "Cincinnati Reds"
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
keys.article
keys.article.keys
keys.article.keys.allowComments
keys.article.keys.allowComments.sample
keys.article.keys.allowComments.type
keys.article.keys.allowContentReactions
keys.article.keys.allowContentReactions.sample
... and 6158 more
```

### Other Fields
```
type
```

