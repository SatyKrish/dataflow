#!/usr/bin/env python3
"""
Multi-Agent Research System - MCP Server

A FastMCP server that provides multi-agent research capabilities by coordinating
with langraph-based agents in the agent/ folder. This server acts as the single
point of interaction for the chat interface.

Usage:
    python fastmcp_server.py

Environment Variables:
    AZURE_OPENAI_API_KEY: The Azure OpenAI API key for generating responses
    AZURE_OPENAI_ENDPOINT: The Azure OpenAI endpoint URL
    AZURE_OPENAI_DEPLOYMENT: The Azure OpenAI deployment name to use
    AZURE_OPENAI_API_VERSION: The Azure OpenAI API version to use
    POSTGRES_HOST: PostgreSQL host (default: localhost)
    POSTGRES_PORT: PostgreSQL port (default: 5432)
    POSTGRES_DB: PostgreSQL database name (default: dataflow_agents)
    POSTGRES_USER: PostgreSQL username (default: postgres)
    POSTGRES_PASSWORD: PostgreSQL password (default: postgres)
    REDIS_HOST: Redis host (default: localhost)
    REDIS_PORT: Redis port (default: 6379)
    MCP_SERVER_PORT: Port to run the server on (default: 8080)
    MCP_SERVER_HOST: Host to bind the server to (default: 0.0.0.0)
"""

import os
import logging
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file if python-dotenv is not available
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from fastmcp import FastMCP, Context
from openai import AsyncAzureOpenAI
import httpx

# Import local database client
from db_client import db_client, SessionStatus, AgentType, ExecutionStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate required environment variables
required_env_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT", 
    "AZURE_OPENAI_DEPLOYMENT",
    "AZURE_OPENAI_API_VERSION"
]

for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"{var} environment variable is required")

# Initialize Azure OpenAI client
openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# HTTP client for calling langraph agents
http_client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout for complex research

# Create FastMCP server
mcp = FastMCP(
    name="multi-agent-research",
    instructions="""
    Multi-Agent Research System providing intelligent data discovery and analysis across multiple sources.
    
    This system uses specialized AI agents to:
    - Analyze user queries and develop research strategies
    - Discover metadata and schemas across data sources  
    - Validate data access permissions and entitlements
    - Retrieve and process data from multiple sources
    - Aggregate and synthesize findings into comprehensive responses
    
    The system coordinates multiple specialized agents working in parallel for efficient and thorough research.
    
    Available capabilities:
    - Multi-agent research with automatic task decomposition
    - Cross-source metadata discovery and data retrieval
    - Intelligent entitlement checking and access validation
    - Parallel subagent execution for speed and coverage
    - Session management and context preservation
    - Health monitoring and analytics
    """
)

