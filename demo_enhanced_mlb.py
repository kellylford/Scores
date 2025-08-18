#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import concurrent.futures
import time
import json

def demo_enhanced_mlb_stats():
    """Demonstrate enhanced MLB statistics loading with all available categories"""
    
    print("=== ENHANCED MLB STATISTICS DEMO ===\n")
    
    # All available statistics we could implement
    full_stat_categories = {
        "hitting": [
            ("homeRuns", "Home Runs"),
            ("battingAverage", "Batting Average"), 
            ("rbi", "RBIs"),
            ("hits", "Hits"),
            ("runs", "Runs"),
            ("doubles", "Doubles"),
            ("triples", "Triples"),
            ("stolenBases", "Stolen Bases"),
            ("onBasePercentage", "On-Base %"),
            ("sluggingPercentage", "Slugging %"),
            ("ops", "OPS"),
            ("walks", "Walks"),
            ("strikeouts", "Strikeouts"),
            ("hitByPitch", "Hit By Pitch"),
            ("sacrificeFlies", "Sacrifice Flies"),
            ("groundIntoDoublePlay", "GIDP"),
        ],
        "pitching": [
            ("wins", "Wins"),
            ("losses", "Losses"),
            ("era", "ERA"),
            ("strikeouts", "Strikeouts"),
            ("saves", "Saves"),
            ("holds", "Holds"),
            ("whip", "WHIP"),
            ("inningsPitched", "Innings Pitched"),
            ("hitBatsmen", "Hit Batsmen"),
            ("wildPitches", "Wild Pitches"),
            ("balks", "Balks"),
            ("completeGames", "Complete Games"),
            ("shutouts", "Shutouts"),
            ("blownSaves", "Blown Saves"),
        ],
        "fielding": [
            ("errors", "Errors"),
            ("fieldingPercentage", "Fielding %"),
            ("assists", "Assists"),
            ("putouts", "Putouts"),
            ("chances", "Total Chances"),
            ("doublePlays", "Double Plays"),
            ("triplePlays", "Triple Plays"),
            ("passedBalls", "Passed Balls"),
            ("caughtStealing", "Caught Stealing"),
        ]
    }
    
    # Test current vs enhanced loading
    print("1. CURRENT IMPLEMENTATION (18 stats)")
    start_time = time.time()
    current_stats = load_current_stats()
    current_time = time.time() - start_time
    print(f"   Loaded in {current_time:.2f} seconds")
    
    print("\n2. ENHANCED IMPLEMENTATION (40 stats)")
    start_time = time.time()
    enhanced_stats = load_enhanced_stats_parallel(full_stat_categories)
    enhanced_time = time.time() - start_time
    print(f"   Loaded in {enhanced_time:.2f} seconds")
    
    print(f"\n3. PERFORMANCE COMPARISON")
    print(f"   Current: {len(current_stats)} stats in {current_time:.2f}s")
    print(f"   Enhanced: {len(enhanced_stats)} stats in {enhanced_time:.2f}s")
    print(f"   Efficiency: {len(enhanced_stats)/enhanced_time:.1f} stats/second")
    
    # Show new categories we could add
    print(f"\n4. NEW STATISTICS WE COULD ADD")
    current_stat_names = {stat.get('name', '') for stat in current_stats}
    
    for category, stats in full_stat_categories.items():
        new_stats = []
        for stat_key, display_name in stats:
            if display_name not in current_stat_names:
                new_stats.append(display_name)
        
        if new_stats:
            print(f"   {category.upper()}: {', '.join(new_stats)}")
    
    # Demonstrate caching potential
    print(f"\n5. CACHING DEMONSTRATION")
    demo_caching_benefits()

def load_current_stats():
    """Load stats using current implementation (sequential)"""
    current_categories = [
        ("homeRuns", "hitting", "Home Runs"),
        ("battingAverage", "hitting", "Batting Average"),
        ("rbi", "hitting", "RBIs"),
        ("hits", "hitting", "Hits"),
        ("runs", "hitting", "Runs"),
        ("stolenBases", "hitting", "Stolen Bases"),
        ("doubles", "hitting", "Doubles"),
        ("triples", "hitting", "Triples"),
        ("onBasePercentage", "hitting", "On-Base Percentage"),
        ("sluggingPercentage", "hitting", "Slugging Percentage"),
        ("wins", "pitching", "Wins"),
        ("era", "pitching", "ERA"),
        ("strikeouts", "pitching", "Strikeouts"),
        ("saves", "pitching", "Saves"),
        ("holds", "pitching", "Holds"),
        ("losses", "pitching", "Losses"),
        ("whip", "pitching", "WHIP"),
        ("inningsPitched", "pitching", "Innings Pitched"),
    ]
    
    stats = []
    for stat_key, stat_group, display_name in current_categories:
        try:
            url = f"https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories={stat_key}&statGroup={stat_group}&season=2025"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'leagueLeaders' in data and len(data['leagueLeaders']) > 0:
                    stats.append({'name': display_name, 'data': data})
        except:
            pass
    
    return stats

def load_enhanced_stats_parallel(full_categories):
    """Load enhanced stats using parallel requests"""
    
    # Flatten all categories into request list
    requests_to_make = []
    for group, stats in full_categories.items():
        for stat_key, display_name in stats:
            url = f"https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories={stat_key}&statGroup={group}&season=2025"
            requests_to_make.append((url, display_name))
    
    stats = []
    
    # Use ThreadPoolExecutor for parallel requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_stat = {
            executor.submit(fetch_stat, url): name 
            for url, name in requests_to_make
        }
        
        for future in concurrent.futures.as_completed(future_to_stat):
            stat_name = future_to_stat[future]
            try:
                data = future.result()
                if data:
                    stats.append({'name': stat_name, 'data': data})
            except Exception as e:
                print(f"Error loading {stat_name}: {e}")
    
    return stats

def fetch_stat(url):
    """Fetch a single statistic"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'leagueLeaders' in data and len(data['leagueLeaders']) > 0:
                return data
    except:
        pass
    return None

def demo_caching_benefits():
    """Demonstrate potential caching benefits"""
    
    # Test repeated requests (simulating user browsing stats)
    stat_url = "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=homeRuns&statGroup=hitting&season=2025"
    
    print("   Testing repeated requests (simulating user browsing):")
    
    # Without caching - 5 requests
    start = time.time()
    for i in range(5):
        response = requests.get(stat_url, timeout=5)
    no_cache_time = time.time() - start
    print(f"   Without caching: 5 requests = {no_cache_time:.2f}s")
    
    # With caching - 1 request + 4 cache hits
    start = time.time()
    cached_response = requests.get(stat_url, timeout=5)
    cached_data = cached_response.json()
    for i in range(4):
        # Simulate instant cache hit
        pass
    cache_time = time.time() - start
    print(f"   With caching: 1 request + 4 cache hits = {cache_time:.2f}s")
    print(f"   Caching speedup: {no_cache_time/cache_time:.1f}x faster")
    
    # Show data freshness
    print(f"   Cache validity: Season stats change infrequently")
    print(f"   Recommended cache time: 1-6 hours")

if __name__ == "__main__":
    demo_enhanced_mlb_stats()
