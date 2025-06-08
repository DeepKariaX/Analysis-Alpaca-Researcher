"""
AnalysisAlpaca - MCP Server for Comprehensive Research

A production-ready MCP server that provides unified research capabilities
for web and academic searches with content extraction.
"""

__version__ = "1.0.0"
__author__ = "AnalysisAlpaca Team"
__description__ = "MCP server for comprehensive research capabilities"

from .core.server import create_server
from .models.research import ResearchQuery, ResearchResult

__all__ = [
    "create_server",
    "ResearchQuery", 
    "ResearchResult",
]