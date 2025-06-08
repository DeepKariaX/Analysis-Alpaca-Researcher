"""MCP server implementation."""

import sys
from contextlib import asynccontextmanager
from typing import Optional

from ..models.research import ResearchQuery, SearchSource
from ..core.research_service import ResearchService
from ..utils.logging import setup_logging
from ..config import Settings
from ..exceptions.base import ResearchError


def install_dependencies():
    """Install required dependencies if not available."""
    try:
        import httpx
        import bs4
        import mcp
    except ImportError:
        print("Installing required dependencies...")
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "httpx", "beautifulsoup4", "mcp"
        ])


@asynccontextmanager
async def lifespan(app):
    """Context manager for server lifecycle."""
    logger = setup_logging().getChild("server")
    logger.info("Server starting up...")
    yield {}
    logger.info("Server shutting down...")


def create_server(settings: Optional[Settings] = None):
    """
    Create and configure the MCP server.
    
    Args:
        settings: Optional settings override
        
    Returns:
        Configured FastMCP server
    """
    if settings is None:
        settings = Settings.from_env()
    
    # Auto-install dependencies if enabled
    if settings.server.auto_install_deps:
        install_dependencies()
    
    # Import after potential installation
    from mcp.server.fastmcp import FastMCP
    
    # Set up logging
    logger = setup_logging(
        level=settings.get_log_level(),
        log_file=settings.server.log_file
    )
    
    # Initialize the MCP server
    mcp = FastMCP(
        settings.server.name,
        dependencies=["httpx", "beautifulsoup4"],
        lifespan=lifespan
    )
    
    # Initialize research service
    research_service = ResearchService(settings)
    
    @mcp.tool()
    async def deep_research(query: str, sources: str = "both", num_results: int = 2) -> str:
        """
        Perform comprehensive research on a topic and return detailed information.

        Args:
            query: The research question or topic
            sources: Which sources to use: "web" for general info, "academic" for scholarly sources, "both" for all sources
            num_results: Number of sources to examine (default 2, max based on config)

        Returns:
            Comprehensive research results combining multiple sources
        """
        try:
            logger.info(f"Research request: query='{query}', sources='{sources}', num_results={num_results}")
            
            # Validate and limit num_results
            if num_results > settings.search.max_results:
                num_results = settings.search.max_results
                logger.warning(f"num_results limited to {settings.search.max_results}")
            
            # Create research query
            research_query = ResearchQuery(
                query=query,
                sources=sources,
                num_results=num_results
            )
            
            # Perform research
            result = await research_service.research(research_query)
            
            # Format and return result
            formatted_result = result.format_output(settings.content.max_content_size)
            
            logger.info(f"Research completed: {len(formatted_result)} characters returned")
            return formatted_result
            
        except Exception as e:
            error_msg = f"Research error: {str(e)[:200]}"
            logger.error(error_msg)
            return error_msg

    @mcp.prompt()
    def research_prompt(topic: str) -> str:
        """
        Create a prompt for comprehensive, multi-stage research on a topic.

        Args:
            topic: The topic to research

        Returns:
            A prompt for comprehensive iterative research with APA citations
        """
        return (
            f"I need to do comprehensive research on: {topic}\\n\\n"
            f"Please follow this multi-step research process:\\n\\n"
            f"1. INITIAL EXPLORATION: Use the deep_research tool to gather information from both web and academic sources.\\n\\n"
            f"2. PRELIMINARY SYNTHESIS: Organize the key findings, identifying main concepts, perspectives, and knowledge gaps. "
            f"Create an artifact for your synthesis to improve readability and organization. Include sections for methodology, "
            f"key findings, and areas requiring further investigation.\\n\\n"
            f"3. VISUAL REPRESENTATION: Where appropriate, create data visualizations to illustrate key concepts, trends, "
            f"or relationships found in the research. Consider using:\\n"
            f"   - Timeline charts for historical developments\\n"
            f"   - Comparison tables for contrasting perspectives\\n"
            f"   - Concept maps to show relationships between ideas\\n"
            f"   - Flowcharts to illustrate processes\\n"
            f"   - Bar/pie charts for statistical information\\n"
            f"Present these visualizations as part of your analysis artifact.\\n\\n"
            f"4. FOLLOW-UP RESEARCH: Based on the initial findings, identify 2-3 specific aspects that need deeper investigation. "
            f"Conduct targeted follow-up research on these aspects using the deep_research tool again with more specific queries.\\n\\n"
            f"5. COMPREHENSIVE SYNTHESIS: Integrate all gathered information into a coherent summary that explains the main points, "
            f"different perspectives, and current understanding of the topic. Highlight how the follow-up research addressed the "
            f"knowledge gaps or expanded on key concepts from the initial exploration. Create a final artifact that includes:\\n"
            f"   - Executive summary\\n"
            f"   - Methodology\\n"
            f"   - Key findings with visualizations\\n"
            f"   - Analysis and interpretation\\n"
            f"   - Conclusions and implications\\n\\n"
            f"6. REFERENCES: Include a properly formatted reference list at the end in APA 7th edition format. For each source used in your synthesis, create "
            f"an appropriate citation. When exact publication dates are unavailable, use the best available information (like website "
            f"copyright dates or 'n.d.' if no date is found). Format web sources as:\\n"
            f"Author, A. A. (Year, Month Day). Title of page. Site Name. URL\\n\\n"
            f"For academic sources, use:\\n"
            f"Author, A. A., & Author, B. B. (Year). Title of article. Journal Name, Volume(Issue), page range. DOI or URL\\n\\n"
            f"This iterative approach with proper citations and visual elements will provide a thorough understanding of {topic} "
            f"that integrates information from multiple authoritative sources and presents it in a well-organized, visually "
            f"enhanced format."
        )
    
    return mcp


def run_server():
    """Run the server with default settings."""
    try:
        settings = Settings.from_env()
        logger = setup_logging(
            level=settings.get_log_level(),
            log_file=settings.server.log_file
        )
        
        logger.info("Starting AnalysisAlpaca MCP server...")
        
        mcp = create_server(settings)
        mcp.run()
        
    except Exception as e:
        logger = setup_logging()
        logger.critical(f"Fatal error: {str(e)}")
        sys.exit(1)