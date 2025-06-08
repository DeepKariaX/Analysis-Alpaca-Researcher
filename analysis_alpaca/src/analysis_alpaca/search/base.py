"""Base classes for search functionality."""

from abc import ABC, abstractmethod
from typing import List
import httpx

from ..models.research import SearchResult
from ..utils.logging import get_logger


class BaseSearcher(ABC):
    """Base class for all search implementations."""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    async def search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Perform a search and return results.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        pass
    
    async def _make_request(self, url: str, headers: dict = None, timeout: float = 10.0) -> httpx.Response:
        """
        Make an HTTP request with proper error handling.
        
        Args:
            url: URL to request
            headers: Optional headers
            timeout: Request timeout
            
        Returns:
            HTTP response
        """
        if headers is None:
            headers = {"User-Agent": self.config.user_agent}
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response