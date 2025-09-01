## Summary
Implement a "My Teams" feature that allows users to mark teams from NFL, MLB, and NCAAF as favorites and provides a dedicated view to track only those teams' games, scores, and schedules.

## Feature Overview
- **Location**: New menu item "My Teams" positioned after "Live Scores" on main menu
- **Scope**: Support for NFL, MLB, NCAAF teams (20 team limit)
- **Functionality**: Track live games, past results, and future schedules for favorited teams
- **Storage**: JSON-based configuration file for persistence

## Key Requirements

### User Interface
- [ ] Add "My Teams" entry to main menu (position 2, after Live Scores)
- [ ] Multi-tabbed configuration dialog (NFL, MLB, NCAAF, Favorites tabs)
- [ ] Space key toggle for marking teams as favorites
- [ ] Past/Future toggle for non-live games display
- [ ] Game list view identical to Live Scores format

### Configuration Management
- [ ] Team selection with alphabetical sorting per league
- [ ] "Favorite - [Team Name]" prefix display for marked teams
- [ ] Save button on all configuration tabs
- [ ] Configure button in My Teams view
- [ ] 20-team maximum with enforcement

### Data & Integration
- [ ] JSON storage: `favorite_teams.json` in executable directory
- [ ] Integration with existing ApiService patterns
- [ ] Seamless navigation to game details view
- [ ] Consistent with existing accessibility patterns

### Game Display Logic
- [ ] Live games: Show current scores (same detail as Live Scores)
- [ ] Past mode: Most recent completed game per team
- [ ] Future mode: Next upcoming game per team
- [ ] Empty states: Teams with no games in separate section

## Technical Implementation

### Core Components Required
```
services/
  favorite_teams_manager.py    # Configuration management
views/
  my_teams_view.py            # Main My Teams display
dialogs/
  team_configuration_dialog.py # Team selection interface
```

### JSON Schema
```json
{
  "version": "1.0", 
  "favorites": [
    {
      "team_id": "string",
      "team_name": "string",
      "league": "string", 
      "added_date": "ISO date"
    }
  ]
}
```

## Acceptance Criteria
- [ ] Users can mark/unmark teams as favorites from configuration dialog
- [ ] My Teams view shows relevant games for favorited teams only
- [ ] Past/Future toggle correctly filters game display
- [ ] Configuration persists across application sessions
- [ ] No impact on existing Live Scores or league view functionality
- [ ] Full keyboard accessibility with screen reader support
- [ ] Performance: Configuration loads <2s, My Teams view <5s

## Testing Requirements
- [ ] Unit tests for FavoriteTeamsManager class
- [ ] Integration tests for API data retrieval and filtering
- [ ] Navigation flow testing between views
- [ ] Accessibility validation with assistive technology
- [ ] Performance testing with maximum 20 teams
- [ ] Regression testing for existing functionality

## Implementation Notes
- Follow existing MVC patterns and PyQt6 dialog structures
- Leverage established ApiService methods for team/game data
- Maintain consistency with current navigation stack approach
- Use existing BaseView pattern for view management
- Implement Windows UIA notifications following current patterns

## Future Enhancements (Out of Scope)
- Additional league support (NBA, NHL)
- Push notifications for favorite team events
- Team-specific news aggregation
- Advanced filtering options

---

**Branch**: `feature/my-teams`  
**Specification**: See `TheBench/MY_TEAMS_FEATURE_SPECIFICATION.md`  
**Priority**: Medium  
**Complexity**: High
