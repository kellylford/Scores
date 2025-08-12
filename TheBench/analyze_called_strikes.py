#!/usr/bin/env python3
"""
Called Strike Zone Analysis
===========================
Analyzes called strikes from MLB pitch data to understand strike zone boundaries
"""

import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def load_pitch_data(folder_path):
    """Load all pitch data CSV files from a folder"""
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {folder_path}")
        return pd.DataFrame()
    
    print(f"Found {len(csv_files)} CSV files")
    
    all_data = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            all_data.append(df)
            print(f"Loaded {len(df)} pitches from {os.path.basename(file)}")
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Total pitches loaded: {len(combined_df)}")
        return combined_df
    else:
        return pd.DataFrame()

def extract_called_strikes(df):
    """Extract only called strikes (strike-looking) with coordinates"""
    # Filter for called strikes
    called_strikes = df[df['play_type'] == 'strike-looking'].copy()
    
    # Only keep rows with valid coordinates
    called_strikes = called_strikes.dropna(subset=['coordinate_x', 'coordinate_y'])
    
    print(f"Found {len(called_strikes)} called strikes with coordinates")
    
    return called_strikes

def analyze_location_frequency(called_strikes_df):
    """Analyze the frequency of called strikes by location"""
    if called_strikes_df.empty:
        print("No called strikes data to analyze")
        return
    
    print("\n" + "="*50)
    print("CALLED STRIKE LOCATION ANALYSIS")
    print("="*50)
    
    # Basic statistics
    print(f"Total called strikes analyzed: {len(called_strikes_df)}")
    print(f"X coordinate range: {called_strikes_df['coordinate_x'].min():.1f} to {called_strikes_df['coordinate_x'].max():.1f}")
    print(f"Y coordinate range: {called_strikes_df['coordinate_y'].min():.1f} to {called_strikes_df['coordinate_y'].max():.1f}")
    
    # Coordinate statistics
    print(f"\nX coordinate statistics:")
    print(f"  Mean: {called_strikes_df['coordinate_x'].mean():.2f}")
    print(f"  Median: {called_strikes_df['coordinate_x'].median():.2f}")
    print(f"  Std Dev: {called_strikes_df['coordinate_x'].std():.2f}")
    
    print(f"\nY coordinate statistics:")
    print(f"  Mean: {called_strikes_df['coordinate_y'].mean():.2f}")
    print(f"  Median: {called_strikes_df['coordinate_y'].median():.2f}")
    print(f"  Std Dev: {called_strikes_df['coordinate_y'].std():.2f}")
    
    # Zone analysis based on our validated coordinate system
    print(f"\nZone Distribution (based on validated coordinate ranges):")
    
    # Horizontal zones
    way_inside = len(called_strikes_df[called_strikes_df['coordinate_x'] < 50])
    inside = len(called_strikes_df[(called_strikes_df['coordinate_x'] >= 50) & (called_strikes_df['coordinate_x'] < 100)])
    strike_zone = len(called_strikes_df[(called_strikes_df['coordinate_x'] >= 100) & (called_strikes_df['coordinate_x'] <= 155)])
    outside = len(called_strikes_df[(called_strikes_df['coordinate_x'] > 155) & (called_strikes_df['coordinate_x'] <= 205)])
    way_outside = len(called_strikes_df[called_strikes_df['coordinate_x'] > 205])
    
    print(f"  Way Inside (X < 50): {way_inside} ({way_inside/len(called_strikes_df)*100:.1f}%)")
    print(f"  Inside (50 <= X < 100): {inside} ({inside/len(called_strikes_df)*100:.1f}%)")
    print(f"  Strike Zone (100 <= X <= 155): {strike_zone} ({strike_zone/len(called_strikes_df)*100:.1f}%)")
    print(f"  Outside (155 < X <= 205): {outside} ({outside/len(called_strikes_df)*100:.1f}%)")
    print(f"  Way Outside (X > 205): {way_outside} ({way_outside/len(called_strikes_df)*100:.1f}%)")
    
    # Vertical zones
    high = len(called_strikes_df[called_strikes_df['coordinate_y'] < 80])
    strike_zone_vert = len(called_strikes_df[(called_strikes_df['coordinate_y'] >= 80) & (called_strikes_df['coordinate_y'] <= 200)])
    low = len(called_strikes_df[called_strikes_df['coordinate_y'] > 200])
    
    print(f"\nVertical Distribution:")
    print(f"  High (Y < 80): {high} ({high/len(called_strikes_df)*100:.1f}%)")
    print(f"  Strike Zone (80 <= Y <= 200): {strike_zone_vert} ({strike_zone_vert/len(called_strikes_df)*100:.1f}%)")
    print(f"  Low (Y > 200): {low} ({low/len(called_strikes_df)*100:.1f}%)")
    
    # Batter handedness analysis
    if 'batter_side' in called_strikes_df.columns:
        print(f"\nBy Batter Handedness:")
        handedness_counts = called_strikes_df['batter_side'].value_counts()
        for hand, count in handedness_counts.items():
            print(f"  {hand}: {count} ({count/len(called_strikes_df)*100:.1f}%)")

