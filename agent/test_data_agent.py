#!/usr/bin/env python3
"""
Test script for LLM-based Data Agent tool selection

Demonstrates how the Data Agent uses LLM to intelligently select which MCP tools to call
based on different types of queries. Tools are discovered dynamically from MCP servers.
"""

import asyncio
import json
import os
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
                    }
                ]
            elif "denodo" in server_name.lower():
                return [
                    {
                        "name": "denodo_query",
                        "description": "Query enterprise data warehouse through Denodo",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "mode": {"type": "string", "enum": ["data", "metadata"]}
                            }
                        }
                    }
                ]
            return []
        
        async def _execute_single_mcp_tool(self, tool_id: str, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
            """Mock tool execution"""
            if "demo" in tool_id and "ask_ai" in tool_id:
                return {
                    "tool": tool_id,
                    "status": "success",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "synthetic_data": [
                                        {"customer_id": "TEST001", "sales": 12500, "quarter": "Q4"},
                                        {"customer_id": "TEST002", "sales": 18500, "quarter": "Q4"}
                                    ],
                                    "note": "This is synthetic test data generated by AI"
                                })
                            }
                        ]
                    },
                    "server": "demoAgent",
                    "tool_name": "ask_ai"
                }
            elif "denodo" in tool_id and "query" in tool_id:
                return {
                    "tool": tool_id,
                    "status": "success",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "data": [
                                        {"customer_id": "C001", "sales": 15000, "quarter": "Q4"},
                                        {"customer_id": "C002", "sales": 22000, "quarter": "Q4"}
                                    ],
                                    "row_count": 2,
                                    "source": "enterprise_warehouse"
                                })
                            }
                        ]
                    },
                    "server": "denodoAgent", 
                    "tool_name": "denodo_query"
                }
            else:
                return {
                    "tool": tool_id,
                    "status": "error",
                    "error": f"Mock tool {tool_id} not implemented"
                }
    
    mock_agent = MockDataAgent()
    
    test_task = "Analyze customer sales performance for Q4 with examples"
    test_context = {
        "query": "Show me customer sales analysis with both real and synthetic examples",
        "user_email": "analyst@company.com",
        "metadata_results": {
            "identified_tables": ["customer_sales"],
            "data_sources": ["sales_warehouse"]
        }
    }
    
    print(f"Task: {test_task}")
    print(f"Context: {json.dumps(test_context, indent=2)}")
    
    try:
        # Execute the full logic
        result = await mock_agent._execute_logic(test_task, test_context)
        
        print(f"\n📊 Full Execution Result:")
        
        # Tool discovery summary
        discovery = result.get('tool_discovery', {})
        print(f"Discovered Tools: {discovery.get('discovered_tools', 0)}")
        print(f"Available Servers: {discovery.get('available_servers', [])}")
        
        # Tool selection summary
        selection = result.get('tool_selection_reasoning', {})
        print(f"Selected Tools: {selection.get('selected_tools', [])}")
        
        # Execution summary
        executions = result.get('tool_executions', [])
        print(f"Tools Executed: {len(executions)}")
        
        print(f"\n📈 Tool Execution Details:")
        for execution in executions:
            tool_id = execution.get('tool', 'unknown')
            status = execution.get('status', 'unknown')
            server = execution.get('server', 'unknown')
            print(f"  - {tool_id} ({server}): {status}")
            
            if status == "success":
                result_data = execution.get('result', {})
                if 'content' in result_data and result_data['content']:
                    try:
                        content_text = result_data['content'][0].get('text', '')
                        parsed_content = json.loads(content_text)
                        if 'data' in parsed_content:
                            print(f"    Retrieved {len(parsed_content['data'])} records")
                        elif 'synthetic_data' in parsed_content:
                            print(f"    Generated {len(parsed_content['synthetic_data'])} synthetic records")
                    except (json.JSONDecodeError, KeyError, IndexError):
                        print(f"    Result format: {type(result_data)}")
        
        # Analysis summary
        analysis = result.get('final_analysis', {})
        if analysis and 'summary' in analysis:
            print(f"\n📝 Analysis Summary:")
            print(f"  {analysis['summary']}")
        
        # Data quality summary
        data_summary = result.get('data_summary', {})
        print(f"\n📊 Data Summary:")
        print(f"  Quality: {data_summary.get('data_quality', 'unknown')}")
        print(f"  Tools Available: {data_summary.get('total_tools_available', 0)}")
        print(f"  Tools Selected: {data_summary.get('tools_selected', 0)}")
        print(f"  Tools Executed: {data_summary.get('tools_executed', 0)}")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    
    print("🚀 Data Agent MCP-Based Tool Selection Test Suite")
    print("=" * 60)
    
    # Run tests in sequence
    config_loaded = await test_mcp_config_loading()
    
    if config_loaded:
        tools_discovered = await test_tool_discovery()
        
        if tools_discovered:
            await test_tool_selection()
        else:
            print("\n⚠️  Skipping tool selection tests - tool discovery failed")
    else:
        print("\n⚠️  Skipping further tests - MCP config not loaded")
    
    # Always run simulation with mocks
    await simulate_full_execution()
    
    print(f"\n✅ Test suite completed!")
    print("\nNext Steps:")
    print("1. Ensure MCP servers are configured in mcp_config.json")
    print("2. Start the actual MCP servers (Demo and Denodo)")
    print("3. Test with real MCP server connections")
    print("4. Monitor LLM tool selection decisions in production")

if __name__ == "__main__":
    asyncio.run(main()) 