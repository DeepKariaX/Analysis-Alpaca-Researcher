# AnalysisAlpaca 🦙

A production-ready MCP (Model Context Protocol) server that enables comprehensive research and analysis capabilities for Claude and other MCP-compatible AI assistants. This server integrates web and academic search functionality with an optional web interface for interactive research and AI-powered report generation.

## 🚀 Quick Start

```bash
# 1. Clone and navigate to the project
cd analysis_alpaca

# 2. Install dependencies (use virtual environment recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# 3. Start the MCP server
python http_server.py

# Server runs on http://localhost:8001
# API documentation: http://localhost:8001/docs
```

**For Web Interface (Optional):**
See the [Web Interface](#-web-interface-optional) section below for manual setup instructions.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Web Interface](#-web-interface)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## ✨ Features

### Core Research Capabilities
- **Multi-Source Search**: Combines DuckDuckGo web search and Semantic Scholar academic research
- **Content Extraction**: Intelligent extraction of relevant information from web pages
- **Academic Integration**: Direct access to scholarly articles and research papers
- **Smart Formatting**: Properly formatted research with citations and structured output
- **Rate Limiting**: Built-in retry logic and graceful handling of API limits

### Web Interface Features
- **Interactive Research**: User-friendly web interface for conducting research
- **Job Management**: Track multiple research jobs with progress monitoring
- **AI-Powered Reports**: Generate comprehensive PDF reports using OpenAI, Anthropic, or Groq
- **PDF Export**: Download research results as properly named PDF files
- **Real-time Updates**: Live progress tracking with WebSocket-like polling

### Production Features
- **Comprehensive Error Handling**: Graceful degradation when services are unavailable
- **Extensive Logging**: Detailed logging for debugging and monitoring
- **Configurable Settings**: Environment-based configuration management
- **Auto-Dependency Installation**: Automatic installation of missing dependencies
- **Modular Architecture**: Easy to extend and customize

## 🏗 Architecture

### Components Overview

```
analysis_alpaca/
├── src/analysis_alpaca/          # Core MCP server implementation
│   ├── core/                     # Server and research orchestration
│   ├── search/                   # Search engine implementations
│   ├── models/                   # Data models and schemas
│   ├── utils/                    # Utility functions and helpers
│   └── exceptions/               # Custom exception handling
├── web_ui/                       # Optional web interface
│   ├── frontend/                 # React.js frontend application
│   └── backend/                  # FastAPI backend for web UI
├── tests/                        # Test suite
├── http_server.py               # HTTP API wrapper for MCP server
└── requirements.txt             # Unified dependencies
```

### Core Components

1. **MCP Server** (`src/analysis_alpaca/core/server.py`)
   - FastMCP-based server exposing research tools to Claude
   - Main tool: `deep_research()` for comprehensive research
   - Built-in prompt templates for structured research methodology

2. **Research Service** (`src/analysis_alpaca/core/research_service.py`)
   - Orchestrates the entire research workflow
   - Coordinates web and academic searches
   - Manages content extraction and result formatting
   - Handles parallel execution and error recovery

3. **Search Implementations**
   - **WebSearcher**: DuckDuckGo web search with result parsing
   - **AcademicSearcher**: Semantic Scholar API integration with retry logic
   - **ContentExtractor**: Web page content extraction and processing

4. **HTTP Server** (`http_server.py`)
   - REST API wrapper for MCP functionality
   - Enables direct HTTP access to research capabilities
   - CORS-enabled for web interface integration

5. **Web Interface**
   - **Frontend**: React.js application with PDF generation
   - **Backend**: FastAPI server for job management and AI report generation

## 🔧 Installation

### Prerequisites

- **Python 3.8+** (recommended: Python 3.11+)
- **Node.js 16+** (only if using web interface)
- **npm or yarn** (only if using web interface)

### Basic Installation

```bash
# Clone the repository
git clone <repository-url>
cd analysis_alpaca

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Or install with all optional dependencies
pip install -e ".[dev,ai]"
```

### Web Interface Setup

```bash
# Install frontend dependencies
cd web_ui/frontend
npm install

# Return to project root
cd ../..
```

### Dependencies Overview

**Core Dependencies:**
- `httpx>=0.25.0` - HTTP client for API requests
- `beautifulsoup4>=4.12.0` - HTML parsing for content extraction
- `mcp>=0.1.0` - Model Context Protocol server framework
- `fastapi>=0.104.0` - Web framework for HTTP API
- `uvicorn>=0.24.0` - ASGI server for FastAPI

**Optional AI Dependencies:**
```bash
pip install -e ".[ai]"  # Installs OpenAI, Anthropic, and Groq clients
```

**Development Dependencies:**
```bash
pip install -e ".[dev]"  # Installs testing and linting tools
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Search Configuration
AA_MAX_RESULTS=5              # Maximum results per search
AA_DEFAULT_NUM_RESULTS=3      # Default number of results
AA_WEB_TIMEOUT=15.0          # Web search timeout (seconds)
AA_USER_AGENT="AnalysisAlpaca 1.0"

# Content Configuration
AA_MAX_CONTENT_SIZE=10000    # Maximum response size
AA_MAX_EXTRACTION_SIZE=150000 # Maximum content to extract

# Server Configuration
AA_LOG_LEVEL=INFO            # Logging level (DEBUG, INFO, WARNING, ERROR)
AA_LOG_FILE="logs/research.log"  # Optional log file path
AA_AUTO_INSTALL_DEPS=true    # Auto-install missing dependencies

# AI Provider API Keys (Optional - for web interface)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here

# Web UI Configuration
MCP_SERVER_URL=http://localhost:8001  # URL of the MCP HTTP server
```

### Configuration Files

The system uses a hierarchical configuration approach:
1. Default values in `config.py`
2. Environment variables (override defaults)
3. Optional `.env` file (override environment)

## 🚀 Usage

### MCP Server

```json
{
  "mcpServers": {
    "analysis-alpaca": {
      "command": "/path/to/python",
      "args": ["/path/to/analysis_alpaca/http_server.py"],
      "env": {
        "AA_MAX_RESULTS": "5",
        "AA_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Standalone HTTP Server

```bash
# Start the HTTP API server
python http_server.py

# Server runs on http://localhost:8001
# API documentation available at http://localhost:8001/docs
```

### Web Interface (Optional)

The web interface provides a user-friendly way to interact with AnalysisAlpaca through a browser.

**Requirements:**
- Node.js 16+ and npm for the frontend
- The MCP HTTP server must be running (see above)

**Setup:**
```bash
# Install frontend dependencies
cd web_ui/frontend
npm install
cd ../..
```

**Manual Startup (2 terminals required):**

**Terminal 1 - Backend API Server:**
```bash
cd web_ui/backend
python main.py

# Backend runs on http://localhost:8000
# API documentation: http://localhost:8000/docs
```

**Terminal 2 - Frontend Development Server:**
```bash
cd web_ui/frontend
npm start

# Frontend runs on http://localhost:3000
# Access the web interface at http://localhost:3000
```

**Complete Setup (3 servers total):**
1. **MCP Server** (Terminal 1): `python http_server.py` → http://localhost:8001
2. **Backend API** (Terminal 2): `cd web_ui/backend && python main.py` → http://localhost:8000  
3. **Frontend UI** (Terminal 3): `cd web_ui/frontend && npm start` → http://localhost:3000

### Research Tool Usage

The main `deep_research` tool accepts these parameters:

- **query** (required): The research question or topic
- **sources** (optional): "web", "academic", or "both" (default: "both")
- **num_results** (optional): Number of sources to examine (default: 2)

#### Example Prompts for Claude

```
Research the latest developments in quantum computing using both web and academic sources.

Can you do comprehensive research on climate change mitigation strategies? Focus on academic sources and examine 3 results.

I need detailed information about the impact of artificial intelligence on healthcare. Use the deep_research tool with web sources only.
```

#### Direct API Usage

```bash
# Research via HTTP API
curl -X POST "http://localhost:8001/deep_research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence in healthcare",
    "sources": "both",
    "num_results": 3
  }'
