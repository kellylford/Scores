from services.api_service import ApiService
from models.game import GameData
from datetime import datetime

print("=== NFL GAMES CHECK ===")
try:
    nfl_scores = ApiService.get_scores('NFL', datetime.now())
    print(f"NFL games today: {len(nfl_scores)}")
    
    if nfl_scores:
        print(f"First NFL game raw: {nfl_scores[0]}")
        nfl_game = GameData(nfl_scores[0])
        print(f"NFL display: {nfl_game.get_display_text()}")
        
        # Check status patterns
        for i, game_data in enumerate(nfl_scores[:3]):
            game = GameData(game_data)
            print(f"  Game {i+1}: {game.get_display_text()}")
    else:
        print("No NFL games today - checking preseason or recent games...")
        
        # Try different dates during NFL season
        from datetime import timedelta
        for days_back in range(0, 7):
            date = datetime.now() - timedelta(days=days_back)
            nfl_scores = ApiService.get_scores('NFL', date)
            if nfl_scores:
                print(f"\nFound NFL games {days_back} days ago:")
                for game_data in nfl_scores[:2]:
                    game = GameData(game_data)
                    print(f"  {game.get_display_text()}")
                break
                
except Exception as e:
    print(f"Error: {e}")

print("\n=== BASEBALL PLAY-BY-PLAY CHECK ===")
try:
    # Get a current MLB game and check for play-by-play data
    mlb_scores = ApiService.get_scores('MLB', datetime.now())
    if mlb_scores:
        game_id = mlb_scores[0]['id']
        print(f"Checking game {game_id} for play-by-play data...")
        
        # Get detailed game data
        game_details = ApiService.get_game_details('MLB', game_id)
        
        print("Available game detail fields:")
        for key in game_details.keys():
            print(f"  {key}: {type(game_details[key])}")
            
        # Check if there's play-by-play data
        if 'plays' in game_details:
            plays = game_details['plays']
            print(f"\nPLAY-BY-PLAY DATA FOUND!")
            print(f"Plays type: {type(plays)}")
            if isinstance(plays, list):
                print(f"Number of plays: {len(plays)}")
                if plays:
                    print(f"First play: {plays[0]}")
            elif isinstance(plays, dict):
                print(f"Plays keys: {list(plays.keys())}")
                
        # Check for other potential play data fields
        potential_fields = ['commentary', 'timeline', 'events', 'innings', 'playByPlay']
        for field in potential_fields:
            if field in game_details:
                print(f"\nFound {field}: {type(game_details[field])}")
                
except Exception as e:
    print(f"Error checking play-by-play: {e}")
