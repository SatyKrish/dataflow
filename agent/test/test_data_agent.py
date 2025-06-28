#!/usr/bin/env python3
"""
Test script for LLM-based Data Agent tool selection

Demonstrates how the Data Agent uses LLM to intelligently select which MCP tools to call
based on different types of queries. Tools are discovered dynamically from MCP servers.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_agent import DataAgent

# Test scenarios with different query types
TEST_SCENARIOS = [
    {
        "name": "Enterprise Data Query",
        "task": "Retrieve customer sales data for Q4 2023",
        "context": {
            "query": "Show me customer sales data for the last quarter",
            "user_email": "analyst@company.com",
            "metadata_results": {
                "identified_tables": ["customer_sales", "quarterly_reports"],
                "data_sources": ["sales_db", "reporting_warehouse"]
            },
            "entitlement_results": {
                "access_granted": True,
                "allowed_tables": ["customer_sales"],
                "restrictions": ["no_pii_fields"]
            }
        },
        "expected_servers": ["denodoAgent"]
    },
    {
        "name": "Synthetic Data Request",
        "task": "Generate sample customer data for testing",
        "context": {
            "query": "I need some test customer data for my application prototype",
            "user_email": "developer@company.com"
        },
        "expected_servers": ["demoAgent"]
    },
    {
        "name": "Mixed Data Exploration",
        "task": "Analyze customer behavior patterns",
        "context": {
            "query": "Help me understand customer behavior patterns with examples",
            "user_email": "researcher@company.com",
            "metadata_results": {
                "identified_tables": ["customer_behavior", "interaction_logs"],
                "data_sources": ["analytics_db"]
            }
        },
        "expected_servers": ["denodoAgent", "demoAgent"]
    },
    {
        "name": "Unclear Request",
        "task": "I need some data",
        "context": {
            "query": "Can you help me with data?",
            "user_email": "user@company.com"
        },
        "expected_servers": ["demoAgent"]  # Fallback to available
    }
]

async def test_mcp_config_loading():
    """Test loading MCP configuration"""
    
    print("📄 Testing MCP Configuration Loading")
    print("=" * 50)
    
    data_agent = DataAgent()
    
    print(f"MCP Config Path: {data_agent.mcp_config_path}")
    print(f"Loaded MCP Servers: {list(data_agent.mcp_servers.keys())}")
    
    for server_name, config in data_agent.mcp_servers.items():
        print(f"\n🖥️  Server: {server_name}")
        print(f"   Type: {config.get('type', 'unknown')}")
        print(f"   URL: {config.get('url', 'not configured')}")
        print(f"   Description: {config.get('description', 'no description')}")
        print(f"   Timeout: {config.get('timeout', 'default')}ms")
    
    return len(data_agent.mcp_servers) > 0

async def test_tool_discovery():
    """Test dynamic tool discovery from MCP servers"""
    
    print("\n🔍 Testing Tool Discovery from MCP Servers")
    print("=" * 60)
    
    data_agent = DataAgent()
    
    try:
        discovered_tools = await data_agent._discover_tools_from_mcp_servers()
        
        print(f"Total discovered tools: {len(discovered_tools)}")
        
        if discovered_tools:
            print("\nDiscovered Tools:")
            for tool_id, tool_info in discovered_tools.items():
                print(f"\n🛠️  {tool_id}")
                print(f"   Server: {tool_info['server_name']}")
                print(f"   Tool: {tool_info['tool_name']}")
                print(f"   Description: {tool_info['description'][:100]}...")
                
                # Show input schema if available
                input_schema = tool_info.get('input_schema', {})
                if input_schema and 'properties' in input_schema:
                    props = list(input_schema['properties'].keys())[:3]
                    print(f"   Input Parameters: {', '.join(props)}{'...' if len(input_schema['properties']) > 3 else ''}")
        else:
            print("⚠️  No tools discovered. Make sure MCP servers are running.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        return False

async def test_tool_selection():
    """Test the LLM-based tool selection logic"""
    
    print("\n🤖 Testing LLM-Based Tool Selection")
    print("=" * 50)
    
    # Initialize the data agent and discover tools
    data_agent = DataAgent()
    
    # First discover tools
    discovered = await data_agent._discover_tools_from_mcp_servers()
    if not discovered:
        print("⚠️  Skipping tool selection tests - no tools available")
        return
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n📋 Test Scenario {i}: {scenario['name']}")
        print(f"Task: {scenario['task']}")
        
        try:
            # Test tool selection
            tool_selection = await data_agent._llm_select_tools(
                scenario["task"], 
                scenario["context"]
            )
            
            print(f"\n🤖 LLM Tool Selection Result:")
            selected_tools = tool_selection.get('selected_tools', [])
            print(f"Selected Tools: {selected_tools}")
            
            if tool_selection.get('reasoning'):
                print(f"Reasoning: {json.dumps(tool_selection['reasoning'], indent=2)}")
            
            print(f"Execution Strategy: {tool_selection.get('execution_strategy', 'unknown')}")
            print(f"Confidence: {tool_selection.get('confidence', 'unknown')}")
            
            # Analyze selected servers
            selected_servers = set()
            for tool_id in selected_tools:
                if ':' in tool_id:
                    server_name = tool_id.split(':')[0]
                    selected_servers.add(server_name)
            
            expected_servers = set(scenario['expected_servers'])
            
            if selected_servers.intersection(expected_servers):
                print("✅ Tool selection includes expected servers!")
            else:
                print("⚠️  Tool selection doesn't match expected servers")
                print(f"   Expected servers: {expected_servers}")
                print(f"   Selected servers: {selected_servers}")
            
        except Exception as e:
            print(f"❌ Tool selection test failed: {e}")
        
        print("-" * 40)

async def simulate_full_execution():
    """Simulate a full data agent execution with mock MCP responses"""
    
    print("\n🎯 Simulating Full Data Agent Execution")
    print("=" * 50)
    
    # Mock the MCP HTTP calls to avoid needing actual servers
    class MockDataAgent(DataAgent):
        async def _get_tools_from_mcp_server(self, server_name: str, server_url: str, server_config: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Mock tool discovery"""
            if "demo" in server_name.lower():
                return [
                    {
                        "name": "ask_ai",
                        "description": "Ask AI for information or synthetic data generation",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "mode": {"type": "string", "enum": ["generate", "analyze", "info"]}
                            }
                        }
                    },
                    {
                        "name": "generate_data",
                        "description": "Generate synthetic test data",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "data_type": {"type": "string"},
                                "count": {"type": "number"},
                                "format": {"type": "string"}
                            }
                        }
                    }
                ]
            elif "denodo" in server_name.lower():
                return [
                    {
                        "name": "query_database",
                        "description": "Execute SQL queries against enterprise databases",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "database": {"type": "string"},
                                "limit": {"type": "number"}
                            }
                        }
                    },
                    {
                        "name": "get_schema",
                        "description": "Get database schema information",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "database": {"type": "string"},
                                "table": {"type": "string"}
                            }
                        }
                    }
                ]
            return []
        
        async def _execute_single_mcp_tool(self, tool_id: str, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
            """Mock tool execution"""
            server_name, tool_name = tool_id.split(':', 1)
            
            # Mock responses based on tool type
            if tool_name == "ask_ai":
                return {
                    "success": True,
                    "result": {
                        "response": "This is mock AI-generated data for testing purposes.",
                        "data": [
                            {"id": 1, "name": "Customer A", "value": 100},
                            {"id": 2, "name": "Customer B", "value": 200}
                        ]
                    },
                    "metadata": {"tool": tool_name, "server": server_name}
                }
            elif tool_name == "query_database":
                return {
                    "success": True,
                    "result": {
                        "rows": [
                            {"customer_id": 1, "sales": 15000, "quarter": "Q4"},
                            {"customer_id": 2, "sales": 22000, "quarter": "Q4"}
                        ],
                        "row_count": 2
                    },
                    "metadata": {"tool": tool_name, "server": server_name, "query": "SELECT * FROM sales"}
                }
            elif tool_name == "generate_data":
                return {
                    "success": True,
                    "result": {
                        "generated_data": [
                            {"id": i, "name": f"Test User {i}", "email": f"user{i}@test.com"}
                            for i in range(1, 6)
                        ],
                        "count": 5
                    },
                    "metadata": {"tool": tool_name, "server": server_name}
                }
            else:
                return {
                    "success": False,
                    "error": f"Mock tool {tool_name} not implemented"
                }
    
    # Test with mock agent
    mock_agent = MockDataAgent()
    
    test_task = "Generate sample customer data and retrieve actual sales information"
    test_context = {
        "query": "I need both synthetic customer data for testing and real sales data for analysis",
        "user_email": "analyst@company.com",
        "metadata_results": {
            "identified_tables": ["customer_sales"],
            "data_sources": ["sales_db"]
        },
        "entitlement_results": {
            "access_granted": True,
            "allowed_tables": ["customer_sales"]
        }
    }
    
    try:
        # Execute the full logic
        session_id = "test_session_mock"
        result = await mock_agent.execute(session_id, test_task, test_context)
        
        print(f"✅ Mock execution completed!")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Execution time: {result.get('execution_time_ms', 0)}ms")
        
        # Show results summary
        execution_results = result.get('results', {})
        if execution_results:
            print(f"\nResults Summary:")
            print(f"Tools selected: {len(execution_results.get('tool_results', []))}")
            print(f"Successful executions: {execution_results.get('successful_tools', 0)}")
            print(f"Failed executions: {execution_results.get('failed_tools', 0)}")
            
            # Show sample tool results
            tool_results = execution_results.get('tool_results', [])
            for i, tool_result in enumerate(tool_results[:2]):  # Show first 2
                print(f"\nTool {i+1} Result:")
                print(f"  Tool ID: {tool_result.get('tool_id', 'unknown')}")
                print(f"  Success: {tool_result.get('success', False)}")
                if tool_result.get('result'):
                    result_data = tool_result['result']
                    if isinstance(result_data, dict):
                        print(f"  Data keys: {list(result_data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock execution failed: {e}")
        return False

async def run_all_data_agent_tests():
    """Run all data agent tests"""
    
    print("🧪 LLM-Based Data Agent Test Suite")
    print("=" * 50)
    print(f"Testing Directory: {os.getcwd()}")
    print()
    
    tests = [
        ("MCP Config Loading", test_mcp_config_loading),
        ("Tool Discovery", test_tool_discovery),
        ("Tool Selection", test_tool_selection),
        ("Full Execution Simulation", simulate_full_execution)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running: {test_name}")
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All data agent tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check MCP server configuration.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_data_agent_tests())
    sys.exit(0 if success else 1) 