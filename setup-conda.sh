#!/bin/bash

# Writing Agent Conda Setup Script
echo "🚀 Setting up Writing Agent with Conda"
echo "======================================"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi

echo "✅ Conda found"

# Check if environment already exists
ENV_NAME="writing-agent"
if conda env list | grep -q "^$ENV_NAME "; then
    echo "📋 Environment '$ENV_NAME' already exists"
    read -p "Do you want to recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        conda env remove -n $ENV_NAME
    else
        echo "✅ Using existing environment"
    fi
fi

# Create conda environment if it doesn't exist
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "🔧 Creating conda environment with Python 3.12..."
    conda create -n $ENV_NAME python=3.12 -y
fi

# Activate environment
echo "🔄 Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Check if Node.js is available
echo "📋 Checking Node.js version..."
node_version=$(node --version 2>/dev/null | grep -oE '[0-9]+')
if [[ -z "$node_version" ]]; then
    echo "❌ Node.js not found. Installing Node.js via conda..."
    conda install -c conda-forge nodejs=18 -y
else
    if [[ $node_version -lt 18 ]]; then
        echo "⚠️  Node.js version too old. Installing Node.js 18..."
        conda install -c conda-forge nodejs=18 -y
    else
        echo "✅ Node.js v$node_version found"
    fi
fi

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
cd backend

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
echo "🚀 To start developing:"
echo "1. Update backend/.env with your OpenAI API key"
echo "2. Activate the environment: conda activate $ENV_NAME"
echo "3. Start all services: ./start-dev.sh"
echo ""
echo "📚 Access points:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- LangGraph Studio: http://localhost:3001"
echo ""
echo "💡 Environment name: $ENV_NAME"
echo "Happy writing! 📝✨" 