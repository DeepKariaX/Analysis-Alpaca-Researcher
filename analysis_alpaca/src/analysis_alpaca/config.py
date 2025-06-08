"""Configuration settings for AnalysisAlpaca."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class SearchConfig:
    """Configuration for search operations."""
    max_results: int = 10
    default_num_results: int = 2
    web_timeout: float = 10.0
    academic_timeout: float = 5.0
    extraction_timeout: float = 8.0
    max_snippet_length: int = 200
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


@dataclass
class ContentConfig:
    """Configuration for content processing."""
    max_content_size: int = 8000
    max_extraction_size: int = 100000
    max_paragraphs: int = 5
    max_elements: int = 8
    max_snippet_length: int = 200
    extraction_timeout: float = 8.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""
    name: str = "analysis-alpaca"
    log_level: str = "INFO"
    log_file: Optional[str] = None
    auto_install_deps: bool = True


@dataclass
class Settings:
    """Main settings class combining all configurations."""
    search: SearchConfig = field(default_factory=SearchConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        settings = cls()
        
        # Search config from env
        if max_results := os.getenv("AA_MAX_RESULTS"):
            settings.search.max_results = int(max_results)
        
        if default_num := os.getenv("AA_DEFAULT_NUM_RESULTS"):
            settings.search.default_num_results = int(default_num)
        
        if web_timeout := os.getenv("AA_WEB_TIMEOUT"):
            settings.search.web_timeout = float(web_timeout)
        
        if user_agent := os.getenv("AA_USER_AGENT"):
            settings.search.user_agent = user_agent
        
        # Content config from env
        if max_content := os.getenv("AA_MAX_CONTENT_SIZE"):
            settings.content.max_content_size = int(max_content)
        
        # Server config from env
        if log_level := os.getenv("AA_LOG_LEVEL"):
            settings.server.log_level = log_level.upper()
        
        if log_file := os.getenv("AA_LOG_FILE"):
            settings.server.log_file = log_file
        
        if auto_install := os.getenv("AA_AUTO_INSTALL_DEPS"):
            settings.server.auto_install_deps = auto_install.lower() in ("true", "1", "yes")
        
        return settings
    
    def get_log_level(self) -> int:
        """Get numeric log level."""
        import logging
        return getattr(logging, self.server.log_level, logging.INFO)


# Global settings instance
settings = Settings.from_env()