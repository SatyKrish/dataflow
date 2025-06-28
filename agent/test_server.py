#!/usr/bin/env python3
"""
Test script for the LangGraph Multi-Agent Research Server

Validates that the server endpoints work correctly with the new implementation.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

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

if __name__ == "__main__":
    print("LangGraph Multi-Agent Research Server Test")
    print("==========================================")
    print("Make sure the server is running: python agent/server.py")
    print()
    
    asyncio.run(test_server()) 