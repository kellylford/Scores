# Baseball Strike Zone Coordinate System

## Overview

The ESPN API provides pitch location data as x-y coordinates representing where each pitch crosses the plate. This document explains the coordinate system, ranges, and how they map to descriptive locations in the Scores application.

## Coordinate System

### Origin and Orientation
- **Origin**: The coordinate system appears to be based on the catcher's perspective
- **X-axis**: **IMPORTANT**: ESPN's "x" coordinate represents **vertical position (height)**
- **Y-axis**: **IMPORTANT**: ESPN's "y" coordinate represents **horizontal position (left-right)**
- **Units**: Coordinate units are in an ESPN-specific scale (not inches or feet)

**Note**: ESPN's coordinate system is swapped from traditional x-y conventions. In our application, we swap them back to display as (horizontal, vertical) for clarity.

### Coordinate Ranges

#### Horizontal Position (ESPN's "y" coordinate)
- **Range**: Approximately 0-250+ (observed values)
- **Strike Zone Width**: 80-140 (60-unit width)
- **Left-handed batter box**: < 50
- **Inside edge**: 50-80
- **Strike zone**: 80-140
- **Outside edge**: 140-170
- **Right-handed batter box**: > 170

#### Vertical Position (ESPN's "x" coordinate)
- **Range**: Approximately 50-300+ (observed values)
- **Low Strike Zone**: < 150
- **Strike Zone Center**: 150-200
- **High Strike Zone**: > 200

## Location Mappings

The `get_pitch_location()` function maps coordinates to these descriptive locations:

### Strike Zone Locations
| ESPN Coordinates | Our Display | Description |
|------------------|-------------|-------------|
| x: 150-200, y: 80-140 | (80-140, 150-200) | "Strike Zone Center" |
| x: > 200, y: 80-140 | (80-140, >200) | "High Strike Zone" |
| x: < 150, y: 80-140 | (80-140, <150) | "Low Strike Zone" |

### Outside Strike Zone
| ESPN Coordinates | Our Display | Description |
|------------------|-------------|-------------|
| x: any, y: < 50 | (<50, any) | "Way Inside" |
| x: any, y: 50-80 | (50-80, any) | "Inside" |
| x: any, y: 140-170 | (140-170, any) | "Outside" |
| x: any, y: > 170 | (>170, any) | "Way Outside" |

## Example Coordinates

### Typical Strike Zone Pitches
- **Center-Center**: ESPN {x: 175, y: 110} → Our display (110, 175) → "Strike Zone Center"
- **High Strike**: ESPN {x: 210, y: 110} → Our display (110, 210) → "High Strike Zone"  
- **Low Strike**: ESPN {x: 140, y: 110} → Our display (110, 140) → "Low Strike Zone"

### Balls Outside Zone
- **Inside Corner**: ESPN {x: 175, y: 70} → Our display (70, 175) → "Inside"
- **Outside Corner**: ESPN {x: 175, y: 150} → Our display (150, 175) → "Outside"
- **Way Inside**: ESPN {x: 175, y: 40} → Our display (40, 175) → "Way Inside"
- **Way Outside**: ESPN {x: 175, y: 180} → Our display (180, 175) → "Way Outside"

### Your Example Case
- **Low and Outside**: ESPN {x: 90, y: 223} → Our display (223, 90) → "Way Outside" (since 90 < 150 = low, 223 > 170 = way outside)

## Display Format

In the application, pitches are displayed with both descriptive location and precise coordinates:

```
Ball 1 (95 mph Fastball) - Strike Zone Center (110, 175)
Strike 1 (88 mph Slider) - Low and Outside (150, 140)
Ball 2 (92 mph Changeup) - Way Inside (40, 180)
```

## Technical Implementation

### Data Source
- Coordinates come from ESPN API `pitchCoordinate` object
- Format: `{"x": 110, "y": 175}`
- Available for most MLB pitch data

### Code Location
- Mapping function: `get_pitch_location(x, y)` in `scores.py`
- Display logic: `_add_baseball_plays_to_tree_group()` function
- Enhanced display includes both description and raw coordinates

## Notes and Limitations

### Data Availability
- Not all pitches have coordinate data
- Older games may have incomplete coordinate information
- Some pitch types may not include location data

### Accuracy Considerations
- Coordinates represent estimated crossing point at home plate
- ESPN's coordinate system may vary slightly between seasons
- Strike zone boundaries are approximate and may not account for batter height

### Customization
- Coordinate boundaries can be adjusted in the `get_pitch_location()` function
- Descriptive text can be modified for different accessibility needs
- Additional location granularity can be added by subdividing coordinate ranges

## Future Enhancements

Potential improvements to the coordinate system:

1. **Batter-Specific Strike Zones**: Adjust Y-axis boundaries based on batter height
2. **Heat Maps**: Visual representation of pitch locations over time
3. **Spin Rate Integration**: Combine location with spin data for enhanced analysis
4. **Pitcher Tendencies**: Track coordinate patterns by pitcher or situation
5. **Umpire Analysis**: Compare called strikes/balls to coordinate-based strike zone

## Related Files

- `scores.py`: Contains `get_pitch_location()` function and display logic
- `espn_api.py`: Handles ESPN API data parsing and coordinate extraction
- `DEVELOPMENT_STATUS_CURRENT.md`: Current project status including coordinate enhancements
