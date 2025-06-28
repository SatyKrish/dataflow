#!/usr/bin/env python3
"""
Data Agent Implementation with LLM-Based Tool Selection

Specialized agent for data retrieval and processing operations.
Uses LLM to intelligently decide which MCP tools to call based on query analysis.
Discovers tools dynamically from configured MCP servers.
"""

import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime

from base_agent import BaseAgent
from db_client import AgentType

logger = logging.getLogger(__name__)

class DataAgent(BaseAgent):
    """Agent specialized in data retrieval with intelligent tool selection"""
    
    def __init__(self):
        super().__init__(AgentType.DATA)
        self.mcp_config_path = os.getenv("MCP_CONFIG_PATH", "/app/mcp_config.json")
        self.mcp_servers = self._load_mcp_config()
        self.available_tools = {}  # Will be populated by discovery
    
    def _load_mcp_config(self) -> Dict[str, Dict[str, Any]]:
        """Load MCP server configuration"""
        try:
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
                return config.get("servers", {})
        except FileNotFoundError:
            logger.warning(f"MCP config file not found: {self.mcp_config_path}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            return {}
    
    async def _discover_tools_from_mcp_servers(self) -> Dict[str, Any]:
        """Discover available tools from all configured MCP servers"""
        
        discovered_tools = {}
        
        for server_name, server_config in self.mcp_servers.items():
            if server_config.get("type") != "http":
                continue  # Only support HTTP servers for now
            
            server_url = server_config.get("url")
            if not server_url:
                continue
            
            try:
                # Discover tools from this MCP server
                tools = await self._get_tools_from_mcp_server(server_name, server_url, server_config)
                
                for tool in tools:
                    tool_name = tool.get("name")
                    if tool_name:
                        discovered_tools[f"{server_name}:{tool_name}"] = {
                            "server_name": server_name,
                            "server_url": server_url,
                            "tool_name": tool_name,
                            "description": tool.get("description", ""),
                            "input_schema": tool.get("inputSchema", {}),
                            "server_config": server_config
                        }
                        
                logger.info(f"Discovered {len(tools)} tools from MCP server: {server_name}")
                
            except Exception as e:
                logger.warning(f"Failed to discover tools from {server_name}: {e}")
        
        self.available_tools = discovered_tools
        logger.info(f"Total discovered tools: {len(discovered_tools)}")
        return discovered_tools
    
    async def _get_tools_from_mcp_server(self, server_name: str, server_url: str, server_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get tools list from an MCP server"""
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if server_config.get("headers"):
            headers.update(server_config["headers"])
        
        # Make MCP list_tools request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        timeout = server_config.get("timeout", 30000) / 1000  # Convert to seconds
        
        try:
            response = await self.http_client.post(
                server_url,
                json=mcp_request,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                mcp_response = response.json()
                if "result" in mcp_response and "tools" in mcp_response["result"]:
                    return mcp_response["result"]["tools"]
                else:
                    logger.warning(f"Unexpected response format from {server_name}")
                    return []
            else:
                logger.warning(f"HTTP {response.status_code} from {server_name}: {response.text}")
                return []
                
        except Exception as e:
            logger.warning(f"Error calling {server_name}: {e}")
            return []
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data retrieval using LLM-selected tools"""
        
        # Step 1: Discover available tools from MCP servers
        await self._discover_tools_from_mcp_servers()
        
        # Step 2: Use LLM to analyze query and select appropriate tools
        tool_selection = await self._llm_select_tools(task_description, context)
        
        # Step 3: Execute selected tools
        tool_results = await self._execute_selected_tools(tool_selection, task_description, context)
        
        # Step 4: Use LLM to analyze and synthesize results
        final_analysis = await self._llm_analyze_results(tool_results, task_description, context)
        
        return {
            "tool_discovery": {
                "discovered_tools": len(self.available_tools),
                "available_servers": list(self.mcp_servers.keys())
            },
            "tool_selection_reasoning": tool_selection,
            "tool_executions": tool_results,
            "final_analysis": final_analysis,
            "data_summary": {
                "tools_selected": len(tool_selection.get("selected_tools", [])),
                "tools_executed": len([r for r in tool_results if "error" not in r]),
                "total_tools_available": len(self.available_tools),
                "data_quality": "validated" if tool_results else "no_data"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _llm_select_tools(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to intelligently select which tools to use"""
        
        if not self.available_tools:
            return {
                "selected_tools": [],
                "reasoning": {"error": "No tools available for selection"},
                "confidence": 0.0
            }
        
        # Prepare tool information for LLM
        tools_for_llm = {}
        for tool_id, tool_info in self.available_tools.items():
            tools_for_llm[tool_id] = {
                "server": tool_info["server_name"],
                "tool": tool_info["tool_name"],
                "description": tool_info["description"],
                "input_schema": tool_info.get("input_schema", {})
            }
        
        system_prompt = f"""
        You are a data tool selection specialist. Your job is to analyze a data request and intelligently select the most appropriate tools from available MCP servers.

        Available Tools (from MCP servers):
        {json.dumps(tools_for_llm, indent=2)}

        Selection Criteria:
        1. **Relevance**: Does the tool's description match the request?
        2. **Server Capability**: Consider what each MCP server is designed for
        3. **Input Schema**: Does the tool accept the right parameters?
        4. **Completeness**: Select tools that together provide comprehensive coverage

        Server Descriptions:
        - demoAgent: AI-powered synthetic data generation and examples
        - denodoAgent: Enterprise data warehouse queries and real data access
        - Other servers: Check their tool descriptions for capabilities

        Return your analysis in this JSON format:
        {{
            "selected_tools": ["server:tool_name", "server:tool_name"],
            "reasoning": {{
                "server:tool_name": "why this tool was selected"
            }},
            "rejected_tools": {{
                "server:tool_name": "why this tool was not selected"
            }},
            "execution_strategy": "parallel" or "sequential",
            "confidence": 0.85
        }}
        """
        
        # Include context from metadata and entitlement agents if available
        metadata_context = ""
        if context.get("metadata_results"):
            metadata_context = f"\nMetadata Agent Results: {json.dumps(context['metadata_results'], indent=2)}"
        
        entitlement_context = ""
        if context.get("entitlement_results"):
            entitlement_context = f"\nEntitlement Agent Results: {json.dumps(context['entitlement_results'], indent=2)}"
        
        user_prompt = f"""
        Data Request: {task_description}
        
        Additional Context:
        - User Query: {context.get("query", "Not provided")}
        - User Email: {context.get("user_email", "Not provided")}
        {metadata_context}
        {entitlement_context}
        
        Analyze this request and select the most appropriate MCP tools to fulfill it. Consider:
        1. What type of data is being requested?
        2. Which MCP servers are most likely to have relevant tools?
        3. Should tools be called in parallel or sequentially?
        4. How do the metadata and entitlement findings influence tool selection?
        
        Provide your tool selection with clear reasoning.
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            
            # Parse LLM response
            try:
                tool_selection = json.loads(llm_response)
                logger.info(f"LLM selected tools: {tool_selection.get('selected_tools', [])}")
                return tool_selection
            except json.JSONDecodeError:
                logger.warning("LLM response was not valid JSON, using fallback selection")
                return self._fallback_tool_selection(task_description, context)
                
        except Exception as e:
            logger.error(f"LLM tool selection failed: {e}")
            return self._fallback_tool_selection(task_description, context)
    
    def _fallback_tool_selection(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback tool selection using simple heuristics"""
        
        task_lower = task_description.lower()
        query_lower = context.get("query", "").lower()
        combined_text = f"{task_lower} {query_lower}"
        
        selected_tools = []
        reasoning = {}
        
        # Simple heuristic selection based on available tools
        for tool_id, tool_info in self.available_tools.items():
            server_name = tool_info["server_name"]
            tool_name = tool_info["tool_name"]
            description = tool_info["description"].lower()
            
            # Basic keyword matching
            if any(word in combined_text for word in ["customer", "sales", "real", "data"]):
                if "denodo" in server_name.lower() or "enterprise" in description:
                    selected_tools.append(tool_id)
                    reasoning[tool_id] = "Matched enterprise data keywords"
            
            if any(word in combined_text for word in ["example", "sample", "test", "synthetic"]):
                if "demo" in server_name.lower() or "synthetic" in description:
                    selected_tools.append(tool_id)
                    reasoning[tool_id] = "Matched synthetic data keywords"
        
        # If no matches, select first available tool from each server
        if not selected_tools:
            seen_servers = set()
            for tool_id, tool_info in self.available_tools.items():
                server_name = tool_info["server_name"]
                if server_name not in seen_servers:
                    selected_tools.append(tool_id)
                    reasoning[tool_id] = "Default selection for comprehensive coverage"
                    seen_servers.add(server_name)
        
        return {
            "selected_tools": selected_tools,
            "reasoning": reasoning,
            "execution_strategy": "parallel",
            "confidence": 0.6,
            "selection_method": "fallback_heuristics"
        }
    
    async def _execute_selected_tools(
        self, 
        tool_selection: Dict[str, Any], 
        task_description: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute the tools selected by LLM"""
        
        selected_tools = tool_selection.get("selected_tools", [])
        execution_strategy = tool_selection.get("execution_strategy", "parallel")
        
        tool_results = []
        
        if execution_strategy == "parallel":
            # Execute tools in parallel
            import asyncio
            tasks = []
            
            for tool_id in selected_tools:
                if tool_id in self.available_tools:
                    task = self._execute_single_mcp_tool(tool_id, task_description, context)
                    tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        tool_results.append({
                            "tool": selected_tools[i],
                            "status": "error",
                            "error": str(result)
                        })
                    else:
                        tool_results.append(result)
        else:
            # Execute tools sequentially
            for tool_id in selected_tools:
                if tool_id in self.available_tools:
                    try:
                        result = await self._execute_single_mcp_tool(tool_id, task_description, context)
                        tool_results.append(result)
                    except Exception as e:
                        tool_results.append({
                            "tool": tool_id,
                            "status": "error",
                            "error": str(e)
                        })
        
        return tool_results
    
    async def _execute_single_mcp_tool(
        self, 
        tool_id: str, 
        task_description: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single MCP tool"""
        
        tool_info = self.available_tools[tool_id]
        server_url = tool_info["server_url"]
        tool_name = tool_info["tool_name"]
        server_config = tool_info["server_config"]
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if server_config.get("headers"):
            headers.update(server_config["headers"])
        
        # Prepare tool arguments based on tool and context
        tool_args = self._prepare_tool_arguments(tool_info, task_description, context)
        
        # Make MCP tool call request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        
        timeout = server_config.get("timeout", 60000) / 1000  # Convert to seconds
        
        try:
            response = await self.http_client.post(
                server_url,
                json=mcp_request,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                mcp_response = response.json()
                
                if "result" in mcp_response:
                    return {
                        "tool": tool_id,
                        "status": "success",
                        "result": mcp_response["result"],
                        "server": tool_info["server_name"],
                        "tool_name": tool_name
                    }
                elif "error" in mcp_response:
                    return {
                        "tool": tool_id,
                        "status": "error",
                        "error": f"MCP error: {mcp_response['error']}"
                    }
                else:
                    return {
                        "tool": tool_id,
                        "status": "error",
                        "error": "Unexpected MCP response format"
                    }
            else:
                return {
                    "tool": tool_id,
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Tool {tool_id} execution failed: {e}")
            return {
                "tool": tool_id,
                "status": "error",
                "error": str(e)
            }
    
    def _prepare_tool_arguments(self, tool_info: Dict[str, Any], task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for calling an MCP tool"""
        
        tool_name = tool_info["tool_name"]
        server_name = tool_info["server_name"]
        
        # Default arguments
        args = {}
        
        # Server-specific argument preparation
        if "demo" in server_name.lower():
            if "ask_ai" in tool_name:
                args = {
                    "question": task_description,
                    "mode": "generate"
                }
        elif "denodo" in server_name.lower():
            if "query" in tool_name:
                query = context.get("query", task_description)
                args = {
                    "query": query,
                    "mode": "data"
                }
        else:
            # Generic tool arguments
            args = {
                "query": context.get("query", task_description),
                "context": task_description
            }
        
        return args
    
    async def _llm_analyze_results(
        self, 
        tool_results: List[Dict[str, Any]], 
        task_description: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to analyze and synthesize the results from selected tools"""
        
        system_prompt = """
        You are a data analysis specialist. Your job is to analyze results from multiple MCP tools and provide comprehensive insights.
        
        Analyze the tool results and provide:
        1. Summary of data retrieved from each MCP server
        2. Quality assessment of the data
        3. Key insights and findings
        4. Recommendations for further analysis
        5. Any data limitations or caveats
        
        Focus on practical insights that help the user understand the data.
        """
        
        user_prompt = f"""
        Original Request: {task_description}
        Context: {json.dumps(context, indent=2)}
        
        MCP Tool Execution Results:
        {json.dumps(tool_results, indent=2)}
        
        Provide a comprehensive analysis of these results in JSON format:
        {{
            "summary": "Overall summary of data retrieved",
            "data_quality": {{
                "completeness": "assessment of data completeness",
                "accuracy": "assessment of data accuracy", 
                "relevance": "how relevant the data is to the request"
            }},
            "key_insights": ["insight 1", "insight 2"],
            "recommendations": ["recommendation 1", "recommendation 2"],
            "limitations": ["limitation 1", "limitation 2"],
            "next_steps": ["suggested next step 1", "suggested next step 2"]
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=2000)
            
            try:
                analysis = json.loads(llm_response)
                return analysis
            except json.JSONDecodeError:
                return {"analysis": llm_response, "format": "unstructured"}
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "raw_results": tool_results
            } 