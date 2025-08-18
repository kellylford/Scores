#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time

def comprehensive_mlb_api_evaluation():
    """Comprehensive evaluation of MLB Stats API capabilities"""
    print("=== COMPREHENSIVE MLB STATS API EVALUATION ===\n")
    
    # 1. Test API Response Times
    print("1. PERFORMANCE TESTING")
    print("-" * 40)
    test_performance()
    
    # 2. Discover Available Endpoints
    print("\n2. ENDPOINT DISCOVERY")
    print("-" * 40)
    discover_endpoints()
    
    # 3. Test Different Data Categories
    print("\n3. DATA CATEGORIES")
    print("-" * 40)
    test_data_categories()
    
    # 4. Test Season/Time Range Options
    print("\n4. SEASON & TIME OPTIONS")
    print("-" * 40)
    test_season_options()
    
    # 5. Test Data Formats and Fields
    print("\n5. DATA STRUCTURE ANALYSIS")
    print("-" * 40)
    analyze_data_structure()
    
    # 6. Compare with ESPN Performance
    print("\n6. ESPN vs MLB API COMPARISON")
    print("-" * 40)
    compare_with_espn()

def test_performance():
    """Test API response times"""
    test_url = "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=homeRuns&statGroup=hitting&season=2025"
    
    times = []
    for i in range(5):
        start = time.time()
        try:
            response = requests.get(test_url, timeout=10)
            end = time.time()
            if response.status_code == 200:
                times.append(end - start)
                print(f"  Test {i+1}: {(end-start)*1000:.0f}ms")
            else:
                print(f"  Test {i+1}: Failed ({response.status_code})")
        except Exception as e:
            print(f"  Test {i+1}: Error - {str(e)[:50]}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"  Average response time: {avg_time*1000:.0f}ms")
        print(f"  Performance: {'FAST' if avg_time < 0.5 else 'MODERATE' if avg_time < 1.0 else 'SLOW'}")

def discover_endpoints():
    """Discover available MLB API endpoints"""
    base_urls = [
        "https://statsapi.mlb.com/api/v1",
        "https://lookup-service-prod.mlb.com/json",
        "https://statsapi.mlb.com/api"
    ]
    
    endpoints_to_test = [
        # Stats endpoints
        "/stats",
        "/stats/leaders", 
        "/stats/types",
        "/stats/groups",
        
        # Teams and players
        "/teams",
        "/people",
        "/people/search",
        
        # Games and schedule
        "/schedule",
        "/games",
        "/standings",
        
        # Meta information
        "/seasons",
        "/leagues",
        "/divisions",
        "/venues",
        
        # Advanced stats
        "/stats/streaks",
        "/stats/splits",
        "/stats/situational",
    ]
    
    working_endpoints = []
    
    for base in base_urls:
        for endpoint in endpoints_to_test:
            url = f"{base}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ {url}")
                    working_endpoints.append(url)
                    
                    # Sample the data structure
                    if isinstance(data, dict) and len(str(data)) < 500:
                        print(f"     Keys: {list(data.keys())}")
                elif response.status_code == 404:
                    pass  # Don't spam with 404s
                else:
                    print(f"  ⚠️  {url} - Status {response.status_code}")
            except:
                pass  # Skip connection errors
    
    print(f"\nFound {len(working_endpoints)} working endpoints")
    return working_endpoints

