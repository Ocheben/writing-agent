# Writing Agent - AI-Powered Writing Assistant

A robust writing application similar to OpenAI's Canvas, built with LangGraph agents, TipTap editor, and FastAPI streaming.

## 🎯 Features

- 🤖 **AI-Powered Writing**: Intelligent text generation, editing, and improvement
- ✨ **Real-time Editor**: TipTap rich text editor with AI extensions
- 🔄 **AI Changes**: Smart suggestions for text modifications
- 🎯 **AI Generations**: Content creation based on prompts
- 📡 **Streaming Responses**: Real-time AI interactions via WebSocket
- 🎨 **Canvas-like UI**: Modern, intuitive user interface
- 🛠️ **LangGraph Studio**: Visual agent development and debugging

## 🏗️ Architecture

- **Frontend**: React + TypeScript + TipTap with custom AI extensions
- **Backend**: FastAPI + LangGraph agents with streaming support
- **AI Integration**: LangGraph Studio compatible agent architecture
- **Communication**: WebSocket streaming for real-time interactions

## 📁 Project Structure

```
writing-agent/
├── frontend/              # React + TipTap frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── extensions/    # TipTap AI extensions
│   │   ├── hooks/         # React hooks
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── backend/               # FastAPI + LangGraph backend
│   ├── main.py           # FastAPI application
│   ├── agent.py          # LangGraph writing agent
│   ├── studio_graph.py   # LangGraph Studio export
│   ├── config.py         # Configuration
│   ├── start.py          # Startup script
│   └── requirements.txt
├── langgraph.json        # LangGraph Studio configuration
├── setup.sh              # Automated setup script
├── setup-conda.sh        # Conda-specific setup script
├── start-dev.sh          # Development startup script
└── README.md
```

## 🚀 Quick Start

### Automated Setup (Recommended)

**For Conda Users:**
```bash
# Automated conda setup (creates environment + installs everything)
./setup-conda.sh

# Start all services
./start-dev.sh
```

**For Standard Python:**
```bash
# If using existing conda environment, activate it first
conda activate your-environment-name  # (optional)

# Clone and setup everything
./setup.sh

# Start all services
./start-dev.sh
```

**Note for Conda Users**: 
- Use `./setup-conda.sh` for a complete automated setup that creates a new conda environment
- Use `./setup.sh` if you already have a conda environment activated
- The setup scripts automatically detect conda environments

### Manual Setup

#### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key

#### 1. Backend Setup

**Option A: Using Conda (Recommended)**
```bash
# Create and activate conda environment
conda create -n writing-agent python=3.12
conda activate writing-agent

cd backend

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Add your OpenAI API key to .env

# Start backend
python start.py
```

**Option B: Using Virtual Environment**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Add your OpenAI API key to .env

# Start backend
python start.py
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 3. LangGraph Studio (Optional)

```bash
# Install LangGraph CLI
pip install langgraph-cli[inmem]

# Start LangGraph Studio
langgraph dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/writing
- **LangGraph Studio**: http://localhost:3001

## 🔧 Configuration

### Environment Variables

Create `backend/.env` with:

```env
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
APP_NAME=Writing Agent
APP_VERSION=1.0.0
```

### LangGraph Studio

The agent is configured for LangGraph Studio in `langgraph.json`. The studio provides:

- Visual graph representation
- Step-by-step execution debugging
- Agent state inspection
- Real-time interaction testing

## 🎨 Usage

### Basic Writing

1. Open the application at http://localhost:3000
2. Start typing in the editor
3. Use the AI panel to generate, improve, or continue text

### AI Features

- **Generate**: Describe what you want to write in the AI panel
- **Continue**: Click "Continue Writing" to extend current text
- **Improve**: Select text and use "Improve Text" for enhancements
- **Edit**: Select text and request specific improvements

### TipTap AI Extensions

The editor includes custom TipTap extensions:

- **AI Changes**: Intelligent text modification suggestions
- **AI Generations**: Content creation and continuation
- Real-time streaming integration
- Visual change indicators

## 🛠️ Development

### Architecture Overview

1. **LangGraph Agent**: 
   - StateGraph with TypedDict state
   - Agent and tools nodes
   - Conditional edges for ReAct pattern
   - Streaming response support

2. **FastAPI Backend**:
   - WebSocket endpoints for real-time communication
   - CORS configured for frontend
   - Structured logging and error handling

3. **React Frontend**:
   - TypeScript for type safety
   - TipTap editor with custom extensions
   - Tailwind CSS for styling
   - WebSocket hook for backend communication

### Adding New AI Tools

1. Add tool function in `backend/agent.py`:
```python
@tool
def your_tool(input: str) -> str:
    """Tool description"""
    return "result"
```

2. Add to tools list and update agent configuration

3. Update frontend types in `frontend/src/types/index.ts`

4. Add UI controls in AI panel or toolbar

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📚 API Reference

### WebSocket API

Connect to `ws://localhost:8000/ws/writing`

**Message Format:**
```json
{
  "action": "generate|edit|improve",
  "content": "text content",
  "context": {
    "style": "formal|casual|creative",
    "length": "short|medium|long",
    "focus": "clarity|structure|engagement"
  }
}
```

**Response Format:**
```json
{
  "type": "generation_start|generation_chunk|generation_complete",
  "content": "response text",
  "message": "status message"
}
```

### REST API

- `GET /`: Health check
- `GET /health`: Detailed health status
- `GET /docs`: OpenAPI documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.11+ required)
- Verify virtual environment activation
- Check OpenAI API key in .env

**Frontend build errors:**
- Check Node.js version (18+ required)
- Clear node_modules and reinstall
- Check TypeScript configuration

**WebSocket connection fails:**
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify firewall settings

**LangGraph Studio issues:**
- Check langgraph.json format
- Ensure graph compiles without errors
- Verify environment variables

**Conda Environment Issues:**
- Make sure conda is properly installed and activated
- Use `./setup-conda.sh` for automated conda setup
- Verify environment activation: `conda activate writing-agent`
- Check Python version in conda environment: `python --version`

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the API documentation at http://localhost:8000/docs
- Use LangGraph Studio for agent debugging

---

Built with ❤️ using LangGraph, FastAPI, React, and TipTap 