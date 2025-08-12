# Sports Scores Application - Architecture Refactoring Plan

## Current State Analysis

### What We Have Built
- Fully functional sports analysis application with PyQt6 UI
- ESPN API integration for live MLB and NFL data
- Hierarchical navigation: League → Games → Game Details → Sub-views (Plays/Drives)
- Enhanced features: Date picker, officials drill-down, drive analysis, kitchen sink
- Working Windows executable build process

### Current Issues
- **Single File Monolith**: All code in `scores.py` (~2,600+ lines)
- **Sport-Specific Logic Mixed**: MLB and NFL code intertwined
- **Risk of Breaking Changes**: Modifying MLB affects NFL and vice versa
- **Hard to Extend**: Adding new sports requires navigating massive file
- **Testing Challenges**: No isolation between components

## Proposed Architecture

### 1. Core Framework Structure

```
sports_app/
├── __init__.py
├── main.py                    # Application entry point
├── core/                      # Core framework components
│   ├── __init__.py
│   ├── base_app.py           # Main application window
│   ├── base_views.py         # Generic view classes
│   ├── navigation.py         # Navigation stack management
│   ├── date_picker.py        # Enhanced date picker dialog
│   └── ui_helpers.py         # Common UI utilities
├── api/                       # API layer
│   ├── __init__.py
│   ├── base_api.py           # Generic API interface
│   ├── espn_api.py           # ESPN-specific implementation
│   └── data_models.py        # Data structure definitions
├── sports/                    # Sport-specific implementations
│   ├── __init__.py
│   ├── base_sport.py         # Generic sport interface
│   ├── mlb/                  # MLB-specific code
│   │   ├── __init__.py
│   │   ├── mlb_sport.py      # MLB sport implementation
│   │   ├── mlb_views.py      # MLB-specific views
│   │   ├── mlb_data.py       # MLB data processing
│   │   └── mlb_config.py     # MLB configuration
│   └── nfl/                  # NFL-specific code
│       ├── __init__.py
│       ├── nfl_sport.py      # NFL sport implementation
│       ├── nfl_views.py      # NFL-specific views
│       ├── nfl_data.py       # NFL data processing
│       └── nfl_config.py     # NFL configuration
├── ui/                        # UI components
│   ├── __init__.py
│   ├── dialogs.py            # Common dialogs
│   ├── tables.py             # Accessible table components
│   └── widgets.py            # Custom widgets
└── utils/                     # Utilities
    ├── __init__.py
    ├── constants.py          # Application constants
    ├── config.py             # Configuration management
    └── helpers.py            # General utilities
```

### 2. Generic View Hierarchy

Each sport follows the same pattern but with sport-specific implementations:

#### Level 1: League Selection
```python
class BaseLeagueView(QWidget):
    """Generic league selection interface"""
    def setup_ui(self) -> None
    def load_games(self, date: str) -> None
    def on_game_selected(self, game_data: dict) -> None
```

#### Level 2: Score View (Games List)
```python
class BaseScoreView(QWidget):
    """Generic games list interface"""
    def setup_ui(self) -> None
    def display_games(self, games: List[dict]) -> None
    def on_game_details_requested(self, game_id: str) -> None
```

#### Level 3: Game Details
```python
class BaseGameDetailsView(QWidget):
    """Generic game details interface"""
    def setup_ui(self) -> None
    def load_game_details(self, game_id: str) -> None
    def get_available_sub_views(self) -> List[str]
    def on_sub_view_requested(self, view_type: str) -> None
```

#### Level 4: Sub-Views (Plays, Drives, etc.)
```python
class BaseSubView(QWidget):
    """Generic sub-view interface"""
    def setup_ui(self) -> None
    def load_data(self, game_data: dict) -> None
    def format_data_for_display(self, data: Any) -> Any
```

### 3. Sport-Specific Implementation Pattern

#### Sport Registry
```python
class SportRegistry:
    """Centralized registry for sport implementations"""
    _sports = {}
    
    @classmethod
    def register_sport(cls, sport_code: str, sport_class: Type[BaseSport]):
        cls._sports[sport_code] = sport_class
    
    @classmethod
    def get_sport(cls, sport_code: str) -> BaseSport:
        return cls._sports[sport_code]()
```

#### Sport Interface
```python
class BaseSport(ABC):
    """Abstract base class for sport implementations"""
    
    @property
    @abstractmethod
    def name(self) -> str: pass
    
    @property  
    @abstractmethod
    def code(self) -> str: pass
    
    @abstractmethod
    def get_league_view(self) -> BaseLeagueView: pass
    
    @abstractmethod
    def get_score_view(self) -> BaseScoreView: pass
    
    @abstractmethod
    def get_game_details_view(self) -> BaseGameDetailsView: pass
    
    @abstractmethod
    def get_available_sub_views(self) -> Dict[str, Type[BaseSubView]]: pass
    
    @abstractmethod
    def process_game_data(self, raw_data: dict) -> dict: pass
```

#### MLB Implementation
```python
class MLBSport(BaseSport):
    name = "Major League Baseball"
    code = "mlb"
    
    def get_available_sub_views(self) -> Dict[str, Type[BaseSubView]]:
        return {
            "plays": MLBPlaysView,
            "leaders": MLBLeadersView,
            "boxscore": MLBBoxscoreView,
            "standings": MLBStandingsView,
            "kitchensink": MLBKitchenSinkView
        }
```

