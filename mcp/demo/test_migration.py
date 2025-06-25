#!/usr/bin/env python3
"""
FastMCP Test Script

Tests the FastMCP implementation to ensure all functionality works correctly.

Usage:
    python test_migration.py [--port 8080]
"""

import asyncio
import json
import logging
import argparse
from typing import Dict, Any, List
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPTester:
    def __init__(self, base_url: str, server_name: str):
        self.base_url = base_url.rstrip('/')
        self.server_name = server_name
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def send_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send an MCP JSON-RPC request"""
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Request failed for {self.server_name}: {e}")
            return {"error": str(e)}
    
    async def test_initialize(self) -> bool:
        """Test MCP initialization"""
        logger.info(f"Testing initialization for {self.server_name}")
        
        response = await self.send_mcp_request("initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "migration-test", "version": "1.0.0"}
        })
        
        if "error" in response:
            logger.error(f"Initialize failed for {self.server_name}: {response['error']}")
            return False
        
        result = response.get("result", {})
        if "serverInfo" not in result:
            logger.error(f"No serverInfo in initialize response for {self.server_name}")
            return False
        
        logger.info(f"✅ Initialize successful for {self.server_name}")
        return True
    
    async def test_tools_list(self) -> List[str]:
        """Test tools/list and return available tool names"""
        logger.info(f"Testing tools/list for {self.server_name}")
        
        response = await self.send_mcp_request("tools/list")
        
        if "error" in response:
            logger.error(f"Tools list failed for {self.server_name}: {response['error']}")
            return []
        
        tools = response.get("result", {}).get("tools", [])
        tool_names = [tool["name"] for tool in tools]
        
        logger.info(f"✅ Found {len(tool_names)} tools for {self.server_name}: {tool_names}")
        return tool_names
    
    async def test_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Test calling a specific tool"""
        logger.info(f"Testing {tool_name} call for {self.server_name}")
        
        response = await self.send_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in response:
            logger.error(f"Tool call {tool_name} failed for {self.server_name}: {response['error']}")
            return {"error": response["error"]}
        
        result = response.get("result", {})
        logger.info(f"✅ Tool call {tool_name} successful for {self.server_name}")
        return result

async def run_fastmcp_tests(port: int):
    """Run comprehensive FastMCP tests"""
    logger.info("Starting FastMCP Tests")
    logger.info("=" * 50)
    
    base_url = f"http://localhost:{port}"
    server_name = "FastMCP Server"
    
    logger.info(f"\nTesting {server_name} at {base_url}")
    logger.info("-" * 30)
    
    async with MCPTester(base_url, server_name) as tester:
        # Test 1: Initialization
        init_success = await tester.test_initialize()
        
        if not init_success:
            logger.error(f"❌ Server initialization failed")
            return {"status": "failed", "reason": "initialization failed"}
        
        # Test 2: Tools list
        tool_names = await tester.test_tools_list()
        
        if not tool_names:
            logger.error(f"❌ No tools found")
            return {"status": "failed", "reason": "no tools found"}
        
        # Test 3: Tool calls
        tool_results = {}
        
        # Test health_check (no arguments)
        if "health_check" in tool_names:
            health_result = await tester.test_tool_call("health_check", {})
            tool_results["health_check"] = health_result
        
        # Test get_server_info (no arguments) 
        if "get_server_info" in tool_names:
            info_result = await tester.test_tool_call("get_server_info", {})
            tool_results["get_server_info"] = info_result
        
        # Test ask_ai (with arguments)
        if "ask_ai" in tool_names:
            ai_result = await tester.test_tool_call("ask_ai", {
                "question": "Generate 3 sample person records",
                "mode": "generate"
            })
            tool_results["ask_ai"] = ai_result
        
        return {
            "status": "success",
            "tools": tool_names,
            "tool_results": tool_results
        }

def main():
    parser = argparse.ArgumentParser(description="Test FastMCP server")
    parser.add_argument(
        "--port", 
        type=int, 
        default=8080,
        help="Port for FastMCP server (default: 8080)"
    )
    
    args = parser.parse_args()
    
    logger.info("FastMCP Test Suite")
    logger.info(f"FastMCP server: http://localhost:{args.port}")
    
    try:
        result = asyncio.run(run_fastmcp_tests(args.port))
        
        # Print summary
        print("\n" + "=" * 60)
        print("FASTMCP TEST SUMMARY")
        print("=" * 60)
        
        status = result.get("status", "unknown")
        print(f"FastMCP Server: {status.upper()}")
        if status == "success":
            tools = result.get("tools", [])
            print(f"  Tools: {len(tools)} available - {tools}")
            print("  ✅ All tests passed!")
        else:
            reason = result.get("reason", "unknown")
            print(f"  ❌ Reason: {reason}")
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    main()
