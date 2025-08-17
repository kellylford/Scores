# Proposal E: English Base Description - Detailed Specification

## 🎯 Overview
Use clear, natural English descriptions for base runner situations that are immediately understandable to all users.

## 📋 Format Specification

### Basic Format Structure
```
Team @ Team (Inning)
Base Runner Description | Count, Outs | At bat: Player Name
Last: Play Description
```

## 🔍 Detailed Examples

### Example 1: Runners on 1st and 2nd
```
Brewers @ Reds (Bot 10th)
Runners on 1st and 2nd | 1-2 count, 2 outs | At bat: E. De La Cruz
Last: Pitch 4 - Strike 2 Foul
```

### Example 2: Bases Loaded
```
Padres @ Dodgers (Bot 1st)
Bases loaded | 3-2 count, 2 outs | At bat: M. Conforto
Last: Ball 4 - Walk loads the bases
```

### Example 3: Scoring Position
```
Tigers @ Twins (Bot 7th)
Runners on 2nd and 3rd | 2-1 count, 1 out | At bat: B. Lee
Last: Double to left field, runner advances
```

### Example 4: Single Runner Variations
```
Orioles @ Astros (Top 9th)
Runner on 3rd | 2-2 count, 2 outs | At bat: D. Carlson
Last: Single to center field
```

```
White Sox @ Royals (Top 8th)
Runner on 2nd | 1-2 count, 2 outs | At bat: L. Robert Jr.
Last: Stolen base, runner advances to 2nd
```

```
Yankees @ Cardinals (Top 7th)
Runner on 1st | 0-0 count, 0 outs | At bat: R. McMahon
Last: Walk, runner takes first base
```

### Example 5: Bases Empty
```
Diamondbacks @ Rockies (Bot 5th)
Bases empty | 0-0 count, 1 out | At bat: M. Moniak
Last: Ground out to shortstop
```

## 📏 Complete Rule Set

### Base Runner Descriptions
| Situation | Description |
|-----------|-------------|
| No runners | "Bases empty" |
| Runner on 1st only | "Runner on 1st" |
| Runner on 2nd only | "Runner on 2nd" |
| Runner on 3rd only | "Runner on 3rd" |
| Runners on 1st and 2nd | "Runners on 1st and 2nd" |
| Runners on 1st and 3rd | "Runners on 1st and 3rd" |
| Runners on 2nd and 3rd | "Runners on 2nd and 3rd" |
| All three bases | "Bases loaded" |

### Special Context Descriptions (Optional Enhancement)
| Situation | Enhanced Description |
|-----------|---------------------|
| Runner(s) on 2nd and/or 3rd | "Scoring position" (alternative) |
| Bases loaded | "Bases loaded" |
| Two runners in scoring position | "Runners on 2nd and 3rd" |

## 🎨 Visual Layout Examples

### Compact Layout (Current Style)
```
Brewers @ Reds (Bot 10th) | Runners on 1st and 2nd | 1-2, 2 outs
At bat: E. De La Cruz | Last: Strike 2 Foul
```

### Two-Line Layout (Expanded)
```
Brewers @ Reds (Bot 10th)
Runners on 1st and 2nd | 1-2 count, 2 outs | At bat: E. De La Cruz
Last: Pitch 4 - Strike 2 Foul
```

### Three-Line Layout (Maximum Detail)
```
Brewers @ Reds (Bot 10th)
Runners on 1st and 2nd | 1-2 count, 2 outs
At bat: E. De La Cruz | Pitching: T. Megill | Last: Strike 2 Foul
```

## 🔧 Implementation Details