@mcp.tool
async def multi_agent_research(
    query: str,
    user_email: str = "default@example.com",
    session_id: Optional[str] = None,
    research_mode: Literal["metadata", "data", "analysis", "full"] = "full"
) -> Dict[str, Any]:
    """Perform multi-agent research across data sources using specialized AI agents.
    
    Args:
        query: Natural language research query or request
        user_email: User identifier for session tracking and entitlements
        session_id: Optional existing session ID to continue research
        research_mode: Research scope:
            - 'metadata': Focus on schema and structure discovery
            - 'data': Focus on data retrieval and processing  
            - 'analysis': Focus on data analysis and insights
            - 'full': Complete research with all agents (default)
    
    Returns:
        Comprehensive research results with agent findings, citations, and metadata
    """
    if not query.strip():
        return {"error": "Query cannot be empty"}
    
    logger.info(f"Starting multi-agent research for query: {query[:100]}...")
    start_time = time.time()
    
    try:
        # Initialize database connection if needed
        if not db_client.pool:
            await db_client.connect()
        
        # Get or create user
        user_id = await db_client.get_or_create_user(user_email)
        
        # Create or get research session
        if session_id:
            session = await db_client.get_research_session(session_id)
            if not session:
                return {"error": f"Session {session_id} not found"}
        else:
            session_id = await db_client.create_research_session(
                user_id=user_id,
                initial_query=query
            )
        
        logger.info(f"Research session: {session_id}")
        
        # Develop research plan
        research_plan = await _develop_research_plan(query, research_mode)
        
        # Update session with research plan
        await db_client.update_research_session(
            session_id=session_id,
            research_plan=research_plan
        )
        
        # Store research plan in session memory
        await db_client.store_session_memory(
            session_id=session_id,
            memory_type=MemoryType.RESEARCH_PLAN,
            content=research_plan
        )
        
        # Execute research using langraph agents
        research_results = await _execute_research_plan(
            session_id=session_id,
            research_plan=research_plan,
            query=query
        )
        
        # Calculate execution time and token usage
        execution_time = int((time.time() - start_time) * 1000)
        total_tokens = research_results.get('total_tokens', 0)
        
        # Prepare final outcome
        final_outcome = {
            "query": query,
            "research_mode": research_mode,
            "research_plan": research_plan,
            "agent_results": research_results.get('agent_results', {}),
            "aggregated_findings": research_results.get('aggregated_findings', {}),
            "citations": research_results.get('citations', []),
            "execution_time_ms": execution_time,
            "total_tokens": total_tokens,
            "session_id": session_id
        }
        
        # Update session as completed
        await db_client.update_research_session(
            session_id=session_id,
            status=SessionStatus.COMPLETED,
            final_outcome=final_outcome,
            token_usage=total_tokens
        )
        
        logger.info(f"Research completed in {execution_time}ms with {total_tokens} tokens")
        
        return final_outcome
        
    except Exception as e:
        logger.error(f"Multi-agent research error: {str(e)}")
        
        # Update session as failed if we have session_id
        if session_id:
            try:
                await db_client.update_research_session(
                    session_id=session_id,
                    status=SessionStatus.FAILED
                )
            except:
                pass
        
        return {"error": f"Research failed: {str(e)}"}

@mcp.tool 
async def analyze_query_intent(query: str) -> Dict[str, Any]:
    """Analyze user query to determine research intent and strategy.
    
    Args:
        query: Natural language query to analyze
        
    Returns:
        Intent analysis with recommended research approach
    """
    if not query.strip():
        return {"error": "Query cannot be empty"}
    
    logger.info(f"Analyzing query intent: {query[:100]}...")
    
    system_prompt = """
    You are a query intent analyzer for a multi-agent research system. Analyze the user's query and determine:
    
    1. Research type: metadata exploration, data retrieval, cross-source analysis, or general inquiry
    2. Data sources likely needed: databases, APIs, documents, etc.
    3. Required agents: metadata, entitlement, data, aggregation
    4. Complexity level: simple (1-2 agents), moderate (2-3 agents), complex (3-4 agents)
    5. Recommended research mode: metadata, data, analysis, or full
    
    Respond with a JSON object containing your analysis.
    """
    
    user_prompt = f"""
    Analyze this query and provide research recommendations:
    
    Query: "{query}"
    
    Provide analysis in this JSON format:
    {{
        "research_type": "metadata|data|analysis|inquiry",
        "complexity_level": "simple|moderate|complex", 
        "recommended_mode": "metadata|data|analysis|full",
        "required_agents": ["metadata", "entitlement", "data", "aggregation"],
        "data_sources": ["source1", "source2"],
        "strategy_notes": "Brief explanation of recommended approach"
    }}
    """
    
    try:
        response = await openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content
        
        # Try to parse JSON response
        try:
            intent_analysis = json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            intent_analysis = {
                "research_type": "inquiry",
                "complexity_level": "moderate",
                "recommended_mode": "full",
                "required_agents": ["metadata", "data"],
                "data_sources": ["unknown"],
                "strategy_notes": "Could not parse detailed analysis, using default approach"
            }
        
        logger.info("Query intent analysis completed")
        return intent_analysis
        
    except Exception as e:
        logger.error(f"Intent analysis error: {str(e)}")
        return {"error": f"Intent analysis failed: {str(e)}"}

