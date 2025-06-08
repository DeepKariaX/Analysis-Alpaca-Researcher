"""Web search implementation using DuckDuckGo."""

import re
from typing import List
from urllib.parse import quote_plus, unquote
from bs4 import BeautifulSoup

from .base import BaseSearcher
from ..models.research import SearchResult
from ..exceptions.base import SearchError


class WebSearcher(BaseSearcher):
    """Web search implementation using DuckDuckGo."""
    
    async def search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Perform web search using DuckDuckGo.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            self.logger.info(f"Starting web search for: {query}")
            
            # Create search URL
            encoded_query = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Set headers
            headers = {
                "User-Agent": self.config.user_agent,
                "Accept": "text/html,application/xhtml+xml"
            }
            
            # Make request
            response = await self._make_request(url, headers, self.config.web_timeout)
            
            # Parse results
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = []
            
            # Extract results
            result_blocks = soup.select(".result")
            for block in result_blocks:
                if len(search_results) >= num_results:
                    break
                    
                # Get title and URL
                title_elem = block.select_one(".result__title a")
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                href = title_elem.get("href", "")
                
                # Extract actual URL from redirect
                if "duckduckgo.com" in href:
                    url_match = re.search(r"uddg=([^&]+)", href)
                    if url_match:
                        href = unquote(url_match.group(1))
                
                # Get snippet
                snippet_elem = block.select_one(".result__snippet")
                snippet = snippet_elem.get_text().strip() if snippet_elem else "No snippet available"
                
                # Add to results
                search_results.append(SearchResult(
                    title=title[:100],
                    url=href[:150],
                    snippet=snippet[:self.config.max_snippet_length],
                    source_type="web"
                ))
            
            self.logger.info(f"Web search completed: {len(search_results)} results")
            return search_results
                
        except Exception as e:
            self.logger.error(f"Web search error: {str(e)}")
            raise SearchError("web", str(e))