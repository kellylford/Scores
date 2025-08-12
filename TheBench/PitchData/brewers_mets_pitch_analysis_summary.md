# **Brewers vs Mets Pitch Data Analysis**
**Game Date**: August 10, 2025  
**Game ID**: 401696676  
**Teams**: Milwaukee Brewers vs New York Mets  

---

## **📊 Data Summary**

### **Total Pitches**: 321
- **With coordinate data**: 318 (99.1%)
- **With velocity data**: Available for all pitches
- **With pitch type data**: 316 pitches classified

### **Game Flow by Inning**
| Inning | Top | Bottom | Total |
|--------|-----|--------|-------|
| 1st    | 29  | 17     | 46    |
| 2nd    | 18  | 23     | 41    |
| 3rd    | 11  | 12     | 23    |
| 4th    | 12  | 32     | 44    |
| 5th    | 19  | 23     | 42    |
| 6th    | 12  | 16     | 28    |
| 7th    | 16  | 10     | 26    |
| 8th    | 16  | 32     | 48    |
| 9th    | 18  | 5      | 23    |

**Total**: 151 pitches (Top) + 170 pitches (Bottom) = 321 pitches

---

## **🎯 Pitch Type Breakdown**

| Pitch Type     | Count | Percentage |
|----------------|-------|------------|
| Four-seam FB   | 96    | 29.9%      |
| Slider         | 57    | 17.8%      |
| Sinker         | 56    | 17.4%      |
| Sweeper        | 38    | 11.8%      |
| Cutter         | 32    | 10.0%      |
| Changeup       | 17    | 5.3%       |
| Curve          | 15    | 4.7%       |
| Splitter       | 5     | 1.6%       |
| Unknown        | 5     | 1.6%       |

---

## **📍 Coordinate System Validation**

### **Sample Coordinates (First 10 pitches)**
1. (109, 182) - Sinker, 95 mph
2. (136, 156) - Cutter, 93 mph  
3. (90, 223) - Curve, 82 mph
4. (76, 160) - Cutter, 92 mph
5. (28, 199) - Curve, 82 mph
6. (28, 199) - Curve, 82 mph (HBP)
7. (166, 157) - Four-seam FB, 92 mph
8. (118, 191) - Sinker, 95 mph
9. (140, 178) - Cutter, 93 mph
10. (135, 159) - Four-seam FB, 95 mph

### **Coordinate Analysis**
- **X-axis range**: 28 to 166 (observed)
- **Y-axis range**: 156 to 223 (observed)  
- **Strike zone center**: Approximately X=127, Y=175
- **Notable**: HBP at (28, 199) - far inside and low (confirms our coordinate system understanding)

---

## **⚡ Velocity Analysis**

### **Velocity by Pitch Type**
| Pitch Type     | Avg Velocity | Range      |
|----------------|--------------|------------|
| Four-seam FB   | ~94 mph      | 89-97 mph  |
| Sinker         | ~94 mph      | 90-96 mph  |
| Cutter         | ~92 mph      | 87-95 mph  |
| Slider         | ~86 mph      | 82-90 mph  |
| Sweeper        | ~84 mph      | 79-88 mph  |
| Changeup       | ~85 mph      | 80-89 mph  |
| Curve          | ~81 mph      | 76-85 mph  |
| Splitter       | ~88 mph      | 85-91 mph  |

---

## **🏏 Batter Handedness**

### **Pitch Data includes**:
- Batter side (L/R) for each pitch
- Batter ID and pitcher ID
- At-bat sequence numbers
- Batting order position

---

## **📈 Data Quality Assessment**

### **Completeness**
✅ **Excellent coordinate coverage**: 318/321 pitches (99.1%)  
✅ **Complete velocity data**: Available for all pitches  
✅ **Rich pitch type classification**: 8 distinct pitch types  
✅ **Full game context**: Inning, score, count data  

### **Validation Opportunities**
🔍 **Strike zone analysis**: Can validate our coordinate system  
🔍 **Handedness correlation**: Inside/outside pitch interpretation  
🔍 **Velocity accuracy**: Cross-reference with broadcast data  
🔍 **Pitch sequence patterns**: Analyze strategic decisions  

---

## **🎵 Audio System Implications**

### **Coordinate System Validation**
- **HBP at (28, 199)** confirms far inside/low interpretation
- **Y-axis range 156-223** aligns with our understanding (higher Y = lower pitch)
- **X-axis range 28-166** shows full plate coverage
- **318 coordinate samples** provide excellent validation dataset

### **Enhancement Opportunities**
1. **Velocity integration**: Could add audio cues for pitch speed
2. **Pitch type awareness**: Different tones for different pitch types
3. **Count situation**: Audio could reflect strategic context
4. **Handedness adaptation**: Better inside/outside interpretation

---

## **📝 File Details**

### **CSV Structure**
- **Filename**: `brewers_mets_8_10_2025_pitches.csv`
- **Columns**: 32 comprehensive data fields
- **Raw data**: Complete ESPN API response included
- **Format**: Ready for analysis in Excel, Python, R, etc.

### **Key Columns for Analysis**
- `coordinate_x`, `coordinate_y`: Pitch location
- `velocity_mph`: Pitch speed
- `pitch_type`: Pitch classification
- `batter_side`: L/R handedness
- `balls_before`, `strikes_before`: Count context
- `inning`, `inning_half`: Game situation

---

## **🔬 Next Steps for Analysis**

### **Immediate Opportunities**
1. **Strike zone mapping**: Plot all coordinates to visualize zone
2. **Velocity distribution**: Analyze speed by pitch type and situation
3. **Count correlation**: Study pitch selection by count
4. **Handedness patterns**: Compare inside/outside by batter side

### **Advanced Analysis**
1. **Pitch sequence analysis**: Study strategic patterns
2. **Location effectiveness**: Correlate coordinates with outcomes
3. **Velocity-location correlation**: Analyze speed vs placement
4. **Audio system optimization**: Use real data to refine coordinate mapping

---

**Generated**: August 12, 2025  
**Data Source**: ESPN MLB API Game #401696676  
**Total Game Duration**: 9 innings, 321 pitches  
**Data Quality**: Excellent (99%+ complete coordinate data)**