```

## 🌐 Web Interface

### Features

- **Research Form**: Interactive form to submit research queries
- **Progress Tracking**: Real-time progress updates with detailed logs  
- **Job Management**: View and manage multiple research jobs
- **AI Report Generation**: Generate comprehensive reports using various LLM providers
- **PDF Export**: Download reports as properly named PDF files
- **History**: Browse previous research jobs and results

### Supported LLM Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo, and other models
- **Anthropic**: Claude 3 (Sonnet, Opus, Haiku)
- **Groq**: Fast inference with various open-source models

### File Naming Convention

Downloaded reports use the format: `{sanitized_title}_{source_type}.pdf`

Example: `artificial_intelligence_healthcare_web_academic.pdf`

## 📚 API Reference

### MCP Tools

#### `deep_research`

Perform comprehensive research on a topic.

**Parameters:**
- `query` (string, required): Research question or topic
- `sources` (string, optional): Source type ("web", "academic", "both")
- `num_results` (integer, optional): Number of sources to examine

**Returns:** Formatted research results with sources and content

#### `research_prompt`

Generate a structured research prompt for multi-stage research.

**Parameters:**
- `topic` (string, required): Topic to research

**Returns:** Comprehensive research prompt with methodology

### HTTP API Endpoints

#### `POST /deep_research`

Execute research query via HTTP.

```json
{
  "query": "string",
  "sources": "both",
  "num_results": 2
}
```

#### `GET /health`

Health check endpoint.

#### `GET /docs`

Interactive API documentation (Swagger UI).

### Web UI API Endpoints

#### `POST /research`

Start a new research job.

#### `GET /research/{job_id}`

Get research job status and results.

#### `GET /research/{job_id}/progress`

Get detailed progress for a research job.

## 🛠 Development

### Project Structure

```
analysis_alpaca/
├── src/analysis_alpaca/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── server.py          # MCP server implementation
│   │   └── research_service.py # Research orchestration
│   ├── search/
│   │   ├── __init__.py
│   │   ├── base.py           # Base searcher class
│   │   ├── web_search.py     # DuckDuckGo implementation
│   │   ├── academic_search.py # Semantic Scholar implementation
│   │   └── content_extractor.py # Content extraction
│   ├── models/
│   │   ├── __init__.py
│   │   └── research.py       # Data models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py        # Logging utilities
│   │   └── text.py          # Text processing
│   └── exceptions/
│       ├── __init__.py
│       └── base.py          # Custom exceptions
├── web_ui/
│   ├── frontend/            # React.js application
│   └── backend/             # FastAPI backend
├── tests/                   # Test suite
├── http_server.py          # HTTP wrapper
├── requirements.txt        # Dependencies
├── pyproject.toml         # Package configuration
└── Makefile              # Development commands
```

### Development Setup

```bash
# Install with development dependencies
pip install -e ".[dev,ai]"

