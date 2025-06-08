"""Academic search implementation using Semantic Scholar."""

import asyncio
import time
from typing import List
from urllib.parse import quote_plus

from .base import BaseSearcher
from ..models.research import SearchResult
from ..exceptions.base import SearchError

# Global rate limiting for Semantic Scholar API
_last_request_time = 0
_min_request_interval = 2.0  # Minimum 2 seconds between requests


class AcademicSearcher(BaseSearcher):
    """Academic search implementation using Semantic Scholar."""
    
    async def search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Perform academic search using Semantic Scholar.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            self.logger.info(f"Starting academic search for: {query}")
            
            # Global rate limiting
            global _last_request_time
            current_time = time.time()
            time_since_last = current_time - _last_request_time
            
            if time_since_last < _min_request_interval:
                sleep_time = _min_request_interval - time_since_last
                self.logger.info(f"Rate limiting: waiting {sleep_time:.1f}s before API call")
                await asyncio.sleep(sleep_time)
            
            _last_request_time = time.time()
            
            # Create search URL
            encoded_query = quote_plus(query)
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_query}&limit={num_results}&fields=title,authors,year,venue,url,abstract"
            
            self.logger.debug(f"Academic search URL: {url}")
            
            # Make request with retry logic
            headers = {"User-Agent": self.config.user_agent, "Accept": "application/json"}
            
            self.logger.debug(f"Making academic search request with timeout: {self.config.academic_timeout}")
            response = await self._make_request_with_retry(url, headers, self.config.academic_timeout)
            
            self.logger.debug(f"Academic search response status: {response.status_code}")
            
            if response.status_code != 200:
                if response.status_code == 429:
                    self.logger.warning("Semantic Scholar API rate limit reached, returning empty results")
                    return []  # Return empty results instead of failing
                else:
                    self.logger.warning(f"Semantic Scholar API returned status {response.status_code}, returning empty results")
                    return []  # Return empty results for any API error
                
            # Parse results
            try:
                json_data = response.json()
                self.logger.debug(f"API response keys: {json_data.keys() if json_data else 'None'}")
                
                if not json_data:
                    self.logger.warning("Empty response from Semantic Scholar API")
                    return []
                    
                results = json_data.get("data", [])
                
                if not results:
                    self.logger.warning("No academic results found in response")
                    return []
                    
            except Exception as e:
                self.logger.error(f"Failed to parse JSON response: {str(e)}")
                return []
                
            # Process results
            search_results = []
            for i, paper in enumerate(results):
                try:
                    if not paper or not isinstance(paper, dict):
                        self.logger.warning(f"Skipping invalid paper object at index {i}")
                        continue
                    title = paper.get("title", "Untitled Paper")
                    
                    # Get authors
                    authors = paper.get("authors", [])
                    if not authors or not isinstance(authors, list):
                        authors = []
                        
                    author_names = []
                    for author in authors:
                        if author and isinstance(author, dict) and author.get("name"):
                            author_names.append(author.get("name", ""))
                            
                    author_names = author_names[:3]
                    if len(authors) > 3:
                        author_names.append("et al.")
                    author_text = ", ".join(author_names) if author_names else "Unknown authors"
                    
                    # Get publication info
                    year = paper.get("year", "") or ""
                    venue = paper.get("venue", "") or ""
                    pub_info = f"{author_text} ({year})"
                    if venue:
                        pub_info += f" - {venue}"
                        
                    # Get URL and abstract
                    url = paper.get("url", "") or ""
                    abstract = paper.get("abstract", "") or "No abstract available"
                    
                    # Ensure we have valid strings
                    if not isinstance(abstract, str):
                        abstract = "No abstract available"
                    if not isinstance(url, str):
                        url = ""
                    if not isinstance(title, str):
                        title = "Untitled Paper"
                    
                    # Create snippet from publication info and abstract
                    snippet = f"{pub_info[:75]}... {abstract[:125]}" if len(pub_info) > 75 else f"{pub_info} {abstract}"
                    
                    search_results.append(SearchResult(
                        title=title[:100],
                        url=url[:150],
                        snippet=snippet[:self.config.max_snippet_length],
                        source_type="academic",
                        metadata={
                            "authors": author_text,
                            "year": year,
                            "venue": venue,
                            "abstract": abstract
                        }
                    ))
                    
                except Exception as e:
                    self.logger.error(f"Error processing paper at index {i}: {str(e)}")
                    continue
                
            self.logger.info(f"Academic search completed: {len(search_results)} results")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Academic search error: {str(e)}")
            raise SearchError("academic", str(e))
    
    async def _make_request_with_retry(self, url: str, headers: dict, timeout: float):
        """
        Make HTTP request with retry logic for rate limiting.
        
        Args:
            url: URL to request
            headers: Request headers
            timeout: Request timeout
            
        Returns:
            HTTP response
        """
        max_retries = 1  # Reduced to 1 to avoid rate limiting
        base_delay = 2.0  # Increased delay
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Academic search attempt {attempt + 1}/{max_retries}")
                response = await self._make_request(url, headers, timeout)
                self.logger.debug(f"Academic search request successful on attempt {attempt + 1}")
                return response
            except Exception as e:
                self.logger.warning(f"Academic search attempt {attempt + 1} failed: {str(e)[:100]}")
                if "429" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue
                # For rate limiting or final attempt, don't raise - let the main function handle it
                if "429" in str(e):
                    self.logger.warning(f"Rate limit exceeded after {attempt + 1} attempts, will return empty results")
                else:
                    self.logger.error(f"Academic search failed after {attempt + 1} attempts: {str(e)[:100]}")
                raise e