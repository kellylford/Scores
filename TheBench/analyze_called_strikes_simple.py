#!/usr/bin/env python3
"""
Called Strike Zone Analysis (Standard Library Only)
===================================================
Analyzes called strikes from MLB pitch data to understand strike zone boundaries
"""

import csv
import glob
import os
from collections import Counter, defaultdict
import json

def load_pitch_data(folder_path):
    """Load all pitch data CSV files from a folder"""
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {folder_path}")
        return []
    
    print(f"Found {len(csv_files)} CSV files")
    
    all_pitches = []
    for file in csv_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                file_pitches = list(reader)
                all_pitches.extend(file_pitches)
                print(f"Loaded {len(file_pitches)} pitches from {os.path.basename(file)}")
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    print(f"Total pitches loaded: {len(all_pitches)}")
    return all_pitches

def extract_called_strikes(pitches):
    """Extract only called strikes (strike-looking) with coordinates"""
    called_strikes = []
    
    for pitch in pitches:
        # Check if it's a called strike with coordinates
        if (pitch.get('play_type') == 'strike-looking' and 
            pitch.get('coordinate_x') and 
            pitch.get('coordinate_y') and
            pitch.get('coordinate_x') != '' and 
            pitch.get('coordinate_y') != ''):
            
            try:
                # Convert coordinates to float to validate they're numeric
                x = float(pitch['coordinate_x'])
                y = float(pitch['coordinate_y'])
                pitch['coordinate_x'] = x
                pitch['coordinate_y'] = y
                called_strikes.append(pitch)
            except (ValueError, TypeError):
                # Skip pitches with invalid coordinates
                continue
    
    print(f"Found {len(called_strikes)} called strikes with valid coordinates")
    return called_strikes

