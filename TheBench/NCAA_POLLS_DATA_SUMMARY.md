# NCAA Polls/Rankings Data - ESPN API Summary

## Overview
ESPN provides comprehensive poll/ranking data for all major NCAA sports through dedicated rankings endpoints. **This includes team records that are NOT available in the regular standings endpoints** for hockey.

## Available Poll Data by Sport

### NCAA Football ✅
**Endpoint**: `https://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings`

**4 Ranking Systems:**
1. **Playoff Committee Rankings (CFP)** - 25 teams
   - Official College Football Playoff committee rankings
   - Most important for playoff selection
   
2. **College Football Playoff Seedings** - 12 teams
   - Actual playoff bracket seedings
   - Shows tournament matchups
   
3. **AP Top 25** - 25 teams
   - Associated Press media poll
   - Points and voting included
   - Movement indicators (previous rank)
   
4. **AFCA Coaches Poll (USA Today)** - 25 teams
   - Coaches poll
   - Points and movement

**Data Includes:**
- Current rank
- Previous rank (shows movement)
- Team record (W-L)
- Poll points
- Team info (name, logo, colors, etc.)

---

### NCAA Men's Basketball ✅
**Endpoint**: `https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/rankings`

**2 Ranking Systems:**
1. **AP Top 25** - 25 teams
2. **Coaches Poll** - 25 teams

**Data Includes:** Same as football

---

### NCAA Women's Basketball ✅
**Endpoint**: `https://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/rankings`

**2 Ranking Systems:**
1. **AP Top 25** - 25 teams
2. **Coaches Poll** - 25 teams

**Data Includes:** Same as football

---

### NCAA Men's Hockey ✅ 🏒
**Endpoint**: `https://site.api.espn.com/apis/site/v2/sports/hockey/mens-college-hockey/rankings`

**2 Ranking Systems:**
1. **USA Hockey Men's Poll** - 20 teams
2. **USCHO Men's Poll** - 20 teams

**Data Includes:**
- Current rank
- Previous rank
- **Team record (W-L-T)** ⭐ **Records ARE available here!**
- Points
- Team info

**Sample (Current Top 5):**
```
1. Michigan (15-3)
2. Wisconsin (10-2-2)  ← Records available in polls!
3. Michigan State (11-3)
4. Minnesota Duluth (12-4)
5. Denver (9-5-1)
```

---

### NCAA Women's Hockey ✅ 🏒
**Endpoint**: `https://site.api.espn.com/apis/site/v2/sports/hockey/womens-college-hockey/rankings`

**2 Ranking Systems:**
1. **USA Hockey Women's Poll** - 15 teams
2. **USCHO Women's Poll** - 15 teams

**Data Includes:** Same as men's hockey

**Sample (Current Top 5):**
```
1. Wisconsin (16-1-1)  ← Wisconsin IS in poll data!
2. Ohio State (15-1)
3. Minnesota (12-4)
4. Penn State (17-1)
5. Minnesota Duluth (10-6)
```

**⭐ KEY FINDING:** Wisconsin Badgers women's hockey **IS PRESENT in poll data** even though missing from teams endpoint!

---

## Data Structure

### Rankings Response Format
```json
{
  "sports": [...],
  "leagues": [...],
  "rankings": [
    {
      "name": "AP Top 25",
      "type": "ap",
      "shortName": "AP Poll",
      "headline": "2025 NCAA Football Rankings - AP Poll Week 16",
      "ranks": [
        {
          "current": 1,
          "previous": 2,
          "points": 1650,
          "recordSummary": "13-0",
          "team": {
            "id": "84",
            "location": "Indiana",
            "nickname": "Hoosiers",
            "abbreviation": "IND",
            "displayName": "Indiana Hoosiers",
            "logos": [...],
            "color": "990000",
            "links": [...]
          }
        },
        ...
      ]
    },
    ...
  ],
  "latestSeason": {...},
  "latestWeek": {...},
  "weeks": [...],
  "availableRankings": [...]
}
```

### Key Fields
- `current`: Current rank position
- `previous`: Previous week's rank (0 = Not Ranked)
- `points`: Poll points/votes
- `recordSummary`: Team record as string (e.g., "13-0", "10-2-2")
- `team`: Full team object with all metadata

---

## Solution for Hockey Record Problem

### The Issue
- Hockey standings endpoint has minimal data (only 1 of 50+ teams)
- Teams endpoint doesn't include records
- Individual team endpoints have empty record fields

### The Solution ✅
**Use the rankings/polls endpoint!**

For teams in the polls (Top 15-25):
- ✅ Records ARE available in `recordSummary` field
- ✅ Wisconsin women's hockey IS present (#1 ranked!)
- ✅ Both men's and women's polls updated weekly
- ✅ Covers top competitive teams