@mcp.tool
async def get_session_status(session_id: str) -> Dict[str, Any]:
    """Get the current status and progress of a research session.
    
    Args:
        session_id: Research session ID to check
        
    Returns:
        Session status with agent execution details
    """
    try:
        if not db_client.pool:
            await db_client.connect()
        
        # Get session details
        session = await db_client.get_research_session(session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}
        
        # Get subagent executions
        executions = await db_client.get_session_executions(session_id)
        
        # Get session memory
        memories = await db_client.get_session_memory(session_id)
        
        status_info = {
            "session_id": session_id,
            "status": session.status.value,
            "initial_query": session.initial_query,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "token_usage": session.token_usage,
            "research_plan": session.research_plan,
            "subagent_executions": [
                {
                    "execution_id": exec.execution_id,
                    "agent_type": exec.agent_type.value,
                    "status": exec.status.value,
                    "task_description": exec.task_description,
                    "execution_time_ms": exec.execution_time_ms,
                    "error_message": exec.error_message
                }
                for exec in executions
            ],
            "memory_count": len(memories)
        }
        
        return status_info
        
    except Exception as e:
        logger.error(f"Get session status error: {str(e)}")
        return {"error": f"Failed to get session status: {str(e)}"}

@mcp.tool
async def health_check() -> Dict[str, Any]:
    """Check the health status of the multi-agent research system.
    
    Returns:
        Health status including database, external services, and recent performance
    """
    logger.info("Performing health check")
    
    health_status = {
        "server_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_name": "Multi-Agent Research MCP Server",
        "version": "1.0.0-mvp"
    }
    
    # Test Azure OpenAI connection
    try:
        test_response = await openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        health_status["azure_openai_status"] = "connected"
        health_status["azure_openai_model"] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    except Exception as e:
        health_status["azure_openai_status"] = f"error: {str(e)}"
    
    # Test database connection
    try:
        if not db_client.pool:
            await db_client.connect()
        
        # Test basic query
        test_result = await db_client.execute_value("SELECT 1")
        if test_result == 1:
            health_status["database_status"] = "connected"
            
            # Get recent analytics
            analytics = await db_client.get_session_analytics(days=1)
            health_status["recent_analytics"] = analytics
        else:
            health_status["database_status"] = "error: test query failed"
            
    except Exception as e:
        health_status["database_status"] = f"error: {str(e)}"
    
    # Test langraph agents endpoint (if running)
    try:
        # This would be the endpoint where langraph agents are running
        agent_endpoint = os.getenv("LANGRAPH_AGENTS_ENDPOINT", "http://localhost:8001")
        response = await http_client.get(f"{agent_endpoint}/health", timeout=5.0)
        if response.status_code == 200:
            health_status["langraph_agents_status"] = "connected"
        else:
            health_status["langraph_agents_status"] = f"error: HTTP {response.status_code}"
    except Exception as e:
        health_status["langraph_agents_status"] = f"error: {str(e)}"
    
    return health_status

@mcp.tool
async def get_system_analytics(days: int = 7) -> Dict[str, Any]:
    """Get system performance analytics for the specified time period.
    
    Args:
        days: Number of days to analyze (default: 7)
        
    Returns:
        Analytics data including session statistics and agent performance
    """
    try:
        if not db_client.pool:
            await db_client.connect()
        
        analytics = await db_client.get_session_analytics(days=days)
        
        return {
            "time_period_days": days,
            "generated_at": datetime.now().isoformat(),
            **analytics
        }
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return {"error": f"Failed to get analytics: {str(e)}"}

# Helper functions