def analyze_location_frequency(called_strikes):
    """Analyze the frequency of called strikes by location"""
    if not called_strikes:
        print("No called strikes data to analyze")
        return
    
    print("\n" + "="*50)
    print("CALLED STRIKE LOCATION ANALYSIS")
    print("="*50)
    
    # Extract coordinates
    x_coords = [pitch['coordinate_x'] for pitch in called_strikes]
    y_coords = [pitch['coordinate_y'] for pitch in called_strikes]
    
    # Basic statistics
    print(f"Total called strikes analyzed: {len(called_strikes)}")
    print(f"X coordinate range: {min(x_coords):.1f} to {max(x_coords):.1f}")
    print(f"Y coordinate range: {min(y_coords):.1f} to {max(y_coords):.1f}")
    
    # Calculate basic stats
    def calculate_stats(values):
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mean = sum(values) / n
        median = sorted_vals[n//2] if n % 2 == 1 else (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = variance ** 0.5
        return mean, median, std_dev
    
    x_mean, x_median, x_std = calculate_stats(x_coords)
    y_mean, y_median, y_std = calculate_stats(y_coords)
    
    print(f"\nX coordinate statistics:")
    print(f"  Mean: {x_mean:.2f}")
    print(f"  Median: {x_median:.2f}")
    print(f"  Std Dev: {x_std:.2f}")
    
    print(f"\nY coordinate statistics:")
    print(f"  Mean: {y_mean:.2f}")
    print(f"  Median: {y_median:.2f}")
    print(f"  Std Dev: {y_std:.2f}")
    
    # Zone analysis based on our validated coordinate system
    print(f"\nZone Distribution (based on validated coordinate ranges):")
    
    # Count strikes in each horizontal zone
    way_inside = sum(1 for x in x_coords if x < 50)
    inside = sum(1 for x in x_coords if 50 <= x < 100)
    strike_zone_horiz = sum(1 for x in x_coords if 100 <= x <= 155)
    outside = sum(1 for x in x_coords if 155 < x <= 205)
    way_outside = sum(1 for x in x_coords if x > 205)
    
    total = len(called_strikes)
    print(f"  Way Inside (X < 50): {way_inside} ({way_inside/total*100:.1f}%)")
    print(f"  Inside (50 <= X < 100): {inside} ({inside/total*100:.1f}%)")
    print(f"  Strike Zone (100 <= X <= 155): {strike_zone_horiz} ({strike_zone_horiz/total*100:.1f}%)")
    print(f"  Outside (155 < X <= 205): {outside} ({outside/total*100:.1f}%)")
    print(f"  Way Outside (X > 205): {way_outside} ({way_outside/total*100:.1f}%)")
    
    # Count strikes in each vertical zone
    high = sum(1 for y in y_coords if y < 80)
    strike_zone_vert = sum(1 for y in y_coords if 80 <= y <= 200)
    low = sum(1 for y in y_coords if y > 200)
    
    print(f"\nVertical Distribution:")
    print(f"  High (Y < 80): {high} ({high/total*100:.1f}%)")
    print(f"  Strike Zone (80 <= Y <= 200): {strike_zone_vert} ({strike_zone_vert/total*100:.1f}%)")
    print(f"  Low (Y > 200): {low} ({low/total*100:.1f}%)")
    
    # True strike zone (both X and Y in zone)
    true_strikes = sum(1 for pitch in called_strikes 
                      if 100 <= pitch['coordinate_x'] <= 155 and 80 <= pitch['coordinate_y'] <= 200)
    print(f"\nTrue Strike Zone (both X and Y in zone): {true_strikes} ({true_strikes/total*100:.1f}%)")
    
    # Batter handedness analysis
    handedness_counter = Counter(pitch.get('batter_side', 'Unknown') for pitch in called_strikes)
    print(f"\nBy Batter Handedness:")
    for hand, count in handedness_counter.most_common():
        print(f"  {hand}: {count} ({count/total*100:.1f}%)")
    
    # Pitch type analysis
    pitch_type_counter = Counter(pitch.get('pitch_type', 'Unknown') for pitch in called_strikes)
    print(f"\nBy Pitch Type (Top 10):")
    for ptype, count in pitch_type_counter.most_common(10):
        print(f"  {ptype}: {count} ({count/total*100:.1f}%)")

def create_zone_grid_analysis(called_strikes):
    """Create a grid-based analysis of strike locations"""
    if not called_strikes:
        return
    
    print(f"\n" + "="*50)
    print("STRIKE ZONE GRID ANALYSIS")
    print("="*50)
    
    # Create a 9-zone grid like umpires use
    zone_counts = defaultdict(int)
    
    for pitch in called_strikes:
        x, y = pitch['coordinate_x'], pitch['coordinate_y']
        
        # Determine horizontal zone (1=left, 2=center, 3=right)
        if x < 100:
            h_zone = 1  # Left
        elif x <= 155:
            h_zone = 2  # Center
        else:
            h_zone = 3  # Right
        
        # Determine vertical zone (1=high, 2=middle, 3=low)
        if y < 80:
            v_zone = 1  # High
        elif y <= 200:
            v_zone = 2  # Middle
        else:
            v_zone = 3  # Low
        
        zone_key = f"{v_zone}{h_zone}"
        zone_counts[zone_key] += 1
    
    # Display as a grid
    print("Zone Grid (like traditional 9-zone system):")
    print("   Left  Center Right")
    
    zone_names = {
        '11': 'High-Left', '12': 'High-Center', '13': 'High-Right',
        '21': 'Mid-Left', '22': 'Mid-Center', '23': 'Mid-Right',
        '31': 'Low-Left', '32': 'Low-Center', '33': 'Low-Right'
    }
    
    for row in [1, 2, 3]:
        row_name = ["High", "Mid ", "Low "][row-1]
        counts = [zone_counts[f"{row}{col}"] for col in [1, 2, 3]]
        print(f"{row_name} {counts[0]:4d}  {counts[1]:4d}   {counts[2]:4d}")
    
    print(f"\nDetailed Zone Breakdown:")
    total = len(called_strikes)
    for zone_id in ['11', '12', '13', '21', '22', '23', '31', '32', '33']:
        count = zone_counts[zone_id]
        pct = count/total*100 if total > 0 else 0
        print(f"  {zone_names[zone_id]:11}: {count:4d} ({pct:4.1f}%)")

def save_called_strikes_csv(called_strikes, filename='called_strikes_coordinates.csv'):
    """Save called strikes coordinates to CSV"""
    if not called_strikes:
        print("No called strikes data to save")
        return
    
    # Define output columns
    output_columns = [
        'game_id', 'game_date', 'teams', 'inning', 'inning_half',
        'batter', 'pitcher', 'coordinate_x', 'coordinate_y',
        'velocity_mph', 'pitch_type', 'batter_side', 'balls_before', 'strikes_before'
    ]
    
    # Write CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # Get available columns from first pitch
        available_columns = [col for col in output_columns if col in called_strikes[0]]
        
        writer = csv.DictWriter(f, fieldnames=available_columns)
        writer.writeheader()
        
        for pitch in called_strikes:
            row = {col: pitch.get(col, '') for col in available_columns}
            writer.writerow(row)
    
    print(f"\nCalled strikes data saved to '{filename}'")
    print(f"Columns included: {', '.join(available_columns)}")
    print(f"Records saved: {len(called_strikes)}")

def save_analysis_summary(called_strikes, filename='called_strikes_analysis.json'):
    """Save analysis summary to JSON file"""
    if not called_strikes:
        return
    
    x_coords = [pitch['coordinate_x'] for pitch in called_strikes]
    y_coords = [pitch['coordinate_y'] for pitch in called_strikes]
    
    def calculate_stats(values):
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mean = sum(values) / n
        median = sorted_vals[n//2] if n % 2 == 1 else (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2
        return {
            'mean': round(mean, 2),
            'median': round(median, 2),
            'min': min(values),
            'max': max(values),
            'count': n
        }
    
    summary = {
        'total_called_strikes': len(called_strikes),
        'x_coordinate_stats': calculate_stats(x_coords),
        'y_coordinate_stats': calculate_stats(y_coords),
        'zone_distribution': {
            'way_inside': sum(1 for x in x_coords if x < 50),
            'inside': sum(1 for x in x_coords if 50 <= x < 100),
            'strike_zone': sum(1 for x in x_coords if 100 <= x <= 155),
            'outside': sum(1 for x in x_coords if 155 < x <= 205),
            'way_outside': sum(1 for x in x_coords if x > 205)
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Analysis summary saved to '{filename}'")

def main():
    # Configuration
    data_folder = "pitchdata"  # Folder containing the CSV files
    
    print("Called Strike Zone Analysis")
    print("="*40)
    
    # Check if folder exists
    if not os.path.exists(data_folder):
        print(f"Error: Folder '{data_folder}' not found.")
        print("Please make sure you have a 'pitchdata' folder with CSV files.")
        return
    
    # Load all pitch data
    print(f"Loading pitch data from '{data_folder}' folder...")
    all_pitches = load_pitch_data(data_folder)
    
    if not all_pitches:
        print("No data loaded. Exiting.")
        return
    
    # Extract called strikes
    called_strikes = extract_called_strikes(all_pitches)
    
    if not called_strikes:
        print("No called strikes found. Exiting.")
        return
    
    # Save called strikes to CSV
    save_called_strikes_csv(called_strikes)
    
    # Analyze location frequency
    analyze_location_frequency(called_strikes)
    
    # Create zone grid analysis
    create_zone_grid_analysis(called_strikes)
    
    # Save analysis summary
    save_analysis_summary(called_strikes)
    
    print(f"\nAnalysis complete!")
    print(f"Files created:")
    print(f"  - called_strikes_coordinates.csv (all called strike data)")
    print(f"  - called_strikes_analysis.json (summary statistics)")

if __name__ == "__main__":
    main()