def test_data_categories():
    """Test different statistical categories available"""
    
    # Test stat groups
    stat_groups = ["hitting", "pitching", "fielding"]
    
    # Common stat categories to test
    hitting_stats = [
        "homeRuns", "battingAverage", "rbi", "hits", "runs", "doubles", "triples",
        "stolenBases", "onBasePercentage", "sluggingPercentage", "ops", "walks",
        "strikeouts", "hitByPitch", "sacrificeFlies", "groundIntoDoublePlay"
    ]
    
    pitching_stats = [
        "wins", "losses", "era", "strikeouts", "saves", "holds", "whip",
        "inningsPitched", "hitBatsmen", "wildPitches", "balks", "completeGames",
        "shutouts", "saves", "blownSaves", "gameFinished"
    ]
    
    fielding_stats = [
        "errors", "fieldingPercentage", "assists", "putouts", "chances",
        "doublePlays", "triplePlays", "passedBalls", "caughtStealing"
    ]
    
    all_stats = {
        "hitting": hitting_stats,
        "pitching": pitching_stats, 
        "fielding": fielding_stats
    }
    
    available_stats = {}
    
    for group, stats in all_stats.items():
        print(f"\n{group.upper()} STATISTICS:")
        available_stats[group] = []
        
        for stat in stats:
            url = f"https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories={stat}&statGroup={group}&season=2025"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'leagueLeaders' in data and len(data['leagueLeaders']) > 0:
                        leaders = data['leagueLeaders'][0].get('leaders', [])
                        if leaders:
                            top_value = leaders[0].get('value', 0)
                            top_name = leaders[0].get('person', {}).get('fullName', 'Unknown')
                            print(f"  ✅ {stat}: {top_name} = {top_value}")
                            available_stats[group].append(stat)
                        else:
                            print(f"  ❌ {stat}: No leaders data")
                    else:
                        print(f"  ❌ {stat}: No league leaders")
                else:
                    print(f"  ❌ {stat}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  💥 {stat}: {str(e)[:40]}")
    
    # Summary
    total_available = sum(len(stats) for stats in available_stats.values())
    print(f"\nSUMMARY: {total_available} statistical categories available")
    for group, stats in available_stats.items():
        print(f"  {group}: {len(stats)} categories")
    
    return available_stats

def test_season_options():
    """Test different season and time range options"""
    
    test_url_base = "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=homeRuns&statGroup=hitting"
    
    # Test different seasons
    seasons_to_test = [2025, 2024, 2023, 2022, 2021, 2020]
    
    print("SEASON AVAILABILITY:")
    for season in seasons_to_test:
        url = f"{test_url_base}&season={season}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'leagueLeaders' in data and len(data['leagueLeaders']) > 0:
                    leaders = data['leagueLeaders'][0].get('leaders', [])
                    if leaders:
                        top_value = leaders[0].get('value', 0)
                        top_name = leaders[0].get('person', {}).get('fullName', 'Unknown')
                        print(f"  ✅ {season}: {top_name} = {top_value} HRs")
                    else:
                        print(f"  ❌ {season}: No data")
                else:
                    print(f"  ❌ {season}: No leaders")
            else:
                print(f"  ❌ {season}: HTTP {response.status_code}")
        except:
            print(f"  💥 {season}: Error")
    
    # Test additional parameters
    print("\nADDITIONAL PARAMETERS:")
    additional_params = [
        ("&sportId=1", "MLB Sport ID"),
        ("&limit=50", "Limit results"),
        ("&offset=10", "Offset results"),
        ("&gameType=R", "Regular season only"),
        ("&teamId=147", "Specific team (Yankees)"),
        ("&personId=592450", "Specific player"),
    ]
    
    for param, description in additional_params:
        url = f"{test_url_base}&season=2025{param}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}: HTTP {response.status_code}")
        except:
            print(f"  💥 {description}: Error")

