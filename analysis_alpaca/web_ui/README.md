# AnalysisAlpaca Web UI

A modern web application that provides a user-friendly interface for the AnalysisAlpaca MCP server. This application combines web and academic research with AI-powered report generation.

## 🚀 Features

- **Interactive Research Interface**: Easy-to-use web form for starting research
- **Real-time Progress Tracking**: Live updates on research progress with detailed logs
- **AI-Powered Reports**: Generate comprehensive reports using OpenAI or Anthropic models
- **Research History**: View and manage all past research jobs
- **Source Selection**: Choose between web, academic, or both source types
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Export Functionality**: Download reports in Markdown format

## 📁 Project Structure

```
web_ui/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example       # Environment variables template
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Header.js
│   │   │   ├── ResearchForm.js
│   │   │   ├── ResearchResults.js
│   │   │   └── JobsList.js
│   │   ├── services/      # API service layer
│   │   │   └── api.js
│   │   ├── App.js         # Main React app
│   │   ├── App.css        # Application styles
│   │   └── index.js       # React entry point
│   ├── public/            # Static files
│   ├── package.json       # Node.js dependencies
│   └── .env.example      # Environment variables template
└── README.md              # This file
```

## 🔧 Installation & Setup

### Prerequisites

1. **AnalysisAlpaca MCP Code**: Ensure the MCP server code is available in the parent directory

2. **Node.js & Python**: Ensure you have Node.js (16+) and Python (3.8+) installed

3. **Port Availability**: Make sure ports 8001, 8000, and 3000 are available

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd web_ui/backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys for enhanced report generation
   ```

4. **Start the backend server**:
   ```bash
   python main.py
   ```
   The backend will run on http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd web_ui/frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if backend runs on different port
   ```

4. **Start the development server**:
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

## 🚀 Usage

### Starting Research

1. **Open the web application**: Navigate to http://localhost:3000
2. **Enter your research query**: Be specific for better results
3. **Configure options**:
   - **Sources**: Choose web, academic, or both
   - **Number of Sources**: Select how many sources to examine
   - **AI Provider**: Choose OpenAI or Anthropic for report generation
   - **Model**: Select specific model (requires API keys)
4. **Click "Start Research"**: The system will begin processing

### Monitoring Progress

- **Real-time Updates**: Progress bar and status updates automatically
- **Detailed Logs**: View step-by-step progress in the Progress Log section
- **Live Polling**: System automatically checks for updates every 2 seconds

### Viewing Results

- **Raw Data**: View the original research data collected from sources
- **Generated Report**: AI-processed comprehensive report with formatting
- **Download**: Export the report as a Markdown file

### Managing Research History

- **View All Jobs**: Access the "Research History" tab
- **Filter by Status**: See completed, in-progress, or failed jobs
- **Delete Jobs**: Remove unwanted research from history
- **Resume Viewing**: Click on any job to view its results

## ⚙️ Configuration

### LLM Integration

For enhanced report generation, configure API keys:

**OpenAI Configuration**:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

**Anthropic Configuration**:
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

**Groq Configuration**:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

Without API keys, the system will still generate basic reports using the raw research data.

### Server Ports

- **MCP HTTP Server**: Port 8001 (configurable via environment)
- **Backend API**: Port 8000 (configurable via environment)  
- **Frontend**: Port 3000 (React development server)

The services communicate via HTTP APIs for proper separation of concerns.

### CORS Configuration

The backend is configured to allow requests from:
- http://localhost:3000
- http://127.0.0.1:3000

Add additional origins in the backend `main.py` file if needed.

## 🔌 API Endpoints

The backend provides the following REST API endpoints:

- `POST /research` - Start new research job
- `GET /research/{job_id}` - Get research job status
- `GET /research/{job_id}/progress` - Get detailed progress
- `GET /research` - List all research jobs
- `DELETE /research/{job_id}` - Delete research job
- `GET /health` - Health check endpoint

## 🎨 UI Components

### ResearchForm
- Query input with examples
- Source and model selection
- Form validation and submission

### ResearchResults
- Real-time progress tracking
- Raw data display
- Formatted report rendering
- Download functionality

### JobsList
- Grid view of all research jobs
- Status indicators and progress bars
- Job management (delete, select)

### Header
- Application branding
- Status indicators

## 🛠️ Development

### Running in Development Mode

1. **Start MCP HTTP Server** (Port 8001):
   ```bash
   cd analysis_alpaca  # Root directory
   python http_server.py
   ```

2. **Start Backend API** (Port 8000):
   ```bash
   cd web_ui/backend
   python main.py
   ```

3. **Start Frontend** (Port 3000):
   ```bash
   cd web_ui/frontend
   npm start
   ```

**All Three Services Running:**
- MCP Server: http://localhost:8001 (API docs: /docs)
- Backend API: http://localhost:8000 (API docs: /docs)  
- Frontend UI: http://localhost:3000 (Web interface)

### Building for Production

**Frontend Build**:
```bash
cd web_ui/frontend
npm run build
```

**Backend Deployment**:
```bash
cd web_ui/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🐛 Troubleshooting

### Common Issues

1. **"Network error - please check if the server is running"**
   - Ensure backend server is running on port 8000
   - Check if MCP server is running and accessible

2. **"MCP research failed"**
   - Verify MCP server is running and accessible
   - Check MCP server logs for errors

3. **"Failed to generate report"**
   - Check if API keys are configured correctly
   - Verify API key permissions and quotas

4. **Frontend not loading**
   - Ensure Node.js dependencies are installed (`npm install`)
   - Check if port 3000 is available

### Debug Mode

Enable detailed logging:

**Backend Debug**:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

**Frontend Debug**:
- Open browser developer tools (F12)
- Check console for errors
- Monitor network tab for API calls

## 📝 License

This project is part of the AnalysisAlpaca platform and follows the same license terms.

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests for review

## 📈 Roadmap

- [ ] User authentication and sessions
- [ ] Research templates and saved queries
- [ ] Advanced filtering and search in history
- [ ] Export to multiple formats (PDF, DOCX)
- [ ] Team collaboration features
- [ ] Integration with more LLM providers