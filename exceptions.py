"""
Custom exceptions for the Scores application.
Provides specific error types for better error handling and debugging.
"""

class ScoresError(Exception):
    """Base exception class for all Scores application errors"""
    pass

class ApiError(ScoresError):
    """Custom exception for API-related errors"""
    def __init__(self, message: str, status_code: int = None, endpoint: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint

class DataModelError(ScoresError):
    """Custom exception for data model parsing errors"""
    def __init__(self, message: str, field: str = None, value = None):
        super().__init__(message)
        self.field = field
        self.value = value

class ConfigurationError(ScoresError):
    """Custom exception for configuration-related errors"""
    pass

class NetworkError(ApiError):
    """Custom exception for network connectivity issues"""
    pass

class AuthenticationError(ApiError):
    """Custom exception for authentication/authorization issues"""
    pass

class ValidationError(ScoresError):
    """Custom exception for data validation errors"""
    def __init__(self, message: str, field: str = None, value = None):
        super().__init__(message)
        self.field = field
        self.value = value
