#!/usr/bin/env python3
"""
Multi-Agent Research System - MCP Server

A FastMCP server that provides multi-agent research capabilities by coordinating
with the FastAPI-based agent server in the agent/ folder.
"""

import os
import logging
import json
import uuid
from typing import Dict, Optional, Literal
from datetime import datetime
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from fastmcp import FastMCP
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP client for calling the agent server
http_client = httpx.AsyncClient(timeout=300.0)

# Create FastMCP server
mcp = FastMCP(
    name="multi-agent-research",
    instructions="""
    Multi-Agent Research System providing intelligent data discovery and analysis.
    
    This system coordinates specialized AI agents to:
    - Discover metadata and schemas across data sources
    - Validate data access permissions and entitlements  
    - Retrieve and process data from multiple sources
    - Synthesize findings into comprehensive responses
    
    Available research modes:
    - metadata: Focus on schema and structure discovery
    - data: Data retrieval with validation
    - analysis: Full analysis with synthesis
    - full: Complete multi-agent research (default)
    """
)

@mcp.tool
async def multi_agent_research(
    query: str,
    user_email: str = "default@example.com",
    session_id: Optional[str] = None,
    research_mode: Literal["metadata", "data", "analysis", "full"] = "full"
) -> Dict:
    """Perform multi-agent research across data sources using specialized AI agents.
    
    Args:
        query: Natural language research query or request
        user_email: User identifier for session tracking and entitlements
        session_id: Optional existing session ID to continue research
        research_mode: Research scope (metadata, data, analysis, full)
    
    Returns:
        Comprehensive research results with agent findings and citations
    """
    
    if not query.strip():
        return {"error": "Query cannot be empty"}
    
    logger.info(f"Multi-agent research request: {query[:100]}...")
    
    try:
        # Call the agent server
        agent_endpoint = os.getenv("LANGRAPH_AGENTS_ENDPOINT", "http://localhost:8001")
        
        request_payload = {
            "query": query,
            "session_id": session_id,
            "research_mode": research_mode,
            "user_email": user_email
        }
        
        response = await http_client.post(
            f"{agent_endpoint}/execute_research",
            json=request_payload,
            timeout=300.0
        )
        
        if response.status_code == 200:
            results = response.json()
            
            # Return formatted results
            return {
                "status": "completed",
                "session_id": results.get("session_id"),
                "query": query,
                "research_mode": research_mode,
                "agent_results": results.get("results", {}),
                "execution_time_ms": results.get("execution_time_ms", 0),
                "timestamp": results.get("timestamp")
            }
        else:
            logger.error(f"Agent server error: HTTP {response.status_code}")
            return {
                "status": "failed",
                "error": f"Agent server returned status {response.status_code}",
                "details": response.text if response.text else "No error details"
            }
            
    except httpx.TimeoutException:
        logger.error("Agent server timeout")
        return {
            "status": "failed",
            "error": "Research request timed out",
            "timeout_seconds": 300
        }
    except httpx.ConnectError:
        logger.error("Agent server connection failed")
        return {
            "status": "failed", 
            "error": "Could not connect to agent server",
            "agent_endpoint": agent_endpoint
        }
    except Exception as e:
        logger.error(f"Research execution failed: {e}")
        return {
            "status": "failed",
            "error": f"Research execution failed: {str(e)}"
        }

