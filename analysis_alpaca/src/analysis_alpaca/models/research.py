"""Data models for research operations."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchSource(Enum):
    """Available search sources."""
    WEB = "web"
    ACADEMIC = "academic"
    BOTH = "both"


@dataclass
class SearchResult:
    """Individual search result."""
    title: str
    url: str
    snippet: str
    source_type: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ExtractedContent:
    """Content extracted from a URL."""
    title: str
    url: str
    description: str
    content: str
    extraction_time: datetime
    error: Optional[str] = None


@dataclass
class ResearchQuery:
    """Research query parameters."""
    query: str
    sources: SearchSource = SearchSource.BOTH
    num_results: int = 2
    
    def __post_init__(self):
        """Validate query parameters."""
        if not self.query.strip():
            raise ValueError("Query cannot be empty")
        
        if self.num_results < 1 or self.num_results > 5:
            raise ValueError("Number of results must be between 1 and 5")
        
        if isinstance(self.sources, str):
            try:
                self.sources = SearchSource(self.sources.lower())
            except ValueError:
                self.sources = SearchSource.BOTH


@dataclass
class ResearchResult:
    """Complete research result."""
    query: ResearchQuery
    search_results: List[SearchResult]
    extracted_content: List[ExtractedContent]
    summary: str
    total_sources: int
    execution_time: float
    errors: List[str]
    
    def format_output(self, max_size: int = 8000) -> str:
        """Format the research result for output."""
        result = f"Research Query: {self.query.query}\n\n"
        
        # Add search results summary
        source_text = "web and academic sources" if self.query.sources == SearchSource.BOTH else f"{self.query.sources.value} sources"
        result += f"Searched {source_text} - Found {len(self.search_results)} results\n\n"
        
        # Add search results
        if self.search_results:
            result += "SEARCH RESULTS:\n"
            for i, search_result in enumerate(self.search_results, 1):
                result += f"{i}. {search_result.title}\n"
                result += f"   URL: {search_result.url}\n"
                result += f"   {search_result.snippet}\n\n"
        
        # Add extracted content
        if self.extracted_content:
            result += f"DETAILED CONTENT FROM TOP {len(self.extracted_content)} SOURCES:\n\n"
            for i, content in enumerate(self.extracted_content, 1):
                if content.error:
                    separator = "=" * 40
                    result += f"{separator}\nSOURCE {i}: Error\n{separator}\n"
                    result += f"Error: {content.error}\n\n"
                else:
                    separator = "=" * 40
                    result += f"{separator}\nSOURCE {i}: {content.title}\n{separator}\n\n"
                    result += f"URL: {content.url}\n"
                    result += f"Description: {content.description}\n\n"
                    result += f"Content:\n{content.content}\n\n"
        
        # Add summary
        result += "\nRESEARCH SUMMARY:\n"
        result += self.summary
        
        # Add errors if any
        if self.errors:
            result += "\n\nERRORS ENCOUNTERED:\n"
            for error in self.errors:
                result += f"- {error}\n"
        
        # Truncate if necessary
        if len(result) > max_size:
            truncation_msg = "\n\n[Content truncated due to size limits]"
            result = result[:max_size - len(truncation_msg)] + truncation_msg
        
        return result