#### NFL Implementation
```python
class NFLSport(BaseSport):
    name = "National Football League"
    code = "nfl"
    
    def get_available_sub_views(self) -> Dict[str, Type[BaseSubView]]:
        return {
            "drives": NFLDrivesView,
            "leaders": NFLLeadersView,
            "boxscore": NFLBoxscoreView,
            "standings": NFLStandingsView
        }
```

### 4. Data Processing Separation

#### Generic Data Processor
```python
class BaseDataProcessor(ABC):
    """Abstract base for sport-specific data processing"""
    
    @abstractmethod
    def extract_basic_info(self, raw_data: dict) -> dict: pass
    
    @abstractmethod
    def extract_plays_data(self, raw_data: dict) -> List[dict]: pass
    
    @abstractmethod
    def format_play_text(self, play_data: dict) -> str: pass
```

#### MLB Data Processor
```python
class MLBDataProcessor(BaseDataProcessor):
    def format_play_text(self, play_data: dict) -> str:
        # MLB-specific play formatting
        return f"[{inning}] {play_text}"
```

#### NFL Data Processor
```python
class NFLDataProcessor(BaseDataProcessor):
    def format_play_text(self, play_data: dict) -> str:
        # NFL-specific play formatting with down/distance
        down_distance = self.get_down_distance(play_data)
        return f"{down_distance} {play_text}"
```

### 5. Configuration Management

#### Sport-Specific Config
```python
# mlb/mlb_config.py
MLB_CONFIG = {
    "detail_fields": ["boxscore", "plays", "leaders", "standings", "kitchensink"],
    "play_fields": ["text", "scoreValue", "team"],
    "date_range": {"start": 1900, "end": 2030},
    "api_endpoints": {
        "games": "/baseball/mlb/scoreboard",
        "details": "/baseball/mlb/summary"
    }
}

# nfl/nfl_config.py  
NFL_CONFIG = {
    "detail_fields": ["boxscore", "drives", "leaders", "standings"],
    "drive_fields": ["description", "plays", "result"],
    "play_fields": ["text", "start", "end", "clock"],
    "date_range": {"start": 1990, "end": 2030},
    "api_endpoints": {
        "games": "/football/nfl/scoreboard", 
        "details": "/football/nfl/summary"
    }
}
```

### 6. Migration Strategy

#### Phase 1: Extract Core Components (Week 1)
1. Create new directory structure
2. Extract date picker, navigation, and UI helpers
3. Create base view classes
4. Extract API layer
5. Test that basic functionality still works

#### Phase 2: Sport Separation (Week 2)
1. Create sport registry and base sport interface
2. Extract MLB-specific code into mlb/ module
3. Extract NFL-specific code into nfl/ module
4. Implement sport-specific data processors
5. Test each sport in isolation

#### Phase 3: View Refactoring (Week 3)
1. Refactor each view level to use base classes
2. Implement sport-specific view overrides
3. Clean up duplicate code
4. Add comprehensive error handling

#### Phase 4: Testing & Documentation (Week 4)
1. Add unit tests for each sport module
2. Add integration tests
3. Update documentation
4. Performance optimization
5. Final executable rebuild

### 7. Benefits of This Architecture

#### Maintainability
- **Isolation**: Changes to MLB won't affect NFL
- **Modularity**: Each component has single responsibility
- **Testability**: Can test sports independently
- **Extensibility**: Adding new sports is straightforward

#### Development Experience
- **Clear Structure**: Easy to find relevant code
- **Consistent Patterns**: Same structure for all sports
- **Reusable Components**: Core UI components shared
- **Configuration Driven**: Easy to adjust sport behavior

#### Risk Mitigation
- **Gradual Migration**: Can migrate incrementally
- **Backward Compatibility**: Keep existing functionality
- **Sport Isolation**: Bug in one sport doesn't break others
- **Clear Interfaces**: Well-defined contracts between components

### 8. Future Sport Addition Process

When adding a new sport (e.g., NBA):

1. **Create Sport Module**: `sports/nba/`
2. **Implement Sport Class**: Inherit from `BaseSport`
3. **Add Data Processor**: Sport-specific data handling
4. **Create Views**: Sport-specific UI components
5. **Add Configuration**: Sport-specific settings
6. **Register Sport**: Add to sport registry
7. **Test**: Verify functionality in isolation

### 9. Validation Approach

Before implementing, we'll:
1. **Prototype Key Interfaces**: Verify the base classes work
2. **Test Migration Strategy**: Ensure we can extract components safely
3. **Validate Sport Separation**: Confirm MLB/NFL can be isolated
4. **Performance Check**: Ensure architecture doesn't slow down the app

## Implementation Priority

1. **High Priority**: Core framework, sport separation, view hierarchy
2. **Medium Priority**: Configuration management, testing framework
3. **Low Priority**: Performance optimization, advanced features

This architecture will make the codebase much more maintainable while preserving all the functionality you've built. Each sport becomes a self-contained module that can be developed and tested independently.
