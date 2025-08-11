# ESPN API Data Reference - Complete Field Guide

This comprehensive reference shows all available data fields from the ESPN API for both MLB and NFL, with examples of how they're currently used and what additional enhancements are possible.

## 🏈 NFL Data Structure Reference

### Game-Level Data
```json
{
  "id": "401776564",
  "name": "Miami Dolphins at Chicago Bears",
  "status": "Final",
  "clock": "0:00 - Final"
}
```

### Drives Structure
```json
{
  "drives": {
    "current": { /* Active drive if game in progress */ },
    "previous": [ /* Array of completed drives */ ]
  }
}
```

### Individual Drive Data
```json
{
  "id": "drive_id",
  "description": "9 plays, 64 yards, 1:35",
  "team": {
    "id": "2",
    "displayName": "Buffalo Bills",
    "abbreviation": "BUF"
  },
  "start": {
    "period": {"number": 4},
    "clock": {"displayValue": "2:11"},
    "yardLine": 35,
    "text": "BUF 35"
  },
  "end": {
    "period": {"number": 4},
    "clock": {"displayValue": "0:36"},
    "yardLine": 99,
    "text": "NYG 1"
  },
  "yards": 64,
  "offensivePlays": 9,
  "result": "DOWNS",
  "plays": [ /* Array of individual plays */ ]
}
```

### Individual NFL Play Data
```json
{
  "id": "play_id",
  "sequenceNumber": "431200",
  "type": {
    "id": "24",
    "text": "Pass Reception",
    "abbreviation": "REC"
  },
  "text": "T.Bagent pass complete to receiver for 8 yards",
  "awayScore": 34,
  "homeScore": 25,
  "period": {"number": 4},
  "clock": {"displayValue": "2:11"},
  "scoringPlay": false,
  "priority": false,
  "modified": "2025-08-09T20:23Z",
  "wallclock": "2025-08-09T20:07:51Z",
  "start": {
    "down": 1,
    "distance": 10,
    "yardLine": 35,
    "yardsToEndzone": 65,
    "downDistanceText": "1st & 10 at BUF 35",
    "shortDownDistanceText": "1st & 10",
    "possessionText": "BUF 35",
    "team": {"id": "2"}
  },
  "end": {
    "down": 2,
    "distance": 2,
    "yardLine": 43,
    "yardsToEndzone": 57,
    "downDistanceText": "2nd & 2 at BUF 43",
    "shortDownDistanceText": "2nd & 2",
    "possessionText": "BUF 43",
    "team": {"id": "2"}
  },
  "statYardage": 8
}
```

### NFL Data Usage in Our App

#### Currently Used Fields
- `text` - Play description
- `start.down` / `start.distance` - Down and distance
- `start.possessionText` - Field position ("BUF 35")
- `clock.displayValue` - Game clock ("2:11")
- `scoringPlay` - Highlights scoring plays
- `awayScore` / `homeScore` - Current game score

#### **✅ NEW - Enhanced Fields We Now Use**
- `statYardage` - Actual yards gained/lost → **(+8 yards)**
- `start.yardsToEndzone` - Distance to endzone → **RED ZONE** / **GOAL LINE**
- `type.text` - Play type → **PASS:** / **RUSH:** / **SACK:**

#### Available But Unused
- `priority` - Play importance flag
- `modified` / `wallclock` - Timing metadata
- `sequenceNumber` - Play order
- `end.*` fields - Result after play completion
- Detailed team information

## ⚾ MLB Data Structure Reference

### Game-Level Data
```json
{
  "id": "401696675",
  "name": "Kansas City Royals at Minnesota Twins",
  "status": "In Progress",
  "inning": 7,
  "topBottom": "top"
}
```

### Individual MLB Play Data
```json
{
  "id": "play_id",
  "sequenceNumber": 1,
  "type": {
    "id": "pitch_type_id",
    "text": "Ball",
    "abbreviation": "B",
    "slug": "ball"
  },
  "text": "Pitch 1 : Ball 1",
  "awayScore": 0,
  "homeScore": 0,
  "period": {
    "type": "Top",
    "number": 1,
    "displayValue": "1st Inning"
  },
  "scoringPlay": false,
  "scoreValue": 0,
  "team": {"id": "7"},
  "participants": [
    {
      "athlete": {
        "id": "pitcher_id",
        "displayName": "Jose Urena",
        "position": "P"
      }
    },
    {
      "athlete": {
        "id": "batter_id", 
        "displayName": "Mike Yastrzemski",
        "position": "OF"
      }
    }
  ],
  "wallclock": "2025-08-10T17:07:31Z",
  "atBatId": "at_bat_id",
  "batOrder": 1,
  "bats": {
    "displayValue": "Left",
    "abbreviation": "L"
  },
  "atBatPitchNumber": 1,
  "pitchCoordinate": {
    "x": coordinate,
    "y": coordinate
  },
  "pitchType": {
    "id": "pitch_type_id",
    "text": "Four-Seam Fastball",
    "displayName": "Fastball"
  },
  "pitchVelocity": 95,
  "summaryType": "P",
  "pitchCount": {
    "balls": 1,
    "strikes": 0
  },
  "resultCount": {
    "balls": 1,
    "strikes": 0
  },
  "outs": 0
}
```

