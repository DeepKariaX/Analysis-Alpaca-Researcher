#!/usr/bin/env python3
"""
FastAPI backend for AnalysisAlpaca Web UI.
Communicates with the MCP server and generates research reports.
"""

import os
import json
import asyncio
import subprocess
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AnalysisAlpaca API",
    description="Backend API for AnalysisAlpaca Web Application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Pydantic models
class ResearchRequest(BaseModel):
    query: str = Field(..., description="Research query or topic")
    sources: str = Field(default="both", description="Source type: web, academic, or both")
    num_results: int = Field(default=2, description="Number of sources to examine")
    llm_provider: str = Field(default="openai", description="LLM provider: openai, anthropic, or groq")
    model: str = Field(default="gpt-4", description="Model to use for report generation")

class ResearchProgress(BaseModel):
    status: str
    message: str
    progress: int
    timestamp: datetime

class ResearchResult(BaseModel):
    id: str
    query: str
    sources: str
    num_results: int
    status: str
    progress: int
    raw_data: Optional[str] = None
    report: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

# In-memory storage for research jobs
research_jobs: Dict[str, ResearchResult] = {}
research_progress: Dict[str, List[ResearchProgress]] = {}

class MCPClient:
    """Client for communicating with the MCP HTTP server."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    async def deep_research(self, query: str, sources: str = "both", num_results: int = 2) -> str:
        """Call the deep_research endpoint via HTTP."""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # 2 minute timeout
                response = await client.post(
                    f"{self.base_url}/deep_research",
                    json={
                        "query": query,
                        "sources": sources,
                        "num_results": num_results
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["result"]
                else:
                    error_detail = response.json().get("detail", f"HTTP {response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"MCP server error: {error_detail}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to MCP server at {self.base_url}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MCP research failed: {str(e)}")
    
    async def health_check(self) -> dict:
        """Check if MCP server is healthy."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

class LLMClient:
    """Client for generating reports using various LLM providers."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.groq_client = None
        
        if OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            except ImportError:
                pass
                
        if ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            except ImportError:
                pass
                
        if GROQ_API_KEY:
            try:
                from groq import AsyncGroq
                self.groq_client = AsyncGroq(api_key=GROQ_API_KEY)
            except ImportError:
                pass
    
    async def generate_report(self, raw_data: str, query: str, provider: str = "openai", model: str = "gpt-4") -> str:
        """Generate a comprehensive research report."""
        
        prompt = f"""Based on the following research data, create a comprehensive research report on: "{query}"

Research Data:
{raw_data}

Please create a well-structured report with the following sections:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Sources and References
5. Conclusions and Implications

Format the output in clean markdown with proper headings, bullet points, and citations where appropriate.
Make the report professional, comprehensive, and easy to read.
"""

        try:
            if provider == "openai" and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional research analyst creating comprehensive reports."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.1
                )
                return response.choices[0].message.content
                
            elif provider == "anthropic" and self.anthropic_client:
                message = await self.anthropic_client.messages.create(
                    model=model if model.startswith("claude") else "claude-3-sonnet-20240229",
                    max_tokens=4000,
                    temperature=0.1,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text if message.content else "Failed to generate report"
                
            elif provider == "groq" and self.groq_client:
                response = await self.groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional research analyst creating comprehensive reports."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.1
                )
                return response.choices[0].message.content
                
            else:
                # Fallback: basic formatting of raw data
                return f"""# Research Report: {query}

## Executive Summary
This report compiles research findings on {query} from multiple sources.

## Research Data
{raw_data}

## Conclusion
The above data provides insights into {query}. Further analysis may be needed for specific use cases.

*Note: This is a basic report. Configure OpenAI, Anthropic, or Groq API keys for enhanced report generation.*
"""
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

# Initialize clients
mcp_client = MCPClient(MCP_SERVER_URL)
llm_client = LLMClient()

async def process_research_job(job_id: str, request: ResearchRequest):
    """Background task to process research job."""
    try:
        # Update progress
        def update_progress(status: str, message: str, progress: int):
            if job_id not in research_progress:
                research_progress[job_id] = []
            research_progress[job_id].append(ResearchProgress(
                status=status,
                message=message,
                progress=progress,
                timestamp=datetime.now()
            ))
            research_jobs[job_id].status = status
            research_jobs[job_id].progress = progress
        
        update_progress("researching", "Starting deep research...", 10)
        print(f"[DEBUG] Job {job_id}: Started research for query '{request.query}' with sources '{request.sources}'")
        
        # Small delay to ensure frontend can catch this status
        await asyncio.sleep(0.5)
        update_progress("researching", "Searching sources and extracting content...", 30)
        
        # Perform research via MCP
        raw_data = await mcp_client.deep_research(
            query=request.query,
            sources=request.sources,
            num_results=request.num_results
        )
        
        research_jobs[job_id].raw_data = raw_data
        print(f"[DEBUG] Job {job_id}: Research completed, got {len(raw_data)} characters of data")
        update_progress("generating", "Generating comprehensive report...", 60)
        
        # Generate report using LLM
        report = await llm_client.generate_report(
            raw_data=raw_data,
            query=request.query,
            provider=request.llm_provider,
            model=request.model
        )
        
        research_jobs[job_id].report = report
        research_jobs[job_id].completed_at = datetime.now()
        print(f"[DEBUG] Job {job_id}: Report generated, marking as completed")
        update_progress("completed", "Research report completed successfully!", 100)
        
    except Exception as e:
        research_jobs[job_id].error = str(e)
        research_jobs[job_id].status = "failed"
        if job_id not in research_progress:
            research_progress[job_id] = []
        research_progress[job_id].append(ResearchProgress(
            status="failed",
            message=f"Research failed: {str(e)}",
            progress=0,
            timestamp=datetime.now()
        ))

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AnalysisAlpaca API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check MCP server health
    mcp_health = await mcp_client.health_check()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "mcp_server": mcp_health
    }

@app.post("/research", response_model=ResearchResult)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research job."""
    job_id = f"research_{int(time.time())}_{hash(request.query) % 10000}"
    
    # Create job record
    job = ResearchResult(
        id=job_id,
        query=request.query,
        sources=request.sources,
        num_results=request.num_results,
        status="queued",
        progress=0,
        created_at=datetime.now()
    )
    
    research_jobs[job_id] = job
    
    # Start background processing
    background_tasks.add_task(process_research_job, job_id, request)
    
    return job

@app.get("/research/{job_id}", response_model=ResearchResult)
async def get_research_status(job_id: str):
    """Get research job status and results."""
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    return research_jobs[job_id]

@app.get("/research/{job_id}/progress")
async def get_research_progress(job_id: str):
    """Get detailed progress for a research job."""
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    job = research_jobs[job_id]
    progress_list = research_progress.get(job_id, [])
    
    print(f"[DEBUG] Progress request for job {job_id}: status={job.status}, progress={job.progress}%, progress_items={len(progress_list)}")
    
    return {
        "job": job,
        "progress": progress_list
    }

@app.get("/research")
async def list_research_jobs():
    """List all research jobs."""
    return {"jobs": list(research_jobs.values())}

@app.delete("/research/{job_id}")
async def delete_research_job(job_id: str):
    """Delete a research job."""
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    del research_jobs[job_id]
    if job_id in research_progress:
        del research_progress[job_id]
    
    return {"message": "Research job deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)