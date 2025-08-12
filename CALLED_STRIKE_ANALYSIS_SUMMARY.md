# Called Strike Zone Analysis Summary

## Executive Summary
Analysis of 786 called strikes from MLB games on August 9, 2025, reveals umpire strike zone patterns and tendencies. The data was extracted from 16 games using ESPN's play-by-play API and processed to examine the spatial distribution of called strikes.

## Data Overview
- **Total Called Strikes Analyzed**: 786
- **Games Included**: 16 MLB games from August 9, 2025
- **Total Pitches in Dataset**: 4,882
- **Called Strike Rate**: 16.1% of all pitches

### Games Analyzed
- ARI vs COL, ATL vs MIA (2 games), BAL vs ATH, CHW vs CLE
- DET vs LAA, LAD vs TOR, MIL vs NYM, MIN vs KC, NYY vs HOU  
- PIT vs CIN, SD vs BOS, SEA vs TB, SF vs WSH, STL vs CHC, TEX vs PHI

## Coordinate System Analysis

### Horizontal Distribution (X-Axis)
- **Range**: 78.0 to 156.0
- **Mean**: 115.30
- **Median**: 115.00
- **Standard Deviation**: 19.20

### Vertical Distribution (Y-Axis)  
- **Range**: 105.0 to 207.0
- **Mean**: 172.76
- **Median**: 174.00
- **Standard Deviation**: 15.08

## Strike Zone Classification Results

### Horizontal Zones
- **Way Inside (X < 50)**: 0 calls (0.0%)
- **Inside Expansion (50 ≤ X < 100)**: 214 calls (27.2%)
- **True Strike Zone (100 ≤ X ≤ 155)**: 570 calls (72.5%)
- **Outside Expansion (155 < X ≤ 205)**: 2 calls (0.3%)
- **Way Outside (X > 205)**: 0 calls (0.0%)

### Vertical Zones
- **High (Y < 80)**: 0 calls (0.0%)
- **Strike Zone (80 ≤ Y ≤ 200)**: 779 calls (99.1%)
- **Low (Y > 200)**: 7 calls (0.9%)

### Combined Strike Zone Analysis
- **True Strike Zone (both X and Y within official bounds)**: 563 calls (71.6%)
- **Zone Expansion Calls**: 223 calls (28.4%)

## Key Findings

### 1. Horizontal Bias Patterns
- **Heavy center-left preference**: 72.5% of called strikes fall within the established horizontal strike zone
- **Significant inside expansion**: 27.2% of calls favor the inside part of the plate
- **Minimal outside expansion**: Only 0.3% of calls extend beyond the outer edge
- **No extreme calls**: Zero calls in "way inside" or "way outside" zones

### 2. Vertical Consistency
- **Excellent vertical control**: 99.1% of called strikes within the vertical strike zone
- **No high strikes**: Zero calls above the traditional strike zone
- **Minimal low expansion**: Only 0.9% of calls below the zone

### 3. Umpire Strike Zone Characteristics
- **Conservative approach**: Umpires avoid calling borderline high/low pitches as strikes
- **Inside preference**: Strong tendency to expand the zone toward batters
- **Consistent boundaries**: Very few calls outside established coordinate ranges

## Important Limitations and Accuracy Considerations

### What the "72.5%" Figure Represents
The 72.5% figure indicates that **72.5% of called strikes fall within the horizontal coordinate range of 100-155** on ESPN's coordinate system. This does NOT represent:

- ✗ Accuracy compared to the official MLB rulebook strike zone
- ✗ Comparison to a verified "ground truth" strike zone
- ✗ Validation against ball-tracking technology (Statcast, etc.)
- ✗ Assessment of correct vs. incorrect calls

### Source of Truth Limitations
**No independent verification source used**. The analysis relies entirely on:
- ESPN's proprietary coordinate system
- ESPN's classification of pitches as "called strikes"
- Coordinate ranges derived from data observation, not official specifications

### What We Cannot Conclude
- **Umpire accuracy**: We cannot determine if these calls were "correct"
- **Rule compliance**: No comparison to official MLB strike zone dimensions
- **Technology validation**: No cross-reference with Statcast or other tracking systems
- **Consistency metrics**: No baseline for what constitutes "good" umpiring

## Recommended Next Steps for Validation

### 1. Cross-Reference Sources
- Compare with official MLB Statcast data
- Validate coordinate system against known strike zone dimensions
- Cross-check with other data providers (FanGraphs, Baseball Savant)

### 2. Establish Ground Truth
- Map ESPN coordinates to official strike zone specifications
- Account for batter height variations in strike zone boundaries
- Incorporate pitch tracking technology data

### 3. Expanded Analysis
- Compare called strikes vs. called balls in borderline zones
- Analyze consistency across different umpires
- Examine game situation factors (count, inning, score)

## Technical Notes
- **Data Source**: ESPN Play-by-Play API
- **Processing Tool**: `analyze_called_strikes_simple.py`
- **Output Files**: `called_strikes_coordinates.csv` (77KB), `called_strikes_analysis.json`
- **Coordinate System**: ESPN proprietary (origin and scale unknown)

## Conclusion
This analysis provides insights into umpire calling patterns within ESPN's data ecosystem but cannot validate the accuracy of strike calls without additional reference sources. The 72.5% figure represents spatial distribution within an assumed strike zone, not verified accuracy against official standards.

---
*Analysis generated on August 12, 2025*
*Data from August 9, 2025 MLB games*
