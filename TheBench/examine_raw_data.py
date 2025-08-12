from services.api_service import ApiService
from datetime import datetime
import json

# Get current games and examine the raw structure
scores = ApiService.get_scores('MLB', datetime.now())

if scores:
    print("=== RAW GAME DATA STRUCTURE ===")
    first_game = scores[0]
    
    # Check what's in the ApiService by examining the raw ESPN response
    # Let's try to get the raw response by calling the ESPN API directly
    try:
        import espn_api
        date_str = datetime.now().strftime("%Y%m%d")
        raw_data = espn_api.get_scores('MLB', datetime.now())
        
        if raw_data:
            print(f"First raw game keys: {list(raw_data[0].keys())}")
            
            # Look for status information
            raw_game = raw_data[0]
            if 'competitions' in raw_game:
                competition = raw_game['competitions'][0]
                print(f"Competition keys: {list(competition.keys())}")
                
                if 'status' in competition:
                    status = competition['status']
                    print(f"Status object: {json.dumps(status, indent=2)}")
                    
                if 'competitors' in competition:
                    print(f"Number of competitors: {len(competition['competitors'])}")
                    if competition['competitors']:
                        comp = competition['competitors'][0]
                        print(f"Competitor keys: {list(comp.keys())}")
                        if 'score' in comp:
                            print(f"Score: {comp['score']}")
    except Exception as e:
        print(f"Error accessing raw data: {e}")
        
    print(f"\nProcessed game display: {first_game}")
else:
    print("No games available today")
