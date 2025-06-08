"""Tests for data models."""

import pytest
from analysis_alpaca.models.research import ResearchQuery, SearchSource, ResearchResult, SearchResult


def test_research_query_validation():
    """Test research query validation."""
    # Valid query
    query = ResearchQuery("test query", SearchSource.WEB, 2)
    assert query.query == "test query"
    assert query.sources == SearchSource.WEB
    assert query.num_results == 2
    
    # Empty query should raise error
    with pytest.raises(ValueError, match="Query cannot be empty"):
        ResearchQuery("", SearchSource.WEB, 2)
    
    # Invalid num_results
    with pytest.raises(ValueError, match="Number of results must be between 1 and 5"):
        ResearchQuery("test", SearchSource.WEB, 0)
    
    with pytest.raises(ValueError, match="Number of results must be between 1 and 5"):
        ResearchQuery("test", SearchSource.WEB, 10)


def test_research_query_string_source_conversion():
    """Test automatic conversion of string sources."""
    query = ResearchQuery("test", "web", 2)
    assert query.sources == SearchSource.WEB
    
    query = ResearchQuery("test", "academic", 2)
    assert query.sources == SearchSource.ACADEMIC
    
    query = ResearchQuery("test", "invalid", 2)
    assert query.sources == SearchSource.BOTH


def test_research_result_format_output():
    """Test research result formatting."""
    from analysis_alpaca.models.research import ExtractedContent
    from datetime import datetime
    
    query = ResearchQuery("test query", SearchSource.BOTH, 2)
    search_results = [
        SearchResult("Title 1", "https://example.com/1", "Snippet 1", "web"),
        SearchResult("Title 2", "https://example.com/2", "Snippet 2", "academic")
    ]
    extracted_content = [
        ExtractedContent("Title 1", "https://example.com/1", "Desc 1", "Content 1", datetime.now())
    ]
    
    result = ResearchResult(
        query=query,
        search_results=search_results,
        extracted_content=extracted_content,
        summary="Test summary",
        total_sources=2,
        execution_time=1.5,
        errors=[]
    )
    
    output = result.format_output()
    
    assert "Research Query: test query" in output
    assert "SEARCH RESULTS:" in output
    assert "Title 1" in output
    assert "Title 2" in output
    assert "DETAILED CONTENT" in output
    assert "RESEARCH SUMMARY:" in output
    assert "Test summary" in output


def test_research_result_truncation():
    """Test content truncation in research results."""
    query = ResearchQuery("test", SearchSource.WEB, 1)
    
    # Create a result with very long content
    long_content = "x" * 1000
    search_results = [SearchResult("Title", "https://example.com", "Snippet", "web")]
    
    from analysis_alpaca.models.research import ExtractedContent
    from datetime import datetime
    
    extracted_content = [
        ExtractedContent("Title", "https://example.com", "Desc", long_content, datetime.now())
    ]
    
    result = ResearchResult(
        query=query,
        search_results=search_results,
        extracted_content=extracted_content,
        summary="Summary",
        total_sources=1,
        execution_time=1.0,
        errors=[]
    )
    
    # Test with small max size
    output = result.format_output(max_size=100)
    assert len(output) <= 100
    assert "[Content truncated due to size limits]" in output