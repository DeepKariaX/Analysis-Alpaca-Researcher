"""Content extraction from web pages."""

import re
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup
import httpx

from ..models.research import ExtractedContent, SearchResult
from ..exceptions.base import ExtractionError
from ..utils.logging import get_logger


class ContentExtractor:
    """Extracts content from web pages."""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
    
    async def extract(self, url: str) -> ExtractedContent:
        """
        Extract content from a URL.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted content
        """
        try:
            self.logger.info(f"Extracting content from: {url}")
            
            async with httpx.AsyncClient(follow_redirects=True, timeout=self.config.extraction_timeout) as client:
                # Set headers
                headers = {
                    "User-Agent": self.config.user_agent,
                    "Accept": "text/html,application/xhtml+xml"
                }
                
                # Make request
                response = await client.get(url, headers=headers)
                
                # Check content type
                content_type = response.headers.get("content-type", "").lower()
                if "application/pdf" in content_type:
                    return ExtractedContent(
                        title="PDF Document",
                        url=url,
                        description="PDF document - contents cannot be extracted directly",
                        content="[PDF document - contents cannot be extracted directly]",
                        extraction_time=datetime.now()
                    )
                    
                # Parse HTML
                soup = BeautifulSoup(response.text[:self.config.max_extraction_size], "html.parser")
                
                # Extract components
                title = self._extract_title(soup)
                description = self._extract_description(soup)
                content = self._extract_content(soup)
                
                # Validate content quality
                if not self._is_valid_content(content, description, title):
                    self.logger.warning(f"Invalid content detected for {url}, discarding")
                    return ExtractedContent(
                        title=title,
                        url=url,
                        description=description,
                        content="",
                        extraction_time=datetime.now(),
                        error="Content validation failed - low quality or restricted content"
                    )
                
                self.logger.info(f"Content extraction completed for: {url}")
                
                return ExtractedContent(
                    title=title,
                    url=url,
                    description=description,
                    content=content,
                    extraction_time=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {str(e)}")
            return ExtractedContent(
                title="Error",
                url=url,
                description="Content extraction failed",
                content="",
                extraction_time=datetime.now(),
                error=str(e)[:100]
            )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_elem = soup.find("title")
        if title_elem and title_elem.string:
            return title_elem.string.strip()[:100]
        return "No title"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description."""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.has_attr("content"):
            return meta_desc["content"][:200]
        return "No description available"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        content_texts = []
        
        # Try to get paragraphs first
        paragraphs = soup.find_all('p')
        for i, p in enumerate(paragraphs):
            if i >= self.config.max_paragraphs:
                break
            text = p.get_text().strip()
            if text and len(text) > 15:
                content_texts.append(text[:300])
                
        # If not enough paragraphs, try other elements
        if len(content_texts) < 2:
            elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
            for i, elem in enumerate(elements):
                if i >= self.config.max_elements:
                    break
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    content_texts.append(text[:200])
                    
        # If still no content, use whatever text we can find
        if not content_texts:
            all_text = soup.get_text()
            clean_text = re.sub(r'\s+', ' ', all_text).strip()
            content_texts = [clean_text[:500]]
            
        return "\n\n".join(content_texts)
    
    def _is_valid_content(self, content: str, description: str = "", title: str = "") -> bool:
        """
        Check if extracted content is valid and meaningful.
        
        Args:
            content: Extracted content text
            description: Page description 
            title: Page title
            
        Returns:
            True if content is valid, False otherwise
        """
        if not content or len(content.strip()) < 50:
            return False
            
        # Check for common error patterns
        error_patterns = [
            "javascript is disabled",
            "page restricted",
            "access denied",
            "403 forbidden",
            "404 not found",
            "503 service unavailable",
            "login required",
            "subscription required",
            "paywall",
            "please enable javascript",
            "cookies required",
            "captcha",
            "robot verification",
            "cloudflare",
            "enable cookies",
            "browser not supported",
            "content not available",
            "page not found",
            "unauthorized access",
            "permission denied"
        ]
        
        content_lower = content.lower()
        title_lower = title.lower() if title else ""
        description_lower = description.lower() if description else ""
        
        # Check if content contains error patterns
        for pattern in error_patterns:
            if (pattern in content_lower or 
                pattern in title_lower or 
                pattern in description_lower):
                return False
        
        # Check if content is mostly navigation/UI elements
        ui_patterns = [
            "skip to main content",
            "toggle navigation",
            "menu",
            "search",
            "login",
            "sign up",
            "cookie policy"
        ]
        
        ui_count = sum(1 for pattern in ui_patterns if pattern in content_lower)
        content_words = len(content.split())
        
        # If more than 30% of content is UI elements, consider it invalid
        if content_words > 0 and ui_count / content_words > 0.3:
            return False
            
        # Check for minimum meaningful content
        sentences = content.split('.')
        meaningful_sentences = [s for s in sentences if len(s.strip()) > 20]
        
        return len(meaningful_sentences) >= 2
    
    async def extract_from_source(self, source: SearchResult) -> ExtractedContent:
        """
        Extract content from a SearchResult, handling academic sources differently.
        
        Args:
            source: SearchResult object containing metadata
            
        Returns:
            Extracted content
        """
        try:
            # For academic sources, use the abstract from metadata instead of web scraping
            if source.source_type == "academic" and source.metadata and source.metadata.get("abstract"):
                abstract = source.metadata.get("abstract", "")
                authors = source.metadata.get("authors", "Unknown authors")
                year = source.metadata.get("year", "Unknown year")
                venue = source.metadata.get("venue", "")
                
                # Create detailed content from metadata
                content_parts = [
                    f"Authors: {authors}",
                    f"Year: {year}",
                ]
                
                if venue:
                    content_parts.append(f"Published in: {venue}")
                
                content_parts.extend([
                    "",
                    "Abstract:",
                    abstract
                ])
                
                content = "\n".join(content_parts)
                
                # Validate academic content (mainly check if abstract is meaningful)
                if not self._is_valid_content(abstract, "", source.title):
                    self.logger.warning(f"Invalid academic content for {source.url}, falling back to web extraction")
                    return await self.extract(source.url)
                
                self.logger.info(f"Used abstract for academic source: {source.url}")
                
                return ExtractedContent(
                    title=source.title,
                    url=source.url,
                    description=f"Academic paper by {authors} ({year})",
                    content=content,
                    extraction_time=datetime.now()
                )
            
            # For web sources or academic sources without abstracts, use regular extraction
            return await self.extract(source.url)
            
        except Exception as e:
            self.logger.error(f"Error extracting content from source {source.url}: {str(e)}")
            return ExtractedContent(
                title=source.title,
                url=source.url,
                description="Content extraction failed",
                content="",
                extraction_time=datetime.now(),
                error=str(e)[:100]
            )