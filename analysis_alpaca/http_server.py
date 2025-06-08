#!/usr/bin/env python3
"""
HTTP wrapper for the AnalysisAlpaca MCP server.
This allows the MCP functionality to be accessed via REST API calls.
"""

import sys
import asyncio
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from analysis_alpaca.core.research_service import ResearchService
from analysis_alpaca.models.research import ResearchQuery, SearchSource
from analysis_alpaca.config import Settings
from analysis_alpaca.utils.logging import setup_logging

# Initialize FastAPI app
app = FastAPI(
    title="AnalysisAlpaca MCP HTTP Server",
    description="HTTP wrapper for AnalysisAlpaca MCP functionality",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
settings = Settings.from_env()
research_service = ResearchService(settings)
logger = setup_logging(
    level=settings.get_log_level(),
    log_file=settings.server.log_file
).getChild("http_server")

# Pydantic models for API
class DeepResearchRequest(BaseModel):
    query: str = Field(..., description="Research query or topic")
    sources: str = Field(default="both", description="Source type: web, academic, or both")
    num_results: int = Field(default=2, description="Number of sources to examine")

class DeepResearchResponse(BaseModel):
    query: str
    sources: str
    num_results: int
    result: str
    execution_time: float
    timestamp: datetime
    total_sources: int
    errors: list

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    mcp_settings: dict

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AnalysisAlpaca MCP HTTP Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "research": "/deep_research",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        mcp_settings={
            "max_results": settings.search.max_results,
            "default_num_results": settings.search.default_num_results,
            "web_timeout": settings.search.web_timeout,
            "max_content_size": settings.content.max_content_size
        }
    )

@app.post("/deep_research", response_model=DeepResearchResponse)
async def deep_research_endpoint(request: DeepResearchRequest):
    """
    Perform comprehensive research on a topic and return detailed information.
    
    This endpoint mirrors the MCP tool functionality but via HTTP.
    """
    start_time = time.time()
    
    try:
        logger.info(f"HTTP Research request: query='{request.query}', sources='{request.sources}', num_results={request.num_results}")
        
        # Validate and limit num_results
        if request.num_results > settings.search.max_results:
            request.num_results = settings.search.max_results
            logger.warning(f"num_results limited to {settings.search.max_results}")
        
        # Map sources string to enum
        source_map = {
            "web": SearchSource.WEB,
            "academic": SearchSource.ACADEMIC, 
            "both": SearchSource.BOTH
        }
        
        if request.sources not in source_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid sources value. Must be one of: {list(source_map.keys())}"
            )
        
        # Create research query
        research_query = ResearchQuery(
            query=request.query,
            sources=source_map[request.sources],
            num_results=request.num_results
        )
        
        # Perform research
        result = await research_service.research(research_query)
        
        # Format result
        formatted_result = result.format_output(settings.content.max_content_size)
        
        execution_time = time.time() - start_time
        
        logger.info(f"HTTP Research completed: {len(formatted_result)} characters returned in {execution_time:.2f}s")
        
        return DeepResearchResponse(
            query=request.query,
            sources=request.sources,
            num_results=request.num_results,
            result=formatted_result,
            execution_time=execution_time,
            timestamp=datetime.now(),
            total_sources=result.total_sources,
            errors=result.errors
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_msg = f"Research error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/settings")
async def get_settings():
    """Get current MCP server settings."""
    return {
        "search": {
            "max_results": settings.search.max_results,
            "default_num_results": settings.search.default_num_results,
            "web_timeout": settings.search.web_timeout,
            "academic_timeout": settings.search.academic_timeout,
            "extraction_timeout": settings.search.extraction_timeout,
            "user_agent": settings.search.user_agent
        },
        "content": {
            "max_content_size": settings.content.max_content_size,
            "max_extraction_size": settings.content.max_extraction_size,
            "max_paragraphs": settings.content.max_paragraphs,
            "max_elements": settings.content.max_elements,
            "max_snippet_length": settings.content.max_snippet_length
        },
        "server": {
            "name": settings.server.name,
            "log_level": settings.server.log_level,
            "auto_install_deps": settings.server.auto_install_deps
        }
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("AnalysisAlpaca MCP HTTP Server starting up...")
    logger.info(f"Max results: {settings.search.max_results}")
    logger.info(f"Default results: {settings.search.default_num_results}")
    logger.info(f"Max content size: {settings.content.max_content_size}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("AnalysisAlpaca MCP HTTP Server shutting down...")

def main():
    """Main entry point for the HTTP server."""
    logger.info("Starting AnalysisAlpaca MCP HTTP Server on port 8001...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()