### MLB Data Usage in Our App

#### Currently Used Fields
- `text` - Play description
- `period.displayValue` - Inning ("1st Inning")
- `period.type` - Top/Bottom of inning
- `scoringPlay` - Highlights scoring plays
- `awayScore` / `homeScore` - Current game score

#### **✅ ALREADY ENHANCED - Pitch Details We Use**
- `pitchVelocity` - Pitch speed → **(95 mph)**
- `pitchType.text` - Pitch type → **(Fastball)**
- Combined display: **"Ball 1 (95 mph Fastball)"**

#### Available But Unused
- `pitchCount` - Current ball/strike count (could show "2-1" format)
- `outs` - Number of outs (could add context)
- `batOrder` - Batting order position
- `participants` - Detailed player information
- `pitchCoordinate` - Strike zone location
- `atBatPitchNumber` - Pitch number in at-bat
- `bats` - Batter handedness (L/R)

## 🚀 Enhancement Opportunities by Category

### NFL - Phase 1 Enhancements ✅ COMPLETED
- [x] Yardage display (`statYardage`)
- [x] Play type labels (`type.text`)
- [x] Situational context (`yardsToEndzone`)
- [x] Visual highlighting

### NFL - Phase 2 Potential Enhancements
- [ ] Player involvement (extract from `text` field)
- [ ] Formation information (if available in future API updates)
- [ ] Penalty details (enhanced parsing of penalty plays)
- [ ] Time between plays (`wallclock` timestamps)
- [ ] Drive efficiency metrics

### MLB - Potential Enhancements
- [ ] Count display: "Ball 1 [2-1]" format using `pitchCount`
- [ ] Outs context: "(2 outs)" using `outs` field
- [ ] Batting order: "Leadoff batter" using `batOrder`
- [ ] Player handedness: "vs LHP" using `bats` and pitcher data
- [ ] Pitch location: Strike zone visualization using `pitchCoordinate`

## 📊 Display Format Comparison

### NFL - Before and After Enhancement
```
BEFORE:
[1st & 10 from CHI 25] T.Bagent pass complete to receiver

AFTER:
[1st & 10 from CHI 25] PASS: (+8 yards) T.Bagent pass complete to receiver
[RED ZONE 3rd & 2 from CHI 18] RUSH: (+1 yard) Running back up the middle
[GOAL LINE 4th & 1 from CHI 3] TOUCHDOWN: Pass complete for touchdown (7-14)
```

### MLB - Current Enhanced Format
```
CURRENT (Already Enhanced):
Pitch 1 : Ball 1 (95 mph Fastball)
Pitch 2 : Strike 1 (88 mph Slider)
Ball 2 (92 mph Changeup)
```

## 🛠️ Implementation Notes

### Data Retrieval Pattern
```python
# This is the proven pattern that works well
nfl_scores = ApiService.get_scores('NFL', datetime.now())
game_id = nfl_scores[0].get('id')
details = ApiService.get_game_details('NFL', game_id)
drives_data = details.get('drives', {})

# For individual plays within drives
for drive in drives_data.get('previous', []):
    for play in drive.get('plays', []):
        yardage = play.get('statYardage', 0)
        yards_to_endzone = play.get('start', {}).get('yardsToEndzone', 0)
        # Process enhanced data...
```

### Performance Considerations
- ESPN API responses are large (27K+ lines for detailed games)
- Only extract needed fields to minimize processing
- Cache frequently accessed data
- Use background loading for non-critical enhancements

### Accessibility Requirements
- All enhancements must work with screen readers
- Use descriptive text instead of symbols/emojis
- Maintain keyboard navigation
- Provide context without visual cues

This reference provides the foundation for any future enhancements while documenting our current successful implementation patterns.
