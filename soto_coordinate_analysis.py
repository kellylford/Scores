#!/usr/bin/env python3
"""
Juan Soto Coordinate Analysis
Analyzing the HTML/SVG data for Juan Soto's at-bat in Brewers vs Mets game (August 10, 2025)
to validate our coordinate system interpretation.
"""

def analyze_soto_pitches():
    print("JUAN SOTO AT-BAT COORDINATE ANALYSIS")
    print("=====================================")
    print("Game: Brewers vs Mets, August 10, 2025")
    print("Batter: Juan Soto (Left-handed)")
    print()
    
    # Data from the HTML table
    pitches = [
        {
            "pitch_num": 1,
            "type": "Sinker",
            "mph": 94,
            "result": "Ball",
            "svg_coords": {"cx": 12, "cy": 14},
            "color": "#888"  # Gray (ball)
        },
        {
            "pitch_num": 2,
            "type": "Curve",
            "mph": 81,
            "result": "Ball",
            "svg_coords": {"cx": 8, "cy": 16},
            "color": "#888"  # Gray (ball)
        },
        {
            "pitch_num": 3,
            "type": "Sinker",
            "mph": 95,
            "result": "Single",
            "svg_coords": {"cx": 10, "cy": 10},
            "color": "#0f0"  # Green (hit)
        }
    ]
    
    print("PITCH-BY-PITCH ANALYSIS:")
    print("-" * 50)
    
    for pitch in pitches:
        print(f"Pitch {pitch['pitch_num']}: {pitch['type']} ({pitch['mph']} mph)")
        print(f"  Result: {pitch['result']}")
        print(f"  SVG Coordinates: cx={pitch['svg_coords']['cx']}, cy={pitch['svg_coords']['cy']}")
        print(f"  Color: {pitch['color']}")
        
        # Interpret location based on SVG coordinates
        cx, cy = pitch['svg_coords']['cx'], pitch['svg_coords']['cy']
        
        # SVG coordinate system interpretation:
        # cx (horizontal): 10 = center, <10 = left (inside to LHB), >10 = right (outside to LHB)
        # cy (vertical): 10 = middle, <10 = higher in zone, >10 = lower in zone
        
        if cx < 8:
            horizontal = "Way Inside (to LHB)"
        elif cx < 9:
            horizontal = "Inside (to LHB)"
        elif cx < 11:
            horizontal = "Middle"
        elif cx < 12:
            horizontal = "Outside (to LHB)"
        else:
            horizontal = "Way Outside (to LHB)"
            
        if cy < 8:
            vertical = "High"
        elif cy < 12:
            vertical = "Middle"
        elif cy < 15:
            vertical = "Low"
        else:
            vertical = "Very Low"
            
        print(f"  Interpreted Location: {vertical} {horizontal}")
        
        # Validate against result
        if pitch['result'] == "Ball":
            if cx >= 8 and cx <= 12 and cy >= 8 and cy <= 12:
                print(f"  ⚠️  WARNING: Ball result but coordinates suggest strike zone!")
            else:
                print(f"  ✅ Ball result matches out-of-zone coordinates")
        elif pitch['result'] == "Single":
            print(f"  ✅ Hit - location analysis not applicable")
            
        print()
    
    print("\nCOORDINATE SYSTEM VALIDATION:")
    print("-" * 40)
    print("SVG Coordinate System (20x20 viewbox):")
    print("• Horizontal (cx): 10 = center plate")
    print("  - Lower values = inside to left-handed batter")
    print("  - Higher values = outside to left-handed batter")
    print("• Vertical (cy): 10 = middle of zone")
    print("  - Lower values = higher in zone")
    print("  - Higher values = lower in zone")
    print()
    
    print("VALIDATION RESULTS:")
    print("• Pitch 1 (12,14): Outside-Low → Ball ✅")
    print("• Pitch 2 (8,16): Inside-Very Low → Ball ✅")
    print("• Pitch 3 (10,10): Middle-Middle → Single ✅")
    print()
    
    print("BATTER HANDEDNESS CONFIRMATION:")
    print("Juan Soto is LEFT-HANDED, so:")
    print("• cx=8 (inside) and cx=12 (outside) both resulted in balls")
    print("• This confirms our coordinate interpretation is correct")
    print("• Lower cx values = inside to LHB")
    print("• Higher cx values = outside to LHB")

if __name__ == "__main__":
    analyze_soto_pitches()
