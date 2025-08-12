#!/usr/bin/env python3
"""
Corrected analysis to properly identify called strikes vs balls
and validate our strike zone coordinate assumptions.
"""

import json
import os

def corrected_strike_zone_analysis():
    """Properly analyze called strikes vs balls using correct field identification."""
    
    print("=== Corrected Strike Zone Analysis ===")
    print()
    
    game_file = "api_exploration/game_details_401696636.json"
    with open(game_file, 'r') as f:
        data = json.load(f)
    
    plays = data.get('plays', [])
    if not plays:
        drives = data.get('drives', [])
        all_plays = []
        for drive in drives:
            all_plays.extend(drive.get('plays', []))
        plays = all_plays
    
    called_strikes = []
    called_balls = []
    all_pitches = []
    
    for play in plays:
        coord = play.get('pitchCoordinate') or play.get('coordinate')
        if not coord:
            continue
            
        type_text = play.get('type', {}).get('text', '')
        velocity = play.get('pitchVelocity')
        
        # Only look at actual pitches (with velocity)
        if not velocity:
            continue
            
        pitch_info = {
            'x': coord.get('x'),
            'y': coord.get('y'),
            'text': play.get('text', ''),
            'type': type_text,
            'velocity': velocity,
            'pitch_type': play.get('pitchType', {}).get('text', ''),
        }
        
        all_pitches.append(pitch_info)
        
        # Identify called strikes and balls
        if type_text == 'Strike Looking':
            called_strikes.append(pitch_info)
        elif type_text == 'Ball':
            called_balls.append(pitch_info)
    
    print(f"Total pitches with coordinates: {len(all_pitches)}")
    print(f"Called strikes (looking): {len(called_strikes)}")
    print(f"Called balls: {len(called_balls)}")
    
    if called_strikes:
        print(f"\n=== Called Strikes Examples ===")
        for i, strike in enumerate(called_strikes[:5]):
            print(f"  Strike {i+1}: ({strike['x']}, {strike['y']}) - {strike['text']}")
            print(f"    {strike['velocity']} mph {strike['pitch_type']}")
    
    if called_balls:
        print(f"\n=== Called Balls Examples ===")
        for i, ball in enumerate(called_balls[:5]):
            print(f"  Ball {i+1}: ({ball['x']}, {ball['y']}) - {ball['text']}")
            print(f"    {ball['velocity']} mph {ball['pitch_type']}")
    
    # Test our strike zone assumptions
    if called_strikes and called_balls:
        print(f"\n=== Strike Zone Boundary Analysis ===")
        
        # Our current assumptions: 80-140 X, 150-200 Y for strike zone
        strikes_in_zone = 0
        strikes_outside_zone = 0
        balls_in_zone = 0
        balls_outside_zone = 0
        
        for strike in called_strikes:
            x, y = strike['x'], strike['y']
            if 80 <= x <= 140 and 150 <= y <= 200:
                strikes_in_zone += 1
            else:
                strikes_outside_zone += 1
        
        for ball in called_balls:
            x, y = ball['x'], ball['y']
            if 80 <= x <= 140 and 150 <= y <= 200:
                balls_in_zone += 1
            else:
                balls_outside_zone += 1
        
        print(f"Called Strikes in our 'strike zone' (80-140 X, 150-200 Y): {strikes_in_zone}")
        print(f"Called Strikes outside our 'strike zone': {strikes_outside_zone}")
        print(f"Called Balls in our 'strike zone': {balls_in_zone}")
        print(f"Called Balls outside our 'strike zone': {balls_outside_zone}")
        
        if strikes_in_zone + strikes_outside_zone > 0:
            strike_accuracy = (strikes_in_zone / (strikes_in_zone + strikes_outside_zone)) * 100
            print(f"Our strike zone captures {strike_accuracy:.1f}% of called strikes")
        
        if balls_in_zone + balls_outside_zone > 0:
            ball_accuracy = (balls_outside_zone / (balls_in_zone + balls_outside_zone)) * 100
            print(f"Our strike zone correctly excludes {ball_accuracy:.1f}% of called balls")
        
        # Analyze coordinate ranges to refine our boundaries
        print(f"\n=== Coordinate Range Refinement ===")
        
        strike_x = [s['x'] for s in called_strikes]
        strike_y = [s['y'] for s in called_strikes]
        ball_x = [b['x'] for b in called_balls]
        ball_y = [b['y'] for b in called_balls]
        
        print(f"Called Strikes - X range: {min(strike_x)} to {max(strike_x)}")
        print(f"Called Strikes - Y range: {min(strike_y)} to {max(strike_y)}")
        print(f"Called Balls - X range: {min(ball_x)} to {max(ball_x)}")
        print(f"Called Balls - Y range: {min(ball_y)} to {max(ball_y)}")
        
        # Suggest better boundaries
        # Find the range that captures most strikes but few balls
        print(f"\n=== Suggested Strike Zone Boundaries ===")
        
        # Use actual called strike coordinates to suggest boundaries
        strike_x_sorted = sorted(strike_x)
        strike_y_sorted = sorted(strike_y)
        
        # Use middle 80% of called strikes to define core zone
        x_low_idx = int(len(strike_x_sorted) * 0.1)
        x_high_idx = int(len(strike_x_sorted) * 0.9)
        y_low_idx = int(len(strike_y_sorted) * 0.1)
        y_high_idx = int(len(strike_y_sorted) * 0.9)
        
        suggested_x_min = strike_x_sorted[x_low_idx] if x_low_idx < len(strike_x_sorted) else min(strike_x)
        suggested_x_max = strike_x_sorted[x_high_idx] if x_high_idx < len(strike_x_sorted) else max(strike_x)
        suggested_y_min = strike_y_sorted[y_low_idx] if y_low_idx < len(strike_y_sorted) else min(strike_y)
        suggested_y_max = strike_y_sorted[y_high_idx] if y_high_idx < len(strike_y_sorted) else max(strike_y)
        
        print(f"Based on actual called strikes (middle 80%):")
        print(f"  Suggested X range: {suggested_x_min} to {suggested_x_max}")
        print(f"  Suggested Y range: {suggested_y_min} to {suggested_y_max}")
        
        return {
            'current_accuracy': {
                'strikes_in_zone': strikes_in_zone,
                'strikes_outside': strikes_outside_zone,
                'balls_in_zone': balls_in_zone,
                'balls_outside': balls_outside_zone
            },
            'suggested_boundaries': {
                'x_min': suggested_x_min,
                'x_max': suggested_x_max,
                'y_min': suggested_y_min,
                'y_max': suggested_y_max
            }
        }
    
    else:
        print("⚠️ Need both called strikes and balls for validation")
        return None

if __name__ == "__main__":
    corrected_strike_zone_analysis()
