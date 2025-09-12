"""
Basic unit tests for the Scores application core functionality.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from version import __version__, get_version
from exceptions import ApiError, DataModelError, ScoresError


class TestVersion:
    """Test version management functionality"""
    
    def test_version_is_defined(self):
        """Test that version is properly defined"""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0
    
    def test_get_version_function(self):
        """Test get_version function returns correct version"""
        version = get_version()
        assert version == __version__
        assert isinstance(version, str)
    
    def test_version_format(self):
        """Test that version follows semantic versioning format"""
        version_parts = __version__.split('.')
        assert len(version_parts) >= 2
        # First two parts should be numbers
        assert version_parts[0].isdigit()
        assert version_parts[1].isdigit()


class TestExceptions:
    """Test custom exception classes"""
    
    def test_scores_error_base_class(self):
        """Test ScoresError base exception"""
        error = ScoresError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_api_error_with_details(self):
        """Test ApiError with additional details"""
        error = ApiError("API failed", status_code=404, endpoint="/api/scores")
        assert str(error) == "API failed"
        assert error.status_code == 404
        assert error.endpoint == "/api/scores"
        assert isinstance(error, ScoresError)
    
    def test_data_model_error_with_field(self):
        """Test DataModelError with field information"""
        error = DataModelError("Invalid data", field="game_id", value="invalid")
        assert str(error) == "Invalid data"
        assert error.field == "game_id"
        assert error.value == "invalid"
        assert isinstance(error, ScoresError)
    
    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from ScoresError"""
        api_error = ApiError("test")
        data_error = DataModelError("test")
        
        assert isinstance(api_error, ScoresError)
        assert isinstance(data_error, ScoresError)


class TestBasicFunctionality:
    """Test basic application functionality"""
    
    def test_imports_work(self):
        """Test that main modules can be imported"""
        try:
            import main
            import scores
            import espn_api
            import exceptions
            # Test passed if no ImportError raised
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    def test_project_structure(self):
        """Test that required files exist"""
        required_files = [
            "main.py",
            "scores.py", 
            "espn_api.py",
            "exceptions.py",
            "version.py",
            "pyproject.toml",
            "requirements.txt"
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"Required file {file_name} not found"
    
    def test_required_directories(self):
        """Test that required directories exist"""
        required_dirs = [
            "models",
            "services", 
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/ui"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Required directory {dir_name} not found"


if __name__ == "__main__":
    pytest.main([__file__])
