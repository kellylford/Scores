

Made changes.

# MLB Pitch Coordinate Analysis - ESPN API

## Overview
The ESPN API provides rich pitch coordinate data for MLB games, including exact strike zone locations for every pitch. This opens up exciting possibilities for enhanced accessibility and analysis.

## Available Data Points

### Pitch Coordinates
- **Format**: `pitchCoordinate: {x: number, y: number}`
- **Coordinate System**: Appears to use a pixel-based system
- **Range Found**: X: 15-221 (206 pixel range), Y: 103-252 (149 pixel range)

### Associated Pitch Data
For each pitch with coordinates, we also get:
- `pitchVelocity`: Speed in mph
- `pitchType.text`: Pitch type (Four-seam FB, Slider, Changeup, etc.)
- `pitchCount`: Current ball/strike count
- `summaryType`: Result (Ball, Strike, Foul, etc.)
- `type.text`: Detailed result description

## Strike Zone Mapping Analysis - VALIDATED ✅

Based on coordinate analysis of 276 actual pitches including 48 called strikes and 89 called balls:

### Validation Results
- **85.4%** of called strikes captured by our strike zone boundaries
- **96.6%** of called balls correctly excluded from strike zone
- **Highly Accurate**: Only 7 called strikes fell outside our zone, only 3 called balls inside

### Refined Strike Zone Boundaries
```
Outside (X < 85)     |  Strike Zone (85-145)   |  Outside (X > 145)
                     |                         |
               High Zone (Y > 195)             |
                     |                         |
            Middle Zone (150-195)              |
                     |                         |
               Low Zone (Y < 150)              |
```

### Coordinate Validation Data
- **Called Strikes Range**: X: 83-150, Y: 148-197
- **Called Balls Range**: X: 15-221, Y: 103-252
- **Total Coordinate Range**: X: 15-221 (206 pixels), Y: 103-252 (149 pixels)

### Location Categories We Could Implement ✅ VALIDATED
1. **STRIKE ZONE CENTER** (85-145 X, 150-195 Y) - 85.4% accuracy for called strikes
2. **HIGH STRIKE ZONE** (85-145 X, Y > 195)
3. **LOW STRIKE ZONE** (85-145 X, Y < 150)
4. **INSIDE** (X < 85)
5. **OUTSIDE** (X > 145)
6. **WAY INSIDE** (X < 50)
7. **WAY OUTSIDE** (X > 175)
8. **HIGH AND OUTSIDE** (X > 145, Y > 195)
9. **LOW AND INSIDE** (X < 85, Y < 150)

## Enhancement Possibilities

### 1. Basic Location Context (IMMEDIATE IMPLEMENTATION)
Add location information to our existing pitch display:

**Current:**
```
Pitch 1: Ball 1 (93 mph Four-seam FB)
```

**Enhanced:**
```
Pitch 1: Ball 1 (93 mph Four-seam FB) - Outside
Pitch 2: Strike 1 (85 mph Slider) - Low Strike Zone
Pitch 3: Foul Ball (79 mph Curve) - Strike Zone Center
```

### 2. Pitch Pattern Analysis (ADVANCED)
- **Corner Worker**: "Pitcher working the corners (3 outside, 2 low)"
- **Zone Attack**: "Attacking the strike zone (4 of 5 pitches in zone)"
- **Setup Patterns**: "Setting up with fastballs outside, then slider inside"

### 3. Accessible "Pitch Plot" (TEXT-BASED)
```
AT-BAT SUMMARY - Batter vs Pitcher
Pitch 1: [OUTSIDE    ] 93mph Fastball (Ball)
Pitch 2: [ CENTER    ] 85mph Slider (Strike Looking)  
Pitch 3: [LOW ZONE   ] 79mph Curve (Foul)
Pitch 4: [WAY OUTSIDE] 94mph Fastball (Ball)
Result: Walk
```

### 4. Count-Based Location Analysis
- **Ahead in Count**: "Pitcher working outside with 0-2 count"
- **Behind in Count**: "Must throw strikes - fastball down the middle"
- **Even Counts**: "Competitive pitch on the edge"

## Pitch Type Distribution (From Sample Game)
```
Four-seam FB: 118 pitches (42.8%)
Slider: 71 pitches (25.7%)
Changeup: 25 pitches (9.1%)
Sinker: 22 pitches (8.0%)
Curve: 16 pitches (5.8%)
Cutter: 11 pitches (4.0%)
Sweeper: 7 pitches (2.5%)
Splitter: 6 pitches (2.2%)
```

## Implementation Strategy


Made changes.



### Phase 1: Basic Location Context ✅ RECOMMENDED
Add simple location descriptions to existing pitch display:
- Minimal code changes to current system
- Immediate value for users
- Screen reader friendly
- Builds on our existing successful pitch enhancement

### Phase 2: Pattern Recognition
- Identify common pitching patterns
- Provide strategic context
- "Pitcher establishing the outside corner"

### Phase 3: Advanced Analysis
- At-bat summaries with pitch locations
- Pitcher tendencies by count
- Comparative analysis between pitchers

## Accessibility Considerations

### ✅ Advantages
- **Rich Context**: Location adds significant strategic understanding
- **Screen Reader Compatible**: Text-based descriptions work perfectly
- **Pattern Recognition**: Helps users understand pitching strategy
- **Educational Value**: Teaches strike zone awareness

### ⚠️ Considerations
- **Information Density**: Must balance detail with overwhelming users
- **Coordinate Accuracy**: Strike zone boundaries may need refinement
- **Consistency**: Coordinate system might vary by stadium/camera angle

## Sample Implementation Code ✅ IMPLEMENTED & VALIDATED
```python
def get_pitch_location(x: int, y: int) -> str:
    """Convert pitch coordinates to accessible location description.
    
    Boundaries validated against actual called strikes/balls:
    - 85.4% of called strikes captured in strike zone
    - 96.6% of called balls correctly excluded
    - Based on analysis of 48 called strikes and 89 called balls
    """
    if x is None or y is None:
        return ""
    
    # Refined strike zone mapping based on ESPN API coordinate validation
    if 85 <= x <= 145:  # Refined strike zone width
        if y > 195:
            return "High Strike Zone"
        elif y < 150:
            return "Low Strike Zone" 
        else:
            return "Strike Zone Center"
    elif x < 85:
        return "Way Inside" if x < 50 else "Inside"
    else:
        return "Way Outside" if x > 175 else "Outside"

# Usage in existing pitch display
location = get_pitch_location(coord['x'], coord['y'])
display_text = f"Pitch {num}: {result} ({velocity} mph {pitch_type}) - {location}"
```

## Expected User Impact

### For Screen Reader Users
- **Strategic Understanding**: "Now I understand why that was ball 4 - it was way outside"
- **Pattern Recognition**: "The pitcher is working the corners, trying to get the batter to chase"
- **Game Flow**: "With 2 strikes, the pitcher can waste a pitch outside"

### For All Users
- **Enhanced Context**: Location adds dimension to every pitch
- **Educational Value**: Learn about pitching strategy and strike zone
- **Pattern Awareness**: Recognize when pitchers are setting up batters

## Recommendation: IMPLEMENT PHASE 1

The pitch coordinate data is rich and reliable. Adding basic location context to our existing pitch display would:

1. **Build on Success**: Our current pitch enhancement is already working well
2. **Add Immediate Value**: Location context significantly enhances understanding
3. **Maintain Accessibility**: Text-based approach fits our design philosophy
4. **Require Minimal Changes**: Can integrate into existing pitch display logic

This would make our MLB pitch display even more comprehensive and valuable for understanding the strategic aspects of each at-bat.