def analyze_data_structure():
    """Analyze the detailed data structure"""
    
    url = "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=homeRuns&statGroup=hitting&season=2025"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            print("DATA STRUCTURE ANALYSIS:")
            print(f"Top-level keys: {list(data.keys())}")
            
            if 'leagueLeaders' in data:
                league_leaders = data['leagueLeaders'][0]
                print(f"League leaders keys: {list(league_leaders.keys())}")
                
                if 'leaders' in league_leaders:
                    leader = league_leaders['leaders'][0]
                    print(f"Individual leader keys: {list(leader.keys())}")
                    
                    # Detailed player information
                    if 'person' in leader:
                        person = leader['person']
                        print(f"Person info keys: {list(person.keys())}")
                        
                        # Show sample person data
                        print(f"Sample person data:")
                        for key, value in person.items():
                            print(f"  {key}: {value}")
                    
                    # Team information
                    if 'team' in leader:
                        team = leader['team']
                        print(f"Team info keys: {list(team.keys())}")
            
            # Save full structure for analysis
            with open("mlb_api_full_structure.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Full structure saved to mlb_api_full_structure.json")
            
    except Exception as e:
        print(f"Error analyzing structure: {e}")

def compare_with_espn():
    """Compare MLB API with ESPN performance and data"""
    
    print("COMPARISON: MLB API vs ESPN API")
    
    # Test MLB API
    mlb_start = time.time()
    mlb_url = "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=homeRuns&statGroup=hitting&season=2025"
    try:
        mlb_response = requests.get(mlb_url, timeout=10)
        mlb_time = time.time() - mlb_start
        mlb_success = mlb_response.status_code == 200
        mlb_data_size = len(mlb_response.content) if mlb_success else 0
    except:
        mlb_time = float('inf')
        mlb_success = False
        mlb_data_size = 0
    
    # Test ESPN API
    espn_start = time.time()
    espn_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics"
    try:
        espn_response = requests.get(espn_url, timeout=10)
        espn_time = time.time() - espn_start
        espn_success = espn_response.status_code == 200
        espn_data_size = len(espn_response.content) if espn_success else 0
    except:
        espn_time = float('inf')
        espn_success = False
        espn_data_size = 0
    
    print(f"\nPERFORMANCE:")
    print(f"  MLB API: {mlb_time*1000:.0f}ms, {mlb_data_size} bytes")
    print(f"  ESPN API: {espn_time*1000:.0f}ms, {espn_data_size} bytes")
    print(f"  Winner: {'MLB API' if mlb_time < espn_time else 'ESPN API'}")
    
    print(f"\nRELIABILITY:")
    print(f"  MLB API: {'✅ Success' if mlb_success else '❌ Failed'}")
    print(f"  ESPN API: {'✅ Success' if espn_success else '❌ Failed'}")
    
    print(f"\nDATA QUALITY:")
    if mlb_success and espn_success:
        mlb_data = mlb_response.json()
        espn_data = espn_response.json()
        
        # Compare home run leaders
        if 'leagueLeaders' in mlb_data:
            mlb_hr_leader = mlb_data['leagueLeaders'][0]['leaders'][0]['value']
            print(f"  MLB API HR leader: {mlb_hr_leader}")
        
        if 'stats' in espn_data and 'categories' in espn_data['stats']:
            for cat in espn_data['stats']['categories']:
                if cat.get('name') == 'homeruns':
                    espn_hr_leader = cat['leaders'][0]['value']
                    print(f"  ESPN API HR leader: {espn_hr_leader}")
                    break

def generate_recommendations():
    """Generate recommendations based on evaluation"""
    print("\n" + "="*50)
    print("RECOMMENDATIONS")
    print("="*50)
    
    recommendations = [
        "1. PERFORMANCE: MLB API is likely faster for specific stats",
        "2. DATA QUALITY: MLB API provides full season data vs ESPN recent performance", 
        "3. RELIABILITY: MLB API is official source, more reliable",
        "4. COVERAGE: MLB API has more detailed baseball statistics",
        "5. IMPLEMENTATION: Can batch multiple stat requests for efficiency",
        "6. CACHING: Implement caching since season stats don't change frequently",
        "7. FALLBACK: Keep ESPN as fallback for non-baseball sports",
        "8. ENHANCEMENT: Could add player photos, team info from MLB API",
    ]
    
    for rec in recommendations:
        print(f"  {rec}")

if __name__ == "__main__":
    comprehensive_mlb_api_evaluation()
    generate_recommendations()
