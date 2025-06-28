#!/usr/bin/env python3
"""
Test script for the LangGraph Multi-Agent Research Server

Validates that the server endpoints work correctly with the new implementation.
"""

import asyncio
import httpx
import json
import os
import sys
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_server():
    """Test the server endpoints"""
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient() as client:
        
        # Test root endpoint
        print("Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Root: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print()
        
        # Test health endpoint
        print("Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"Health: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print()
        
        # Test Azure OpenAI status endpoint (new)
        print("Testing Azure OpenAI status endpoint...")
        try:
            response = await client.get(f"{base_url}/azure-openai/status")
            print(f"Azure OpenAI Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(json.dumps({
                    "configuration": result.get("configuration", {}),
                    "validation": result.get("validation", {}),
                    "connection_test": {
                        "status": result.get("connection_test", {}).get("status", "unknown"),
                        "message": result.get("connection_test", {}).get("message", "")
                    },
                    "timestamp": result.get("timestamp", "")
                }, indent=2))
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Azure OpenAI status test failed: {e}")
        print()
        
        # Test agents endpoint
        print("Testing agents endpoint...")
        response = await client.get(f"{base_url}/agents")
        print(f"Agents: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print()
        
        # Test research endpoint
        print("Testing research endpoint...")
        research_request = {
            "query": "What customer data is available in the sales database?",
            "user_email": "test@example.com",
            "session_id": "test_session_001"
        }
        
        try:
            response = await client.post(
                f"{base_url}/research",
                json=research_request,
                timeout=30.0
            )
            
            print(f"Research: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(json.dumps({
                    "session_id": result["session_id"],
                    "status": result["status"],
                    "timestamp": result["timestamp"],
                    "results_summary": {
                        k: f"<{type(v).__name__} with {len(str(v))} chars>"
                        for k, v in result.get("results", {}).items()
                    }
                }, indent=2))
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Research endpoint test failed: {e}")

async def test_server_health():
    """Quick health check test"""
    
    base_url = "http://localhost:8001"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/health")
            return response.status_code == 200
    except Exception:
        return False

async def run_all_server_tests():
    """Run all server tests with proper error handling"""
    
    print("🧪 LangGraph Multi-Agent Research Server Test Suite")
    print("=" * 60)
    print("Make sure the server is running: python agent/server.py")
    print()
    
    # First check if server is running
    print("🔍 Checking server availability...")
    if await test_server_health():
        print("✅ Server is running")
        print()
        await test_server()
        print("🎉 All server tests completed!")
    else:
        print("❌ Server is not running or not responding")
        print("Please start the server with: python agent/server.py")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_all_server_tests())
    sys.exit(0 if success else 1) 