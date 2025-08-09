from services.api_service import ApiService
from datetime import datetime, timedelta

# Check games from multiple days to see different status types
print("=== GAME STATUS EXAMPLES ===")

for days_back in range(0, 3):
    date = datetime.now() - timedelta(days=days_back)
    print(f"\n{date.strftime('%Y-%m-%d')} ({days_back} days ago):")
    
    try:
        scores = ApiService.get_scores('MLB', date)
        
        statuses = {}
        for game in scores:
            status = game.get('status', 'Unknown')
            start_time = game.get('start_time', '')
            
            if status not in statuses:
                statuses[status] = []
            statuses[status].append(start_time)
        
        for status, times in statuses.items():
            print(f"  {status}: {len(times)} games")
            if times:
                sample_times = list(set(times))[:3]  # Show unique examples
                print(f"    Examples: {sample_times}")
                
    except Exception as e:
        print(f"  Error: {e}")
