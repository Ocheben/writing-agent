import os
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "Writing Agent"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Keys
    openai_api_key: str = ""
    
    # LangSmith Configuration
    langsmith_api_key: str = ""
    langsmith_tracing: bool = True
    langsmith_project: str = "default"
    langsmith_endpoint: str = "https://eu.api.smith.langchain.com"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    class Config:
        env_file = Path(__file__).parent / ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

settings = Settings() 