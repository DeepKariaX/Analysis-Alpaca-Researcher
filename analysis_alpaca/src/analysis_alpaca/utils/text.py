"""Text processing utilities."""

import re
from typing import Optional


def safe_truncate(
    text: str, 
    max_length: int, 
    suffix: str = "...\n[Content truncated due to size limits]"
) -> str:
    """
    Safely truncate text to max_length with a suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of the result
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text with suffix if needed
    """
    if not text or len(text) <= max_length:
        return text
    
    # Try to truncate at a paragraph boundary
    last_para_break = text[:max_length-50].rfind("\n\n")
    if last_para_break > max_length // 2:
        return text[:last_para_break] + "\n\n" + suffix
    
    return text[:max_length] + suffix


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common unwanted characters
    text = re.sub(r'[^\w\s\-.,;:!?()[\]{}"\'/]', '', text)
    
    return text.strip()


def extract_urls(text: str) -> list[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text containing URLs
        
    Returns:
        List of extracted URLs
    """
    url_pattern = r'https?://[^\s<>"\'{}|\\^`[\]]+'
    return re.findall(url_pattern, text)