### ESPN API Data Mapping
```python
def get_base_runner_description(situation):
    """Convert ESPN situation data to English description"""
    
    on_first = situation.get('onFirst', False)
    on_second = situation.get('onSecond', False)
    on_third = situation.get('onThird', False)
    
    # Count runners
    runner_count = sum([on_first, on_second, on_third])
    
    if runner_count == 0:
        return "Bases empty"
    elif runner_count == 3:
        return "Bases loaded"
    elif runner_count == 1:
        if on_first:
            return "Runner on 1st"
        elif on_second:
            return "Runner on 2nd"
        elif on_third:
            return "Runner on 3rd"
    elif runner_count == 2:
        if on_first and on_second:
            return "Runners on 1st and 2nd"
        elif on_first and on_third:
            return "Runners on 1st and 3rd"
        elif on_second and on_third:
            return "Runners on 2nd and 3rd"
    
    return "Unknown base situation"
```

### Count Description
```python
def get_count_description(situation):
    """Format count information"""
    balls = situation.get('balls', 0)
    strikes = situation.get('strikes', 0)
    outs = situation.get('outs', 0)
    
    return f"{balls}-{strikes} count, {outs} out{'s' if outs != 1 else ''}"
```

### Complete Baseball Format Function
```python
def format_baseball_enhanced_display(game_data):
    """Generate enhanced baseball display with base runners"""
    
    # Extract basic game info
    game_name = game_data.get('name', 'Unknown Game')
    status = game_data.get('status', 'Unknown')
    
    # Get situation data from competitions
    situation = None
    for comp in game_data.get('competitions', []):
        if 'situation' in comp:
            situation = comp['situation']
            break
    
    if not situation:
        return f"{game_name} ({status})"
    
    # Build enhanced display
    base_description = get_base_runner_description(situation)
    count_description = get_count_description(situation)
    
    # Current batter
    batter = situation.get('batter', {}).get('athlete', {})
    batter_name = batter.get('displayName', 'Unknown') if batter else 'Unknown'
    
    # Last play
    last_play = situation.get('lastPlay', {})
    last_play_text = last_play.get('text', 'No recent play') if last_play else 'No recent play'
    
    # Format lines
    line1 = f"{game_name} ({status})"
    line2 = f"{base_description} | {count_description} | At bat: {batter_name}"
    line3 = f"Last: {last_play_text}"
    
    return f"{line1}\n{line2}\n{line3}"
```

## 📊 Space Usage Analysis

### Character Count Examples
| Situation | Characters | Space Efficiency |
|-----------|------------|------------------|
| "Bases empty" | 11 | ⭐⭐⭐⭐⭐ |
| "Runner on 1st" | 13 | ⭐⭐⭐⭐⭐ |
| "Runners on 1st and 2nd" | 22 | ⭐⭐⭐⭐ |
| "Runners on 2nd and 3rd" | 22 | ⭐⭐⭐⭐ |
| "Bases loaded" | 12 | ⭐⭐⭐⭐⭐ |

## ♿ Accessibility Features

### Screen Reader Compatibility
- Uses natural language that screen readers pronounce correctly
- Clear sentence structure
- No special characters that might confuse assistive technology

### High Contrast Support
- Pure text-based, no color dependencies
- Works with high contrast themes
- Readable in all display modes

## 🎯 Integration with Current System

### Football vs Baseball Format Comparison

**Current Football:**
```
Chiefs vs Ravens (4th 2:15)
3rd & 8 at KC 42 | TD 7pts Chiefs: 8 plays, 75 yards, 4:23
Last: Mahomes pass complete to Kelce for 12 yards
```

**Enhanced Baseball (Proposal E):**
```
Brewers @ Reds (Bot 10th)
Runners on 1st and 2nd | 1-2 count, 2 outs | At bat: E. De La Cruz
Last: Pitch 4 - Strike 2 Foul
```

### Consistency Benefits
- Same three-line structure as football
- Similar information density
- Familiar format for existing users
- Natural language maintains readability

## 🚀 Implementation Priority

### Phase 1: Basic Implementation
- Add base runner descriptions
- Include count and outs
- Show current batter

### Phase 2: Enhanced Details
- Add pitcher information
- Include more detailed last play descriptions
- Add batting statistics

### Phase 3: Smart Enhancements
- Highlight high-leverage situations
- Add contextual information
- Include inning importance indicators

**Proposal E provides the most accessible and immediately understandable enhancement to baseball live scores while maintaining consistency with the current football format.**