@mcp.tool
async def get_research_session(session_id: str) -> Dict:
    """Get the status and results of a research session.
    
    Args:
        session_id: Research session ID to retrieve
        
    Returns:
        Session status and details
    """
    
    if not session_id:
        return {"error": "Session ID is required"}
    
    try:
        # For MVP, return basic session info
        # In production, this would query the database
        return {
            "session_id": session_id,
            "status": "unknown",
            "message": "Session lookup not yet implemented in MVP",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Session lookup failed: {e}")
        return {"error": f"Session lookup failed: {str(e)}"}

@mcp.tool
async def list_available_agents() -> Dict:
    """List available research agents and their capabilities.
    
    Returns:
        Information about available agents and research modes
    """
    
    try:
        agent_endpoint = os.getenv("LANGRAPH_AGENTS_ENDPOINT", "http://localhost:8001")
        
        response = await http_client.get(
            f"{agent_endpoint}/agents",
            timeout=10.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback agent information
            return {
                "agents": {
                    "metadata": {
                        "description": "Discovers data schemas and metadata",
                        "capabilities": ["schema_discovery", "data_source_mapping"]
                    },
                    "entitlement": {
                        "description": "Validates data access permissions", 
                        "capabilities": ["access_validation", "permission_checking"]
                    },
                    "data": {
                        "description": "Retrieves and processes data",
                        "capabilities": ["data_retrieval", "data_processing"]
                    },
                    "aggregation": {
                        "description": "Synthesizes research findings",
                        "capabilities": ["result_synthesis", "citation_generation"]
                    }
                },
                "research_modes": ["metadata", "data", "analysis", "full"],
                "note": "Agent server not available, showing cached information"
            }
            
    except Exception as e:
        logger.error(f"Agent listing failed: {e}")
        return {"error": f"Could not retrieve agent information: {str(e)}"}

@mcp.tool
async def health_check() -> Dict:
    """Check the health status of the multi-agent research system.
    
    Returns:
        Health status of all system components
    """
    
    logger.info("Performing health check")
    
    health_status = {
        "mcp_server": {
            "status": "healthy",
            "server_name": "Multi-Agent Research MCP Server",
            "version": "1.0.0-mvp"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Check agent server
    try:
        agent_endpoint = os.getenv("LANGRAPH_AGENTS_ENDPOINT", "http://localhost:8001") 
        
        response = await http_client.get(
            f"{agent_endpoint}/health",
            timeout=10.0
        )
        
        if response.status_code == 200:
            agent_health = response.json()
            health_status["agent_server"] = {
                "status": agent_health.get("status", "unknown"),
                "endpoint": agent_endpoint,
                "components": agent_health.get("components", {})
            }
        else:
            health_status["agent_server"] = {
                "status": "error",
                "endpoint": agent_endpoint,
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        health_status["agent_server"] = {
            "status": "error",
            "endpoint": os.getenv("LANGRAPH_AGENTS_ENDPOINT", "http://localhost:8001"),
            "error": str(e)
        }
    
    # Overall status
    if health_status["agent_server"]["status"] == "healthy":
        health_status["overall_status"] = "healthy"
    else:
        health_status["overall_status"] = "degraded"
    
    return health_status

@mcp.tool
async def analyze_query_intent(query: str) -> Dict:
    """Analyze user query to determine research intent and recommended approach.
    
    Args:
        query: Natural language query to analyze
        
    Returns:
        Intent analysis with research recommendations
    """
    
    if not query.strip():
        return {"error": "Query cannot be empty"}
    
    # Simple intent analysis for MVP
    query_lower = query.lower()
    
    # Determine intent based on keywords
    if any(word in query_lower for word in ["schema", "table", "structure", "metadata"]):
        intent = "metadata_exploration"
        recommended_mode = "metadata"
    elif any(word in query_lower for word in ["data", "retrieve", "get", "show me"]):
        intent = "data_retrieval"
        recommended_mode = "data"
    elif any(word in query_lower for word in ["analyze", "insights", "trends", "compare"]):
        intent = "analysis"
        recommended_mode = "analysis"
    else:
        intent = "general_inquiry"
        recommended_mode = "full"
    
    return {
        "query": query,
        "intent": intent,
        "recommended_mode": recommended_mode,
        "complexity": "moderate",  # Simple heuristic for MVP
        "suggested_agents": {
            "metadata": intent in ["metadata_exploration", "general_inquiry"],
            "entitlement": intent != "metadata_exploration",
            "data": intent in ["data_retrieval", "analysis", "general_inquiry"],
            "aggregation": intent in ["analysis", "general_inquiry"]
        },
        "confidence": "basic_heuristic",
        "timestamp": datetime.now().isoformat()
    }

# Server startup/shutdown handlers
@mcp.hook("startup")
async def startup():
    """Initialize MCP server"""
    logger.info("Multi-Agent Research MCP Server starting up")
    
    # Test connection to agent server
    try:
        agent_endpoint = os.getenv("LANGRAPH_AGENTS_ENDPOINT", "http://localhost:8001")
        response = await http_client.get(f"{agent_endpoint}/", timeout=5.0)
        if response.status_code == 200:
            logger.info("Successfully connected to agent server")
        else:
            logger.warning("Agent server not responding properly")
    except Exception as e:
        logger.warning(f"Could not connect to agent server: {e}")

@mcp.hook("shutdown")
async def shutdown():
    """Clean up MCP server"""
    logger.info("Multi-Agent Research MCP Server shutting down")
    try:
        await http_client.aclose()
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", 8082))
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    
    logger.info(f"Starting Multi-Agent Research MCP Server on {host}:{port}")
    mcp.run(host=host, port=port) 