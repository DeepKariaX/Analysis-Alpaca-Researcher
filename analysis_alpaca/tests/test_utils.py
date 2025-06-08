"""Tests for utility functions."""

import pytest
from analysis_alpaca.utils.text import safe_truncate, clean_text, extract_urls


def test_safe_truncate():
    """Test safe text truncation."""
    # Short text should not be truncated
    short_text = "This is short"
    result = safe_truncate(short_text, 100)
    assert result == short_text
    
    # Long text should be truncated
    long_text = "x" * 200
    result = safe_truncate(long_text, 50)
    assert len(result) <= 50 + len("...\n[Content truncated due to size limits]")
    assert result.endswith("[Content truncated due to size limits]")
    
    # Test paragraph boundary truncation
    text_with_paragraphs = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    result = safe_truncate(text_with_paragraphs, 30)
    assert "First paragraph." in result
    assert result.endswith("[Content truncated due to size limits]")


def test_clean_text():
    """Test text cleaning."""
    # Test whitespace normalization
    messy_text = "  Too   much    whitespace  "
    result = clean_text(messy_text)
    assert result == "Too much whitespace"
    
    # Test empty text
    assert clean_text("") == ""
    assert clean_text(None) == ""
    
    # Test special character removal
    text_with_special = "Text with special chars: ♠♣♥♦"
    result = clean_text(text_with_special)
    assert "♠" not in result
    assert "Text with special chars" in result


def test_extract_urls():
    """Test URL extraction."""
    text_with_urls = "Visit https://example.com and http://test.org for more info"
    urls = extract_urls(text_with_urls)
    
    assert len(urls) == 2
    assert "https://example.com" in urls
    assert "http://test.org" in urls
    
    # Test with no URLs
    text_without_urls = "No URLs here"
    urls = extract_urls(text_without_urls)
    assert len(urls) == 0