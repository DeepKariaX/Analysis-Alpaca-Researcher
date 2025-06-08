"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, AsyncMock
import httpx

from analysis_alpaca.config import Settings, SearchConfig, ContentConfig, ServerConfig
from analysis_alpaca.core.research_service import ResearchService


@pytest.fixture
def test_settings():
    """Test settings fixture."""
    return Settings(
        search=SearchConfig(
            max_results=3,
            default_num_results=2,
            web_timeout=5.0,
            academic_timeout=5.0,
            extraction_timeout=5.0
        ),
        content=ContentConfig(
            max_content_size=1000,
            max_extraction_size=10000
        ),
        server=ServerConfig(
            name="test-server",
            log_level="ERROR"
        )
    )


@pytest.fixture
def research_service(test_settings):
    """Research service fixture."""
    return ResearchService(test_settings)


@pytest.fixture
def mock_httpx_response():
    """Mock HTTP response fixture."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.headers = {"content-type": "text/html"}
    response.text = "<html><title>Test</title><body><p>Test content</p></body></html>"
    response.raise_for_status = Mock()
    return response


@pytest.fixture
def mock_search_results():
    """Mock search results fixture."""
    from analysis_alpaca.models.research import SearchResult
    
    return [
        SearchResult(
            title="Test Result 1",
            url="https://example.com/1",
            snippet="Test snippet 1",
            source_type="web"
        ),
        SearchResult(
            title="Test Result 2", 
            url="https://example.com/2",
            snippet="Test snippet 2",
            source_type="academic"
        )
    ]