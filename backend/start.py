#!/usr/bin/env python
"""
Startup script for the Writing Agent FastAPI backend.
Handles environment setup and server startup.
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def setup_environment():
    """Setup environment variables and check dependencies"""
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write("# Writing Agent Environment Variables\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("DEBUG=True\n")
            f.write("APP_NAME=Writing Agent\n")
            f.write("APP_VERSION=1.0.0\n")
        print(f"Created {env_file}")
        print("Please update the .env file with your OpenAI API key")
    
    # Import config after ensuring .env file exists
    from config import settings
    
    # Check if OpenAI API key is set
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        print("⚠️  Warning: OpenAI API key not set. Agent will use mock responses.")
        print("   Set OPENAI_API_KEY in your .env file for full functionality.")
    else:
        print("✅ OpenAI API key found")
    
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Writing Agent Backend...")
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Import after environment setup
    from config import settings
    
    print(f"📝 {settings.app_name} v{settings.app_version}")
    print(f"🌐 Server will start at http://{settings.host}:{settings.port}")
    print(f"📚 API docs available at http://{settings.host}:{settings.port}/docs")
    print(f"🔄 WebSocket endpoint: ws://{settings.host}:{settings.port}/ws/writing")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

if __name__ == "__main__":
    main() 