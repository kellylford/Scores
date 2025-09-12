"""
Test Infrastructure Guide for the Scores Application

This document outlines the testing strategy and infrastructure for the Scores application.

## Testing Strategy

### Test Categories
1. **Unit Tests** (`tests/unit/`) - Test individual functions and classes in isolation
2. **Integration Tests** (`tests/integration/`) - Test component interactions and API integrations
3. **UI Tests** (`tests/ui/`) - Test user interface components and interactions

### Test Structure
- `conftest.py` - Shared pytest fixtures and configuration
- `fixtures/` - Test data and mock objects
- Each test module should follow the naming convention `test_*.py`

### Running Tests
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/ui/

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py
```

### Test Dependencies
- pytest - Test framework
- pytest-qt - PyQt testing support
- pytest-cov - Coverage reporting
- pytest-mock - Mocking utilities

### Writing Tests
1. Use descriptive test method names: `test_should_parse_game_data_correctly`
2. Follow AAA pattern: Arrange, Act, Assert
3. Use fixtures for common test data
4. Mock external dependencies (API calls, file system, etc.)
5. Test both success and failure scenarios

### Fixtures Available
- `app` - QApplication instance for UI tests
- `sample_game_data` - Mock game data for testing
- `api_client` - Mock API client

### Example Test
```python
def test_should_create_game_from_valid_data(sample_game_data):
    # Arrange
    raw_data = sample_game_data["valid_game"]
    
    # Act
    game = GameData(raw_data, league="MLB")
    
    # Assert
    assert game.game_id == "expected_id"
    assert game.league == "MLB"
    assert len(game.teams) == 2
```

## Current Status
- Basic test structure established
- Need to implement comprehensive test suites
- UI testing framework ready for PyQt components
- Mock data fixtures need to be populated