For teams NOT in polls:
- Still show 0-0 or "Unranked" status
- Most users care about ranked teams anyway
- Polls cover ~40% of teams (20 of 50 for men, 15 of 44 for women)

---

## Implementation Recommendations

### 1. Add Poll/Rankings View
Create new views for each sport:
- `--ncaaf-rankings` / `--ncaaf-polls`
- `--ncaam-rankings` / `--ncaam-polls`
- `--ncaawb-rankings` / `--ncaawb-polls`
- `--ncaah-rankings` / `--ncaah-polls`
- `--ncaawh-rankings` / `--ncaawh-polls`

### 2. Enhance Standings with Poll Data
For hockey specifically:
- Fetch both standings AND rankings
- Merge poll data into standings
- Show poll rank next to team name
- Display actual records from polls
- Highlight ranked teams

### 3. UI Enhancements
- Show poll rank badges (🥇 #1, 🥈 #2, etc.)
- Display movement arrows (↑↓)
- Color-code ranked teams
- Show multiple polls side-by-side
- Include poll points

### 4. Team Detail Enhancements
- Show team's ranking across all polls
- Display ranking history/trend
- Show votes received
- Include "Others Receiving Votes" section

---

## Example Integration for Hockey

```python
def _get_ncaah_standings_with_polls():
    # Get regular standings (basic team list)
    standings = _get_ncaah_standings_fast()
    
    # Get rankings/polls
    rankings_resp = requests.get(
        'https://site.api.espn.com/apis/site/v2/sports/hockey/mens-college-hockey/rankings'
    )
    
    if rankings_resp.status_code == 200:
        rankings_data = rankings_resp.json()
        
        # Create lookup of team records from polls
        records = {}
        poll_ranks = {}
        
        for poll in rankings_data['rankings']:
            poll_name = poll['shortName']
            for team in poll['ranks']:
                team_id = team['team']['id']
                records[team_id] = team.get('recordSummary', '0-0-0')
                if team_id not in poll_ranks:
                    poll_ranks[team_id] = []
                poll_ranks[team_id].append({
                    'poll': poll_name,
                    'rank': team['current'],
                    'points': team.get('points', 0)
                })
        
        # Merge poll data into standings
        for team in standings:
            team_id = team['team_id']
            if team_id in records:
                # Parse record (W-L-T format)
                record = records[team_id]
                parts = record.split('-')
                team['wins'] = int(parts[0]) if len(parts) > 0 else 0
                team['losses'] = int(parts[1]) if len(parts) > 1 else 0
                team['ties'] = int(parts[2]) if len(parts) > 2 else 0
                team['record_summary'] = record
                
                # Add poll rankings
                team['poll_ranks'] = poll_ranks.get(team_id, [])
                team['is_ranked'] = True
            else:
                team['is_ranked'] = False
    
    return standings
```

---

## Benefits

### For Users
- ✅ See actual records for top hockey teams
- ✅ Understand team quality (ranked vs unranked)
- ✅ Access to official polls (AP, Coaches, USA Hockey, USCHO)
- ✅ Compare rankings across different polls
- ✅ Track ranking changes week-to-week

### For App
- ✅ Solves hockey record data problem
- ✅ Adds valuable feature across ALL NCAA sports
- ✅ Differentiates from other score apps
- ✅ Uses existing ESPN API (no new dependencies)
- ✅ Fast (single API call per sport)

### Data Quality
- ✅ Official poll data (authoritative)
- ✅ Updated weekly during season
- ✅ Includes all major polls
- ✅ Complete team records
- ✅ Historical movement data

---

## Testing Commands

```bash
# Football (4 polls)
curl -s "https://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings" | python -m json.tool

# Men's Basketball (2 polls)
curl -s "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/rankings" | python -m json.tool

# Women's Basketball (2 polls)
curl -s "https://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/rankings" | python -m json.tool

# Men's Hockey (2 polls)
curl -s "https://site.api.espn.com/apis/site/v2/sports/hockey/mens-college-hockey/rankings" | python -m json.tool

# Women's Hockey (2 polls)
curl -s "https://site.api.espn.com/apis/site/v2/sports/hockey/womens-college-hockey/rankings" | python -m json.tool
```

---

## Summary

ESPN provides **excellent poll/ranking data** for all NCAA sports with:
- ✅ Multiple polls per sport
- ✅ **Complete team records** (including hockey!)
- ✅ Ranking movement tracking
- ✅ Poll points/votes
- ✅ Weekly updates
- ✅ **Wisconsin women's hockey IS present** (#1 ranked!)

**This solves the hockey record problem** and adds a valuable feature across all college sports!
