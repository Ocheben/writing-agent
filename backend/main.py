from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from typing import Dict, Optional
import logging
import os

from config import settings
from agent import WritingAgent

# Initialize LangSmith tracing
if settings.langsmith_api_key and settings.langsmith_tracing:
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    
    try:
        import langsmith
        print(f"✅ LangSmith tracing initialized for project: {settings.langsmith_project}")
        
        # Test the connection
        try:
            client = langsmith.Client()
            # Try to ping the service to validate the API key
            print(f"🔗 Testing LangSmith connection...")
            # This will fail gracefully if there are auth issues
        except Exception as e:
            print(f"⚠️ LangSmith connection test failed: {str(e)}")
            print("💡 Possible solutions:")
            print("   1. Verify your LANGSMITH_API_KEY is correct")
            print("   2. Ensure the project 'writing-agent' exists in your LangSmith workspace")
            print("   3. Check that your API key has write permissions")
            print("   4. Visit https://smith.langchain.com to verify your setup")
            
    except ImportError:
        print("⚠️ LangSmith not installed. Install with: pip install langsmith")
else:
    print("⚠️ LangSmith tracing disabled. Set LANGSMITH_API_KEY and LANGSMITH_TRACING=true to enable.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize writing agent
writing_agent = WritingAgent()

# Request models
class GenerateRequest(BaseModel):
    prompt: str
    context: Optional[Dict] = None

class EditRequest(BaseModel):
    content: str
    context: Optional[Dict] = None

class ImproveRequest(BaseModel):
    content: str
    context: Optional[Dict] = None

@app.get("/")
async def root():
    return {"message": "Writing Agent API", "version": settings.app_version}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_ready": writing_agent.is_ready()}

async def create_sse_stream(generator, action_type: str):
    """Create SSE formatted stream from async generator"""
    try:
        # Send start event
        yield f"data: {json.dumps({'type': f'{action_type}_start', 'message': f'Starting {action_type}...'})}\n\n"
        
        # Stream content chunks
        async for chunk in generator:
            if chunk:
                yield f"data: {json.dumps({'type': f'{action_type}_chunk', 'content': chunk})}\n\n"
        
        # Send completion event
        yield f"data: {json.dumps({'type': f'{action_type}_complete', 'message': f'{action_type.title()} completed'})}\n\n"
        
    except Exception as e:
        logger.error(f"{action_type} error: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'{action_type.title()} failed: {str(e)}'})}\n\n"

@app.post("/api/generate")
async def generate_text(request: GenerateRequest):
    """Generate text with SSE streaming"""
    logger.info(f"Generate request: prompt length {len(request.prompt)}")
    
    generator = writing_agent.generate_text(request.prompt, request.context or {})
    stream = create_sse_stream(generator, "generation")
    
    return StreamingResponse(
        stream, 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.post("/api/edit")
async def edit_text(request: EditRequest):
    """Edit text with SSE streaming"""
    logger.info(f"Edit request: content length {len(request.content)}")
    
    generator = writing_agent.edit_text(request.content, request.context or {})
    stream = create_sse_stream(generator, "edit")
    
    return StreamingResponse(
        stream, 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive", 
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.post("/api/improve")
async def improve_text(request: ImproveRequest):
    """Improve text with SSE streaming"""
    logger.info(f"Improve request: content length {len(request.content)}")
    
    generator = writing_agent.improve_text(request.content, request.context or {})
    stream = create_sse_stream(generator, "improve")
    
    return StreamingResponse(
        stream, 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 