async def _develop_research_plan(query: str, research_mode: str) -> Dict[str, Any]:
    """Develop a research plan for the given query"""
    system_prompt = """
    You are a research strategist for a multi-agent system. Create a detailed research plan that will guide specialized agents.
    
    Consider:
    - What information is needed to answer the query
    - Which data sources should be explored
    - What metadata discovery is required
    - How to break down the work for parallel execution
    - What entitlement checks are needed
    
    Create a plan that maximizes parallel execution while ensuring thorough coverage.
    """
    
    user_prompt = f"""
    Create a research plan for this query in {research_mode} mode:
    
    Query: "{query}"
    Mode: {research_mode}
    
    Provide a JSON research plan with:
    {{
        "objective": "Clear research objective",
        "approach": "Overall strategy",
        "agent_tasks": {{
            "metadata": "Specific task for metadata agent",
            "entitlement": "Specific task for entitlement agent", 
            "data": "Specific task for data agent",
            "aggregation": "Specific task for aggregation agent"
        }},
        "execution_order": ["parallel_group_1", "parallel_group_2"],
        "success_criteria": "How to measure successful completion"
    }}
    """
    
    try:
        response = await openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        plan_text = response.choices[0].message.content
        
        try:
            research_plan = json.loads(plan_text)
        except json.JSONDecodeError:
            # Fallback plan if JSON parsing fails
            research_plan = {
                "objective": f"Research and analyze: {query}",
                "approach": f"Multi-agent {research_mode} research",
                "agent_tasks": {
                    "metadata": "Discover relevant data sources and schemas",
                    "entitlement": "Validate data access permissions",
                    "data": "Retrieve and process relevant data",
                    "aggregation": "Synthesize findings into comprehensive response"
                },
                "execution_order": ["metadata,entitlement", "data", "aggregation"],
                "success_criteria": "Complete answer to user query with proper citations"
            }
        
        return research_plan
        
    except Exception as e:
        logger.error(f"Research plan development error: {str(e)}")
        # Return basic fallback plan
        return {
            "objective": f"Research: {query}",
            "approach": "Basic multi-agent research",
            "agent_tasks": {
                "metadata": "Discover data sources",
                "data": "Retrieve relevant data"
            },
            "execution_order": ["metadata", "data"],
            "success_criteria": "Answer user query"
        }

async def _execute_research_plan(
    session_id: str, 
    research_plan: Dict[str, Any], 
    query: str
) -> Dict[str, Any]:
    """Execute the research plan using langraph agents"""
    logger.info(f"Executing research plan for session {session_id}")
    
    try:
        # Call langraph agents endpoint
        agent_endpoint = os.getenv("LANGRAPH_AGENTS_ENDPOINT", "http://localhost:8001")
        
        request_payload = {
            "session_id": session_id,
            "query": query,
            "research_plan": research_plan
        }
        
        response = await http_client.post(
            f"{agent_endpoint}/execute_research",
            json=request_payload,
            timeout=300.0  # 5 minute timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Langraph agents error: HTTP {response.status_code}")
            return {
                "error": f"Agent execution failed with status {response.status_code}",
                "agent_results": {},
                "total_tokens": 0
            }
            
    except Exception as e:
        logger.error(f"Research execution error: {str(e)}")
        
        # Fallback: simple research using available tools
        return await _fallback_research_execution(session_id, query, research_plan)

async def _fallback_research_execution(
    session_id: str,
    query: str, 
    research_plan: Dict[str, Any]
) -> Dict[str, Any]:
    """Fallback research execution when langraph agents are not available"""
    logger.info("Using fallback research execution")
    
    # Simple implementation that calls existing MCP tools
    agent_results = {}
    total_tokens = 0
    
    try:
        # Try to call demo MCP server for basic research
        demo_endpoint = os.getenv("DEMO_MCP_ENDPOINT", "http://localhost:8080")
        
        demo_response = await http_client.post(
            f"{demo_endpoint}/ask_ai",
            json={"question": query, "mode": "analyze"},
            timeout=60.0
        )
        
        if demo_response.status_code == 200:
            demo_result = demo_response.json()
            agent_results["demo_research"] = demo_result
            total_tokens += 500  # Estimate
            
    except Exception as e:
        logger.warning(f"Demo MCP call failed: {str(e)}")
        agent_results["demo_research"] = {"error": str(e)}
    
    return {
        "agent_results": agent_results,
        "aggregated_findings": {
            "summary": f"Basic research completed for: {query}",
            "method": "fallback_execution"
        },
        "citations": [],
        "total_tokens": total_tokens
    }

# Initialize database connection on startup
@mcp.hook("startup")
async def startup():
    """Initialize connections on server startup"""
    logger.info("Initializing Multi-Agent Research MCP Server...")
    try:
        await db_client.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Continue without database for basic functionality

@mcp.hook("shutdown") 
async def shutdown():
    """Clean up connections on server shutdown"""
    logger.info("Shutting down Multi-Agent Research MCP Server...")
    try:
        await db_client.disconnect()
        await http_client.aclose()
        logger.info("Connections closed successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

if __name__ == "__main__":
    # Run the FastMCP server
    port = int(os.getenv("MCP_SERVER_PORT", 8080))
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    
    logger.info(f"Starting Multi-Agent Research MCP Server on {host}:{port}")
    mcp.run(host=host, port=port) 