# Set up pre-commit hooks (optional)
pre-commit install

# Run tests
make test

# Code formatting
make format

# Linting
make lint

# Type checking
make type-check
```

### Adding New Search Providers

1. Create a new searcher class inheriting from `BaseSearcher`
2. Implement the `search()` method
3. Add the searcher to `ResearchService`
4. Update configuration and documentation

Example:
```python
from .base import BaseSearcher

class NewSearcher(BaseSearcher):
    async def search(self, query: str, num_results: int) -> List[SearchResult]:
        # Implement search logic
        pass
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Test Structure

- `tests/test_models.py` - Data model tests
- `tests/test_utils.py` - Utility function tests
- `tests/conftest.py` - Test configuration and fixtures

### Writing Tests

Tests use pytest and pytest-asyncio for async testing:

```python
import pytest
from analysis_alpaca.models.research import ResearchQuery

@pytest.mark.asyncio
async def test_research_query():
    query = ResearchQuery(query="test", sources="web", num_results=2)
    assert query.query == "test"
```

## 🚀 Deployment

### Production Deployment

#### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8001
CMD ["python", "http_server.py"]
```

#### Environment Configuration

For production, set these environment variables:

```bash
AA_LOG_LEVEL=WARNING
AA_LOG_FILE=/var/log/analysis-alpaca.log
AA_AUTO_INSTALL_DEPS=false
AA_MAX_RESULTS=3
AA_WEB_TIMEOUT=20.0
```

#### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Monitoring

The application provides comprehensive logging. Monitor these key metrics:

- Research request rates
- Search success/failure rates
- Content extraction success rates
- Response times
- Error patterns

### Scaling Considerations

- The application is stateless and can be horizontally scaled
- Consider implementing Redis for caching search results
- Use a proper message queue for background processing in high-traffic scenarios

## 🔍 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure proper installation
pip install -e .

# Check Python path
python -c "import analysis_alpaca; print('OK')"
```

#### Search Timeouts
```bash
# Increase timeout values
export AA_WEB_TIMEOUT=30.0
export AA_ACADEMIC_TIMEOUT=30.0
```

#### Academic Search Rate Limiting
The system automatically handles Semantic Scholar rate limits with:
- Exponential backoff retry logic
- Graceful degradation (returns web results only)
- Request spacing

#### Content Extraction Failures
- Check network connectivity
- Verify target site availability
- Some sites may block automated requests

#### Large Response Truncation
```bash
# Increase content size limits
export AA_MAX_CONTENT_SIZE=15000
export AA_MAX_EXTRACTION_SIZE=200000
```

### Debug Mode

Enable detailed logging:

```bash
export AA_LOG_LEVEL=DEBUG
export AA_LOG_FILE="debug.log"
python http_server.py
```

View logs:
```bash
tail -f debug.log
```

### Getting Help

1. Check the logs for detailed error messages
2. Verify your configuration against the examples
3. Test with simple queries first
4. Ensure all dependencies are properly installed

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run quality checks: `make check-all`
5. Submit a pull request

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
make check-all
```

### Commit Guidelines

Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for refactoring

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Semantic Scholar** for academic search API
- **DuckDuckGo** for web search functionality
- **Model Context Protocol** for the integration framework
- **FastMCP** for the server implementation
- **React.js** and **FastAPI** for the web interface

## 📊 Roadmap

### Planned Features

- [ ] **Additional Search Providers**
  - Google Scholar integration
  - Bing Academic search
  - ArXiv direct integration

- [ ] **Enhanced Content Processing**
  - PDF content extraction
  - Image and chart analysis
  - Table data extraction

- [ ] **Performance Improvements**
  - Redis caching layer
  - Async processing optimization
  - Response streaming

- [ ] **Advanced Features**
  - Citation graph analysis
  - Research trend detection
  - Multi-language support

- [ ] **Enterprise Features**
  - User authentication
  - Usage analytics
  - API rate limiting
  - Custom search domains

### Version History

- **v1.0.0** - Initial release with core research functionality
- **v1.1.0** - Added web interface and PDF export
- **v1.2.0** - Enhanced error handling and rate limiting
- **Current** - Comprehensive cleanup and documentation

---

For the latest updates and detailed changelog, visit the [GitHub repository](https://github.com/yourusername/analysis-alpaca).