def create_coordinate_heatmap(called_strikes_df, save_plot=True):
    """Create a heatmap visualization of called strike locations"""
    if called_strikes_df.empty:
        return
    
    plt.figure(figsize=(12, 8))
    
    # Create 2D histogram
    x = called_strikes_df['coordinate_x']
    y = called_strikes_df['coordinate_y']
    
    plt.hist2d(x, y, bins=20, cmap='Reds', alpha=0.7)
    plt.colorbar(label='Number of Called Strikes')
    
    # Add strike zone boundaries
    plt.axvline(x=100, color='blue', linestyle='--', alpha=0.7, label='Strike Zone Left (X=100)')
    plt.axvline(x=155, color='blue', linestyle='--', alpha=0.7, label='Strike Zone Right (X=155)')
    plt.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='Strike Zone Top (Y=80)')
    plt.axhline(y=200, color='green', linestyle='--', alpha=0.7, label='Strike Zone Bottom (Y=200)')
    
    plt.xlabel('X Coordinate (Horizontal Position)')
    plt.ylabel('Y Coordinate (Vertical Position)')
    plt.title(f'Called Strike Locations Heatmap\n({len(called_strikes_df)} called strikes)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    if save_plot:
        plt.savefig('called_strikes_heatmap.png', dpi=300, bbox_inches='tight')
        print(f"\nHeatmap saved as 'called_strikes_heatmap.png'")
    
    plt.tight_layout()
    plt.show()

def save_called_strikes_csv(called_strikes_df, filename='called_strikes_coordinates.csv'):
    """Save called strikes coordinates to CSV"""
    if called_strikes_df.empty:
        print("No called strikes data to save")
        return
    
    # Select relevant columns
    output_columns = [
        'game_id', 'game_date', 'teams', 'inning', 'inning_half',
        'batter', 'pitcher', 'coordinate_x', 'coordinate_y',
        'velocity_mph', 'pitch_type', 'batter_side', 'balls_before', 'strikes_before'
    ]
    
    # Only include columns that exist in the dataframe
    available_columns = [col for col in output_columns if col in called_strikes_df.columns]
    
    output_df = called_strikes_df[available_columns].copy()
    output_df.to_csv(filename, index=False)
    
    print(f"\nCalled strikes data saved to '{filename}'")
    print(f"Columns included: {', '.join(available_columns)}")

def main():
    # Configuration
    data_folder = "pitchdata"  # Folder containing the CSV files
    
    print("Called Strike Zone Analysis")
    print("="*40)
    
    # Load all pitch data
    print(f"Loading pitch data from '{data_folder}' folder...")
    all_pitches = load_pitch_data(data_folder)
    
    if all_pitches.empty:
        print("No data loaded. Exiting.")
        return
    
    # Extract called strikes
    called_strikes = extract_called_strikes(all_pitches)
    
    if called_strikes.empty:
        print("No called strikes found. Exiting.")
        return
    
    # Save called strikes to CSV
    save_called_strikes_csv(called_strikes)
    
    # Analyze location frequency
    analyze_location_frequency(called_strikes)
    
    # Create visualization
    try:
        create_coordinate_heatmap(called_strikes)
    except Exception as e:
        print(f"Could not create heatmap (matplotlib may not be available): {e}")
    
    print(f"\nAnalysis complete!")
    print(f"Files created:")
    print(f"  - called_strikes_coordinates.csv (coordinate data)")
    print(f"  - called_strikes_heatmap.png (visualization)")

if __name__ == "__main__":
    main()
