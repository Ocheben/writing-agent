#!/usr/bin/env python
"""
Test script to verify LangSmith connectivity and diagnose issues.
Run this to test your LangSmith configuration.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings

def test_langsmith_setup():
    """Test LangSmith configuration and connectivity"""
    print("🔬 LangSmith Configuration Test")
    print("=" * 40)
    
    # Check if API key is set
    if not settings.langsmith_api_key:
        print("❌ LANGSMITH_API_KEY not set")
        print("💡 Set it in your .env file: LANGSMITH_API_KEY=ls__...")
        return False
    
    print(f"✅ API Key: Set ({len(settings.langsmith_api_key)} chars)")
    print(f"✅ Project: {settings.langsmith_project}")
    print(f"✅ Tracing: {settings.langsmith_tracing}")
    
    # Handle endpoint gracefully
    endpoint = settings.langsmith_endpoint
    print(f"✅ Endpoint: {endpoint}")
    
    # Set environment variables
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    
    # Test langsmith import
    try:
        import langsmith
        print("✅ LangSmith package imported successfully")
    except ImportError:
        print("❌ LangSmith package not installed")
        print("💡 Install with: pip install langsmith")
        return False
    
    # Test client creation and connection
    try:
        print("\n🔗 Testing LangSmith connection...")
        client = langsmith.Client()
        
        # Try to list projects (this tests auth)
        print("📋 Attempting to list projects...")
        projects = list(client.list_projects(limit=5))
        print(f"✅ Successfully connected! Found {len(projects)} projects:")
        
        for project in projects[:3]:  # Show first 3 projects
            print(f"   - {project.name}")
        
        # Check if our target project exists
        target_project = settings.langsmith_project
        project_exists = any(p.name == target_project for p in projects)
        
        if project_exists:
            print(f"✅ Target project '{target_project}' exists")
        else:
            print(f"⚠️ Target project '{target_project}' not found")
            print("💡 Create it at https://smith.langchain.com or use an existing project name")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        
        if "403" in str(e) or "Forbidden" in str(e):
            print("\n💡 403 Forbidden Error Solutions:")
            print("   1. Check your API key is correct (starts with 'ls__')")
            print("   2. Verify the key hasn't expired")
            print("   3. Ensure you're using the right organization's key")
            print("   4. Visit https://smith.langchain.com/settings to verify")
            
        elif "401" in str(e) or "Unauthorized" in str(e):
            print("\n💡 401 Unauthorized Error Solutions:")
            print("   1. API key is likely invalid or malformed")
            print("   2. Double-check the key from https://smith.langchain.com/settings")
            
        else:
            print(f"\n💡 General troubleshooting:")
            print("   1. Check your internet connection")
            print("   2. Verify LangSmith service status")
            print("   3. Try creating a new API key")
            
        return False

if __name__ == "__main__":
    print("LangSmith Configuration Test\n")
    
    if test_langsmith_setup():
        print("\n🎉 LangSmith setup is working correctly!")
    else:
        print("\n🔧 Please fix the issues above and try again.")
        sys.exit(1) 