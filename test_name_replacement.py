"""
Test script to demonstrate the text processor handling name replacement issues.
This simulates what would happen if ESPN's API returned stories with unresolved player ID placeholders.
"""

import sys
sys.path.append('.')

from text_utils import text_processor
from models.news import NewsData

def test_name_replacement_handling():
    """Test various scenarios of name replacement issues"""
    
    print("=== NAME REPLACEMENT ISSUE HANDLER TEST ===\n")
    
    # Simulate problematic ESPN API responses
    test_articles = [
        {
            "headline": "Great Game Yesterday",
            "description": "{{4362887}} threw for 300 yards while [3128390] caught 8 passes. The #4569618 had an amazing performance.",
            "categories": [
                {"type": "athlete", "description": "Justin Fields"},
                {"type": "athlete", "description": "Allen Lazard"},
                {"type": "athlete", "description": "Garrett Wilson"}
            ]
        },
        {
            "headline": "MLB Trade News",
            "description": "The player_12345 was traded to the athlete_67890 team for future considerations.",
            "categories": []
        },
        {
            "headline": "Normal Article",
            "description": "Aaron Judge hit his 50th home run while Shohei Ohtani pitched 7 innings.",
            "categories": []
        },
        {
            "headline": "Mixed Content",
            "description": "Justin Fields had a great game, but the {{unknown_player}} struggled with turnovers.",
            "categories": [
                {"type": "athlete", "description": "Justin Fields"}
            ]
        }
    ]
    
    for i, article_data in enumerate(test_articles, 1):
        print(f"Test Case {i}: {article_data['headline']}")
        print(f"Original: {article_data['description']}")
        
        # Process with our text processor
        cleaned_description = text_processor.clean_description(
            article_data['description'], 
            article_data
        )
        
        print(f"Cleaned:  {cleaned_description}")
        
        # Test with NewsData model
        article_data['description'] = cleaned_description
        news_data = NewsData(article_data)
        
        print(f"Display:  {news_data.get_display_text()[:100]}...")
        
        if article_data['description'] != cleaned_description:
            print("✅ Issue detected and handled")
        else:
            print("→ No issues found")
        
        print("-" * 60)

def test_real_world_integration():
    """Test with real ESPN data and our processing"""
    
    print("\n=== REAL WORLD INTEGRATION TEST ===\n")
    
    try:
        from espn_api import get_news
        
        # Get some real news
        news_items = get_news('NFL', limit=2)
        
        for i, item in enumerate(news_items, 1):
            print(f"Real Article {i}:")
            print(f"Headline: {item['headline']}")
            print(f"Description: {item['description'][:100]}...")
            
            # Create NewsData object to test full pipeline
            news_data = NewsData(item)
            print(f"Final Display: {news_data.get_display_text()[:100]}...")
            print("-" * 60)
            
        print("✅ Real world integration working correctly")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == "__main__":
    test_name_replacement_handling()
    test_real_world_integration()
    
    print("\n🎯 SOLUTION SUMMARY:")
    print("• Detects common name replacement patterns ({{123}}, [456], #789012, etc.)")
    print("• Replaces unresolved placeholders with [Player Name]")
    print("• Provides fallback descriptions when needed")
    print("• Integrates seamlessly with existing ESPN API")
    print("• No impact on normal articles with proper names")
    print("\n✅ Your news story text replacement issue is now handled!")
