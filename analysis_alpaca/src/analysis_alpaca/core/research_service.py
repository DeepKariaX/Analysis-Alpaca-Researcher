"""Core research service that orchestrates searches and content extraction."""

import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor
import asyncio

from ..models.research import ResearchQuery, ResearchResult, SearchResult, ExtractedContent, SearchSource
from ..search import WebSearcher, AcademicSearcher, ContentExtractor
from ..exceptions.base import ResearchError
from ..utils.logging import get_logger


class ResearchService:
    """Main service that coordinates research operations."""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize searchers
        self.web_searcher = WebSearcher(config.search)
        self.academic_searcher = AcademicSearcher(config.search)
        self.content_extractor = ContentExtractor(config.content)
    
    async def research(self, query: ResearchQuery) -> ResearchResult:
        """
        Perform comprehensive research on a query.
        
        Args:
            query: Research query parameters
            
        Returns:
            Complete research result
        """
        start_time = time.time()
        search_results = []
        extracted_content = []
        errors = []
        
        try:
            self.logger.info(f"Starting research: {query.query}")
            
            # Get extra results to account for potential invalid sources
            # Request 2-3x the needed results to ensure we have enough valid sources
            search_multiplier = 3
            expanded_results_needed = min(query.num_results * search_multiplier, self.config.search.max_results)
            
            # Perform searches based on source selection
            if query.sources in [SearchSource.WEB, SearchSource.BOTH]:
                try:
                    web_results = await self.web_searcher.search(query.query, expanded_results_needed)
                    search_results.extend(web_results)
                    self.logger.info(f"Retrieved {len(web_results)} web results")
                except Exception as e:
                    error_msg = f"Web search failed: {str(e)[:100]}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            if query.sources in [SearchSource.ACADEMIC, SearchSource.BOTH]:
                try:
                    academic_results = await self.academic_searcher.search(query.query, expanded_results_needed)
                    search_results.extend(academic_results)
                    self.logger.info(f"Retrieved {len(academic_results)} academic results")
                except Exception as e:
                    if "429" in str(e):
                        error_msg = f"Academic search rate limited - continuing with web results only"
                        self.logger.warning(error_msg)
                        errors.append(error_msg)
                    else:
                        error_msg = f"Academic search failed: {str(e)[:100]}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
            
            # If no results found, return early
            if not search_results:
                return self._create_empty_result(query, errors, time.time() - start_time)
            
            # Extract content from sources until we get the desired number of valid sources
            extracted_content = await self._extract_valid_content(search_results, query, errors)
            
            # Generate summary
            summary = self._generate_summary(query, search_results, extracted_content)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Research completed in {execution_time:.2f}s")
            
            return ResearchResult(
                query=query,
                search_results=search_results,
                extracted_content=extracted_content,
                summary=summary,
                total_sources=len(search_results),
                execution_time=execution_time,
                errors=errors
            )
            
        except Exception as e:
            self.logger.error(f"Research failed: {str(e)}")
            raise ResearchError(f"Research failed: {str(e)}")
    
    async def _extract_valid_content(self, search_results: List[SearchResult], query: ResearchQuery, errors: List[str]) -> List[ExtractedContent]:
        """
        Extract content from sources until we get the desired number of valid sources.
        
        Args:
            search_results: All available search results
            query: Research query with desired num_results
            errors: List to append errors to
            
        Returns:
            List of valid extracted content (up to query.num_results)
        """
        valid_content = []
        tried_sources = set()
        batch_size = min(3, len(search_results))  # Process in batches to be efficient
        
        self.logger.info(f"Target: {query.num_results} valid sources from {len(search_results)} available sources")
        
        # Get sources with proper balancing
        balanced_sources = self._select_sources_for_extraction(search_results, query)
        
        # Try to extract content in batches until we have enough valid sources
        source_index = 0
        max_iterations = 5  # Safety limit to prevent infinite loops
        iteration_count = 0
        
        while (len(valid_content) < query.num_results and 
               source_index < len(search_results) and 
               iteration_count < max_iterations):
            
            iteration_count += 1
            
            # Determine sources for this batch
            if source_index == 0:
                # First batch: use balanced selection
                current_batch = balanced_sources[:batch_size]
            else:
                # Subsequent batches: get next available sources
                available_sources = [s for s in search_results if s.url not in tried_sources]
                if not available_sources:
                    self.logger.info("No more available sources to try")
                    break
                current_batch = available_sources[:batch_size]
            
            if not current_batch:
                self.logger.info("No sources in current batch, stopping")
                break
                
            self.logger.info(f"Batch {source_index // batch_size + 1}: Trying {len(current_batch)} sources, need {query.num_results - len(valid_content)} more")
            
            # Extract content from current batch
            extraction_tasks = [
                self.content_extractor.extract_from_source(source) 
                for source in current_batch
            ]
            
            batch_content = await asyncio.gather(*extraction_tasks, return_exceptions=True)
            
            # Filter and validate content from this batch
            for i, content in enumerate(batch_content):
                source = current_batch[i]
                tried_sources.add(source.url)
                
                if isinstance(content, Exception):
                    error_msg = f"Content extraction failed for {source.url}: {str(content)[:100]}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
                elif content.error and "validation failed" in content.error.lower():
                    self.logger.info(f"Skipping invalid content from {content.url}: {content.error}")
                elif not content.content or len(content.content.strip()) < 50:
                    self.logger.info(f"Skipping source with insufficient content: {content.url}")
                else:
                    valid_content.append(content)
                    self.logger.info(f"Valid content found from {content.url} ({len(valid_content)}/{query.num_results})")
                    
                    # Stop if we have enough valid sources
                    if len(valid_content) >= query.num_results:
                        break
            
            source_index += batch_size
            
            # If we still need more sources, continue with next batch
            if len(valid_content) < query.num_results:
                self.logger.info(f"Need {query.num_results - len(valid_content)} more valid sources, continuing... (iteration {iteration_count})")
        
        if iteration_count >= max_iterations:
            self.logger.warning(f"Reached maximum iterations ({max_iterations}), stopping with {len(valid_content)} valid sources")
        
        self.logger.info(f"Content extraction completed: {len(valid_content)} valid sources from {len(tried_sources)} tried sources in {iteration_count} iterations")
        return valid_content
    
    def _select_sources_for_extraction(self, search_results: List[SearchResult], query: ResearchQuery) -> List[SearchResult]:
        """
        Select sources for content extraction based on source balancing.
        
        Args:
            search_results: Available search results
            query: Original query
            
        Returns:
            List of SearchResult objects
        """
        if query.sources == SearchSource.BOTH:
            # Balance between web and academic sources
            web_results = [r for r in search_results if r.source_type == "web"]
            academic_results = [r for r in search_results if r.source_type == "academic"]
            
            combined_sources = []
            max_per_type = max(1, query.num_results // 2)
            
            # Interleave sources
            for i in range(max(len(web_results), len(academic_results))):
                if len(combined_sources) >= query.num_results:
                    break
                if i < len(web_results) and len([s for s in combined_sources if s.source_type == "web"]) < max_per_type:
                    combined_sources.append(web_results[i])
                if i < len(academic_results) and len([s for s in combined_sources if s.source_type == "academic"]) < max_per_type:
                    combined_sources.append(academic_results[i])
            
            return combined_sources[:query.num_results]
        else:
            # Single source type
            return search_results[:query.num_results]
    
    def _generate_summary(self, query: ResearchQuery, search_results: List[SearchResult], extracted_content: List[ExtractedContent]) -> str:
        """Generate a summary of the research."""
        source_text = "web and academic databases" if query.sources == SearchSource.BOTH else f"{query.sources.value} sources"
        
        summary = f"Completed research on: {query.query}\n"
        summary += f"Found {len(search_results)} potential sources from {source_text}\n"
        summary += f"Successfully extracted valid content from {len(extracted_content)} high-quality sources"
        
        # Add target achievement info
        if len(extracted_content) == query.num_results:
            summary += f" (target of {query.num_results} achieved)\n"
        elif len(extracted_content) < query.num_results:
            summary += f" (target was {query.num_results}, but only {len(extracted_content)} valid sources found)\n"
        else:
            summary += f" (exceeded target of {query.num_results})\n"
        
        if len(extracted_content) < len(search_results):
            filtered_count = len(search_results) - len(extracted_content)
            summary += f"Filtered out {filtered_count} sources with restricted access or low-quality content\n"
        
        summary += "The information above represents the most relevant and accessible content found on this topic."
        
        return summary
    
    def _create_empty_result(self, query: ResearchQuery, errors: List[str], execution_time: float) -> ResearchResult:
        """Create an empty result when no sources are found."""
        return ResearchResult(
            query=query,
            search_results=[],
            extracted_content=[],
            summary="No valid search results found. Please try a different query.",
            total_sources=0,
            execution_time=execution_time,
            errors=errors
        )