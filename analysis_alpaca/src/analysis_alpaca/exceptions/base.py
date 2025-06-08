"""Base exceptions for the research system."""


class ResearchError(Exception):
    """Base exception for research-related errors."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class SearchError(ResearchError):
    """Exception raised when search operations fail."""
    
    def __init__(self, search_type: str, message: str, details: str = None):
        self.search_type = search_type
        super().__init__(f"Search error ({search_type}): {message}", details)


class ExtractionError(ResearchError):
    """Exception raised when content extraction fails."""
    
    def __init__(self, url: str, message: str, details: str = None):
        self.url = url
        super().__init__(f"Extraction error for {url}: {message}", details)


class ConfigurationError(ResearchError):
    """Exception raised when configuration is invalid."""
    pass