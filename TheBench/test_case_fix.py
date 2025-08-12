#!/usr/bin/env python3

def test_case_insensitive_league():
    """Test case-insensitive league check"""
    
    print("=== Case-Insensitive League Test ===")
    
    # Test different league cases
    leagues = ["MLB", "mlb", "Mlb", "mLb"]
    
    for league in leagues:
        print(f"League: '{league}'")
        
        # This is the new logic
        if league.lower() == "mlb":
            print("  ✓ Kitchen Sink would be added!")
        else:
            print("  ✗ Kitchen Sink would NOT be added")
    
    print("\n=== Summary ===")
    print("All MLB league variations should now work!")

if __name__ == "__main__":
    test_case_insensitive_league()
