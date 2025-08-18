#!/bin/bash

# Development Startup Script for Writing Agent
echo "🚀 Starting Writing Agent Development Environment"
echo "================================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID $LANGGRAPH_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Check if setup has been run
if [[ "$CONDA_DEFAULT_ENV" == "" ]] && [[ ! -d "backend/venv" ]]; then
    echo "❌ Please run ./setup.sh first to install dependencies"
    echo "💡 Or activate your conda environment: conda activate your-environment-name"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found. Please run ./setup.sh first"
    exit 1
fi

# Start Backend
echo "🔧 Starting Backend Server..."
cd backend

# Activate environment if not using conda
if [[ "$CONDA_DEFAULT_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Using conda environment: $CONDA_DEFAULT_ENV"
fi

python start.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start Frontend
echo "🔧 Starting Frontend Development Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Start LangGraph Studio
echo "🔧 Starting LangGraph Studio..."
langgraph dev &
LANGGRAPH_PID=$!

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📚 Access your application:"
echo "- 🌐 Frontend: http://localhost:3000"
echo "- 🔌 Backend API: http://localhost:8000"
echo "- 📖 API Documentation: http://localhost:8000/docs"
echo "- 🛠️  LangGraph Studio: http://localhost:3001"
echo ""
echo "💡 Press Ctrl+C to stop all services"
echo ""

# Keep script running
wait 