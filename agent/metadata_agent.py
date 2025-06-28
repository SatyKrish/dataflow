#!/usr/bin/env python3
"""
Metadata Agent Implementation with LLM-Based Reasoning

Specialized agent for discovering data schemas and metadata structures.
Uses LLM to reason about metadata discovery strategies and select appropriate tools/approaches.
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from base_agent import BaseAgent
from db_client import AgentType

logger = logging.getLogger(__name__)

class MetadataAgent(BaseAgent):
    """Agent specialized in discovering data schemas and metadata using LLM reasoning"""
    
    def __init__(self):
        super().__init__(AgentType.METADATA)
        self.available_discovery_methods = self._initialize_discovery_methods()
    
    def _initialize_discovery_methods(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available metadata discovery methods"""
        return {
            "denodo_schema_discovery": {
                "description": "Query Denodo virtualization layer for schema information",
                "endpoint": os.getenv("DENODO_MCP_ENDPOINT", "http://localhost:8081"),
                "capabilities": ["table_schemas", "view_definitions", "data_source_mapping", "relationships"],
                "query_types": ["SHOW TABLES", "DESCRIBE TABLE", "SHOW VIEWS", "EXPLAIN"],
                "scope": "enterprise_data_warehouse"
            },
            "database_introspection": {
                "description": "Direct database metadata queries using system catalogs",
                "endpoint": os.getenv("DB_DIRECT_ENDPOINT"),
                "capabilities": ["system_catalogs", "foreign_keys", "indexes", "constraints"],
                "query_types": ["INFORMATION_SCHEMA", "sys.tables", "pg_catalog"],
                "scope": "direct_database_access"
            },
            "file_system_scanning": {
                "description": "Analyze file structures and data lake schemas",
                "endpoint": os.getenv("FILESYSTEM_MCP_ENDPOINT"),
                "capabilities": ["file_formats", "directory_structures", "data_lake_schemas"],
                "query_types": ["parquet_schema", "csv_headers", "json_structure"],
                "scope": "unstructured_data_sources"
            },
            "api_schema_discovery": {
                "description": "Discover API schemas and data models from external services",
                "endpoint": os.getenv("API_DISCOVERY_ENDPOINT"),
                "capabilities": ["openapi_specs", "graphql_schemas", "rest_endpoints"],
                "query_types": ["swagger_discovery", "graphql_introspection"],
                "scope": "external_apis"
            }
        }
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute metadata discovery using LLM-based reasoning and planning"""
        
        # Step 1: LLM analyzes the task and creates a discovery strategy
        discovery_strategy = await self._llm_create_discovery_strategy(task_description, context)
        
        # Step 2: LLM selects appropriate discovery methods
        method_selection = await self._llm_select_discovery_methods(discovery_strategy, task_description, context)
        
        # Step 3: Execute selected methods with LLM-guided approach
        discovery_results = await self._execute_discovery_methods(method_selection, discovery_strategy, context)
        
        # Step 4: LLM analyzes and synthesizes metadata findings
        metadata_synthesis = await self._llm_synthesize_metadata(discovery_results, task_description, context)
        
        # Step 5: LLM provides recommendations for next steps
        recommendations = await self._llm_generate_recommendations(metadata_synthesis, task_description, context)
        
        return {
            "discovery_strategy": discovery_strategy,
            "method_selection": method_selection,
            "discovery_results": discovery_results,
            "metadata_synthesis": metadata_synthesis,
            "recommendations": recommendations,
            "metadata_summary": {
                "discovery_methods_used": len(method_selection.get("selected_methods", [])),
                "schemas_discovered": self._count_discovered_schemas(discovery_results),
                "data_sources_identified": self._count_data_sources(discovery_results),
                "completeness_score": metadata_synthesis.get("completeness_score", 0.0)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _llm_create_discovery_strategy(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to create an intelligent metadata discovery strategy"""
        
        system_prompt = """
        You are a metadata discovery strategist. Your job is to analyze a data discovery request and create an intelligent strategy for discovering the most relevant metadata.

        Consider these aspects:
        1. **Scope**: What type of data sources are likely relevant?
        2. **Depth**: How detailed should the discovery be?
        3. **Priority**: What metadata is most critical for the request?
        4. **Approach**: Should discovery be broad or focused?
        5. **Relationships**: What data relationships should be explored?

        Create a strategy that maximizes discovery efficiency while ensuring completeness.
        """
        
        user_prompt = f"""
        Task: {task_description}
        Context: {json.dumps(context, indent=2)}
        
        Available discovery scopes:
        - Enterprise data warehouse (structured, relational)
        - File systems and data lakes (semi-structured, unstructured)
        - External APIs (third-party, real-time)
        - Direct database access (system catalogs, constraints)
        
        Create a metadata discovery strategy in JSON format:
        {{
            "discovery_goals": ["goal1", "goal2"],
            "priority_areas": ["area1", "area2"],
            "scope_preferences": ["enterprise", "files", "apis"],
            "depth_level": "shallow|medium|deep",
            "relationship_focus": ["table_relationships", "data_lineage", "foreign_keys"],
            "success_criteria": ["criteria1", "criteria2"],
            "estimated_complexity": "low|medium|high",
            "reasoning": "explanation of strategy"
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1000)
            strategy = json.loads(llm_response)
            logger.info(f"LLM created discovery strategy with {len(strategy.get('discovery_goals', []))} goals")
            return strategy
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM strategy creation failed: {e}, using fallback")
            return self._fallback_discovery_strategy(task_description, context)
    
    async def _llm_select_discovery_methods(self, strategy: Dict[str, Any], task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to select the best discovery methods based on strategy"""
        
        # Filter available methods based on enabled endpoints
        enabled_methods = {name: info for name, info in self.available_discovery_methods.items() 
                          if info.get("endpoint")}
        
        system_prompt = f"""
        You are a metadata discovery method selector. Based on the discovery strategy, select the most appropriate methods to achieve the goals.

        Available Discovery Methods:
        {json.dumps(enabled_methods, indent=2)}

        Selection Criteria:
        1. **Goal Alignment**: Does the method support the strategy goals?
        2. **Scope Match**: Does the method cover the preferred scopes?
        3. **Capability**: Can the method discover the required metadata types?
        4. **Efficiency**: Consider the effort vs. value of each method
        5. **Completeness**: Ensure selected methods together provide comprehensive coverage

        Strategy Context:
        {json.dumps(strategy, indent=2)}
        """
        
        user_prompt = f"""
        Task: {task_description}
        Discovery Strategy: {json.dumps(strategy, indent=2)}
        
        Select the optimal discovery methods to execute this strategy. Consider:
        1. Which methods best align with the strategy goals?
        2. What is the most efficient execution order?
        3. How can methods complement each other?
        4. What are the resource and time implications?
        
        Provide your selection in JSON format:
        {{
            "selected_methods": ["method1", "method2"],
            "execution_order": ["method1", "method2"],
            "method_reasoning": {{
                "method1": "why this method was selected",
                "method2": "why this method was selected"
            }},
            "rejected_methods": {{
                "method3": "why this method was not selected"
            }},
            "execution_strategy": "parallel|sequential|hybrid",
            "estimated_duration": "5-10 minutes",
            "confidence": 0.85
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1200)
            selection = json.loads(llm_response)
            logger.info(f"LLM selected {len(selection.get('selected_methods', []))} discovery methods")
            return selection
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM method selection failed: {e}, using fallback")
            return self._fallback_method_selection(strategy, task_description)
    
    async def _execute_discovery_methods(self, method_selection: Dict[str, Any], strategy: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute selected discovery methods with intelligent error handling"""
        
        selected_methods = method_selection.get("selected_methods", [])
        execution_strategy = method_selection.get("execution_strategy", "parallel")
        
        results = []
        
        if execution_strategy == "parallel":
            # Execute methods in parallel
            import asyncio
            tasks = []
            
            for method_name in selected_methods:
                if method_name in self.available_discovery_methods:
                    task = self._execute_single_discovery_method(method_name, strategy, context)
                    tasks.append(task)
            
            if tasks:
                parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(parallel_results):
                    if isinstance(result, Exception):
                        results.append({
                            "method": selected_methods[i],
                            "status": "error",
                            "error": str(result)
                        })
                    else:
                        results.append(result)
        else:
            # Execute methods sequentially with adaptive approach
            for method_name in selected_methods:
                if method_name in self.available_discovery_methods:
                    try:
                        result = await self._execute_single_discovery_method(method_name, strategy, context)
                        results.append(result)
                        
                        # LLM-guided adaptive execution: should we continue?
                        if len(results) > 1:
                            should_continue = await self._llm_should_continue_discovery(results, strategy, context)
                            if not should_continue:
                                logger.info("LLM determined sufficient metadata discovered, stopping early")
                                break
                                
                    except Exception as e:
                        results.append({
                            "method": method_name,
                            "status": "error",
                            "error": str(e)
                        })
        
        return results
    
    async def _execute_single_discovery_method(self, method_name: str, strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single metadata discovery method"""
        
        method_config = self.available_discovery_methods[method_name]
        endpoint = method_config["endpoint"]
        
        if not endpoint:
            return {
                "method": method_name,
                "status": "error",
                "error": "Method endpoint not configured"
            }
        
        try:
            if method_name == "denodo_schema_discovery":
                return await self._execute_denodo_discovery(method_config, strategy, context)
            elif method_name == "database_introspection":
                return await self._execute_database_introspection(method_config, strategy, context)
            elif method_name == "file_system_scanning":
                return await self._execute_filesystem_discovery(method_config, strategy, context)
            elif method_name == "api_schema_discovery":
                return await self._execute_api_discovery(method_config, strategy, context)
            else:
                return {
                    "method": method_name,
                    "status": "error",
                    "error": f"Method {method_name} not implemented"
                }
                
        except Exception as e:
            logger.error(f"Discovery method {method_name} failed: {e}")
            return {
                "method": method_name,
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_denodo_discovery(self, method_config: Dict[str, Any], strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Denodo-based metadata discovery with LLM-guided queries"""
        
        # LLM creates targeted queries based on strategy
        queries = await self._llm_create_denodo_queries(strategy, context)
        
        results = []
        endpoint = method_config["endpoint"]
        
        for query in queries:
            try:
                response = await self.http_client.post(
                    f"{endpoint}/denodo_query",
                    json={"query": query, "mode": "metadata"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results.append({
                        "query": query,
                        "result": result,
                        "status": "success"
                    })
                else:
                    results.append({
                        "query": query,
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                results.append({
                    "query": query,
                    "status": "error", 
                    "error": str(e)
                })
        
        return {
            "method": "denodo_schema_discovery",
            "status": "completed",
            "queries_executed": len(queries),
            "successful_queries": len([r for r in results if r.get("status") == "success"]),
            "results": results,
            "discovery_scope": "enterprise_data_warehouse"
        }
    
    async def _llm_create_denodo_queries(self, strategy: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Use LLM to create targeted Denodo queries based on discovery strategy"""
        
        system_prompt = """
        You are a Denodo query specialist. Create targeted SQL queries to discover metadata efficiently based on the discovery strategy.

        Available Denodo query patterns:
        - SHOW TABLES [LIKE 'pattern']
        - DESCRIBE TABLE table_name
        - SHOW VIEWS [LIKE 'pattern'] 
        - SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE condition
        - SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE condition
        
        Focus on queries that will discover the most relevant metadata for the strategy goals.
        """
        
        user_prompt = f"""
        Discovery Strategy: {json.dumps(strategy, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Create 3-5 targeted Denodo queries to discover metadata efficiently. Consider:
        1. What tables/views are most likely relevant?
        2. What schema information is needed?
        3. How to discover relationships between data sources?
        
        Return as JSON array:
        ["query1", "query2", "query3"]
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=800)
            queries = json.loads(llm_response)
            return queries if isinstance(queries, list) else ["SHOW TABLES", "SHOW VIEWS"]
        except:
            # Fallback queries
            return ["SHOW TABLES", "SHOW VIEWS", "SELECT TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES LIMIT 20"]
    
    async def _execute_database_introspection(self, method_config: Dict[str, Any], strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute direct database introspection (placeholder for now)"""
        return {
            "method": "database_introspection",
            "status": "not_implemented",
            "message": "Direct database introspection not yet implemented"
        }
    
    async def _execute_filesystem_discovery(self, method_config: Dict[str, Any], strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file system metadata discovery (placeholder for now)"""
        return {
            "method": "file_system_scanning", 
            "status": "not_implemented",
            "message": "File system scanning not yet implemented"
        }
    
    async def _execute_api_discovery(self, method_config: Dict[str, Any], strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API schema discovery (placeholder for now)"""
        return {
            "method": "api_schema_discovery",
            "status": "not_implemented", 
            "message": "API schema discovery not yet implemented"
        }
    
    async def _llm_should_continue_discovery(self, current_results: List[Dict[str, Any]], strategy: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Use LLM to determine if discovery should continue based on current results"""
        
        system_prompt = """
        You are a metadata discovery optimizer. Analyze current discovery results and determine if additional discovery methods should be executed.

        Consider:
        1. Have the strategy goals been sufficiently met?
        2. Is the metadata coverage adequate for the task?
        3. Would additional discovery provide significant value?
        4. Are there diminishing returns from further discovery?
        
        Return true to continue discovery, false to stop.
        """
        
        user_prompt = f"""
        Discovery Strategy: {json.dumps(strategy, indent=2)}
        Current Results: {json.dumps(current_results, indent=2)}
        
        Should discovery continue? Consider:
        - Goal achievement level
        - Metadata completeness
        - Value vs. cost of additional discovery
        
        Respond with just: true or false
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=100)
            return "true" in llm_response.lower()
        except:
            return True  # Default to continue if LLM fails
    
    async def _llm_synthesize_metadata(self, discovery_results: List[Dict[str, Any]], task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to synthesize and analyze all metadata discovery results"""
        
        system_prompt = """
        You are a metadata analysis specialist. Synthesize metadata discovery results into actionable insights.

        Provide:
        1. **Schema Summary**: Key schemas, tables, and structures discovered
        2. **Data Relationships**: Connections and dependencies identified
        3. **Quality Assessment**: Completeness and reliability of metadata
        4. **Business Context**: Relevance to the original task
        5. **Coverage Analysis**: What areas are well-covered vs. gaps
        """
        
        user_prompt = f"""
        Original Task: {task_description}
        Discovery Results: {json.dumps(discovery_results, indent=2)}
        
        Synthesize these metadata discovery results in JSON format:
        {{
            "schema_summary": {{
                "total_schemas": 0,
                "key_tables": ["table1", "table2"],
                "data_types_found": ["structured", "semi_structured"],
                "primary_sources": ["source1", "source2"]
            }},
            "relationships": {{
                "table_relationships": ["foreign_key_relationships"],
                "data_lineage": ["source_to_target_flows"],
                "dependencies": ["critical_dependencies"]
            }},
            "quality_assessment": {{
                "completeness_score": 0.85,
                "reliability": "high|medium|low",
                "coverage_gaps": ["gap1", "gap2"]
            }},
            "business_relevance": {{
                "task_alignment": "high|medium|low",
                "key_insights": ["insight1", "insight2"],
                "actionable_findings": ["finding1", "finding2"]
            }},
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            synthesis = json.loads(llm_response)
            return synthesis
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Metadata synthesis failed: {e}")
            return self._fallback_metadata_synthesis(discovery_results)
    
    async def _llm_generate_recommendations(self, metadata_synthesis: Dict[str, Any], task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to generate actionable recommendations based on metadata analysis"""
        
        system_prompt = """
        You are a data strategy advisor. Based on metadata discovery and analysis, provide actionable recommendations for the next steps.

        Focus on:
        1. **Data Access Strategy**: How to best access the discovered data
        2. **Quality Improvements**: How to address any metadata gaps
        3. **Investigation Priorities**: What should be explored further
        4. **Risk Mitigation**: Potential data quality or access issues
        """
        
        user_prompt = f"""
        Task: {task_description}
        Metadata Synthesis: {json.dumps(metadata_synthesis, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Provide strategic recommendations in JSON format:
        {{
            "immediate_actions": ["action1", "action2"],
            "data_access_strategy": "recommended approach for accessing the data",
            "quality_improvements": ["improvement1", "improvement2"],
            "further_investigation": ["area1", "area2"],
            "risk_considerations": ["risk1", "risk2"],
            "success_metrics": ["metric1", "metric2"],
            "estimated_effort": "low|medium|high",
            "priority_ranking": ["highest_priority", "medium_priority", "lower_priority"]
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1200)
            recommendations = json.loads(llm_response)
            return recommendations
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Recommendations generation failed: {e}")
            return {"error": "Failed to generate recommendations", "fallback": "Proceed with manual data exploration"}
    
    def _fallback_discovery_strategy(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback strategy when LLM fails"""
        return {
            "discovery_goals": ["schema_discovery", "relationship_mapping"],
            "priority_areas": ["enterprise_data"],
            "scope_preferences": ["enterprise"],
            "depth_level": "medium",
            "relationship_focus": ["table_relationships"],
            "success_criteria": ["identify_relevant_tables"],
            "estimated_complexity": "medium",
            "reasoning": "Fallback strategy - comprehensive enterprise metadata discovery"
        }
    
    def _fallback_method_selection(self, strategy: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Fallback method selection when LLM fails"""
        available_methods = [name for name, config in self.available_discovery_methods.items() 
                           if config.get("endpoint")]
        
        return {
            "selected_methods": available_methods[:2],  # Use first 2 available
            "execution_order": available_methods[:2],
            "method_reasoning": {"fallback": "LLM selection failed, using available methods"},
            "execution_strategy": "sequential",
            "confidence": 0.5
        }
    
    def _count_discovered_schemas(self, discovery_results: List[Dict[str, Any]]) -> int:
        """Count total schemas discovered across all methods"""
        total = 0
        for result in discovery_results:
            if result.get("status") == "completed":
                results = result.get("results", [])
                for res in results:
                    if res.get("status") == "success" and res.get("result"):
                        # Count based on result structure
                        total += len(res.get("result", {}).get("tables", []))
        return total
    
    def _count_data_sources(self, discovery_results: List[Dict[str, Any]]) -> int:
        """Count unique data sources identified"""
        sources = set()
        for result in discovery_results:
            if result.get("discovery_scope"):
                sources.add(result["discovery_scope"])
        return len(sources)
    
    def _fallback_metadata_synthesis(self, discovery_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback metadata synthesis when LLM fails"""
        successful_results = [r for r in discovery_results if r.get("status") in ["completed", "success"]]
        
        return {
            "schema_summary": {
                "total_schemas": self._count_discovered_schemas(discovery_results),
                "methods_used": len(discovery_results),
                "successful_methods": len(successful_results)
            },
            "quality_assessment": {
                "completeness_score": 0.7 if successful_results else 0.3,
                "reliability": "medium",
                "coverage_gaps": ["LLM synthesis failed - manual review needed"]
            },
            "error": "LLM synthesis failed, basic summary provided"
        } 