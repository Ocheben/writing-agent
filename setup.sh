#!/bin/bash

# Writing Agent Setup Script
echo "🚀 Setting up Writing Agent - AI-Powered Writing Assistant"
echo "================================================"

# Check if Python 3.11+ is available
echo "📋 Checking Python version..."

# Check conda environment first
if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
    echo "🐍 Detected conda environment: $CONDA_DEFAULT_ENV"
    # In conda environments, prefer 'python' over 'python3'
    python_version=$(python --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
    python_cmd="python"
    
    if [[ -z "$python_version" ]]; then
        python_version=$(python3 --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
        python_cmd="python3"
    fi
else
    # Not in conda, try python3 first, then python
    python_version=$(python3 --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
    python_cmd="python3"

    if [[ -z "$python_version" ]]; then
        python_version=$(python --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
        python_cmd="python"
    fi
fi

if [[ -z "$python_version" ]]; then
    echo "❌ Python not found. Please ensure Python 3.11+ is installed and activated."
    echo "💡 If using conda: conda activate your-environment-name"
    echo "💡 Run ./debug-python.sh for detailed diagnostics"
    exit 1
fi

python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [[ $python_major -lt 3 || ($python_major -eq 3 && $python_minor -lt 11) ]]; then
    echo "❌ Python 3.11+ required. Found: $python_version using $python_cmd"
    echo ""
    if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
        echo "💡 You're in conda environment '$CONDA_DEFAULT_ENV' but Python is too old."
        echo "🔧 Try: conda install python=3.12"
        echo "🔧 Or: conda create -n writing-agent python=3.12 && conda activate writing-agent"
    else
        echo "💡 Please activate a conda environment with Python 3.11+ or create one:"
        echo "🔧 conda create -n writing-agent python=3.12"
        echo "🔧 conda activate writing-agent"
        echo "🔧 Or run: ./setup-conda.sh"
    fi
    echo ""
    echo "🔍 Run ./debug-python.sh for detailed environment information"
    exit 1
fi

echo "✅ Python $python_version found"

# Check if Node.js is available
echo "📋 Checking Node.js version..."
node_version=$(node --version 2>/dev/null | grep -oE '[0-9]+' | head -1)
if [[ -z "$node_version" ]]; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

if [[ $node_version -lt 18 ]]; then
    echo "❌ Node.js 18+ required. Found: v$node_version"
    exit 1
fi

echo "✅ Node.js v$node_version found"

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Handle virtual environment setup
if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
    echo "✅ Using conda environment: $CONDA_DEFAULT_ENV"
    echo "Skipping virtual environment creation..."
else
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        $python_cmd -m venv venv
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Writing Agent Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
APP_NAME=Writing Agent
APP_VERSION=1.0.0
EOL
    echo "⚠️  Please update .env file with your OpenAI API key"
fi

cd ..

# Setup Frontend
echo ""
echo "🔧 Setting up Frontend..."
cd frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

# Install LangGraph CLI
echo ""
echo "🔧 Installing LangGraph CLI..."
pip install langgraph-cli[inmem]

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Quick Start:"
echo "1. Update backend/.env with your OpenAI API key"
echo "2. Start the backend:"
echo "   cd backend && python start.py"
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo "4. For LangGraph Studio:"
echo "   langgraph dev"
echo ""
echo "📚 Access points:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- LangGraph Studio: http://localhost:3001"
echo ""
echo "Happy writing! 📝✨" 