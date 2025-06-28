#!/usr/bin/env python3
"""
Test Runner for DataFlow Agent Tests

Comprehensive test runner that can execute all agent tests individually or as a suite.
"""

import asyncio
import argparse
import sys
import os
from typing import List, Tuple, Callable, Awaitable

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
import test_azure_openai
import test_server
import test_data_agent

class TestRunner:
    """Test runner for agent system tests"""
    
    def __init__(self):
        self.test_modules = {
            "azure_openai": {
                "module": test_azure_openai,
                "function": test_azure_openai.run_all_tests,
                "description": "Azure OpenAI configuration and connection tests"
            },
            "server": {
                "module": test_server,
                "function": test_server.run_all_server_tests,
                "description": "Server endpoint and API tests"
            },
            "data_agent": {
                "module": test_data_agent,
                "function": test_data_agent.run_all_data_agent_tests,
                "description": "Data agent functionality and tool selection tests"
            }
        }
    
    async def run_single_test(self, test_name: str) -> bool:
        """Run a single test module"""
        
        if test_name not in self.test_modules:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available tests: {', '.join(self.test_modules.keys())}")
            return False
        
        test_info = self.test_modules[test_name]
        print(f"🧪 Running {test_name} tests: {test_info['description']}")
        print("=" * 70)
        
        try:
            result = await test_info["function"]()
            if result:
                print(f"✅ {test_name} tests PASSED")
            else:
                print(f"❌ {test_name} tests FAILED")
            return result
        except Exception as e:
            print(f"❌ {test_name} tests CRASHED: {e}")
            return False
    
    async def run_all_tests(self) -> Tuple[int, int]:
        """Run all test modules"""
        
        print("🧪 DataFlow Agent Test Suite")
        print("=" * 70)
        print("Running comprehensive tests for all agent components")
        print()
        
        results = []
        for test_name, test_info in self.test_modules.items():
            print(f"🔍 Starting {test_name} tests...")
            try:
                result = await test_info["function"]()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: CRASHED - {e}")
                results.append((test_name, False))
            print()
        
        # Summary
        print("📊 Overall Test Results")
        print("=" * 70)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            description = self.test_modules[test_name]["description"]
            print(f"{test_name:15} | {status:10} | {description}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{total} test modules passed")
        
        if passed == total:
            print("🎉 All tests passed! The agent system is working correctly.")
        else:
            print("⚠️ Some tests failed. Please review the output above.")
        
        return passed, total
    
    def list_tests(self):
        """List available tests"""
        
        print("📋 Available Test Modules")
        print("=" * 50)
        
        for test_name, test_info in self.test_modules.items():
            print(f"🧪 {test_name}")
            print(f"   Description: {test_info['description']}")
            print()
    
    async def run_quick_health_check(self) -> bool:
        """Run a quick health check of key components"""
        
        print("⚡ Quick Health Check")
        print("=" * 30)
        
        # Test Azure OpenAI configuration
        try:
            from azure_openai_config import validate_azure_openai_config
            validation = validate_azure_openai_config()
            if validation["is_valid"]:
                print("✅ Azure OpenAI configuration valid")
            else:
                print("⚠️ Azure OpenAI configuration issues detected")
        except Exception as e:
            print(f"❌ Azure OpenAI config check failed: {e}")
        
        # Test server health (if running)
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get("http://localhost:8001/health")
                if response.status_code == 200:
                    print("✅ Server is running and healthy")
                else:
                    print("⚠️ Server responded but may have issues")
        except Exception:
            print("⚠️ Server not running or not accessible")
        
        # Test imports
        try:
            from data_agent import DataAgent
            from metadata_agent import MetadataAgent
            from entitlement_agent import EntitlementAgent
            from aggregation_agent import AggregationAgent
            print("✅ All agent modules can be imported")
        except Exception as e:
            print(f"❌ Agent import failed: {e}")
            return False
        
        print("\n✅ Quick health check completed")
        return True

async def main():
    """Main entry point for test runner"""
    
    parser = argparse.ArgumentParser(
        description="Test runner for DataFlow agent system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                    # Run all tests
  python test_runner.py azure_openai      # Run only Azure OpenAI tests
  python test_runner.py --list            # List available tests
  python test_runner.py --health          # Quick health check
        """
    )
    
    parser.add_argument(
        "test_name", 
        nargs="?", 
        help="Name of specific test to run (optional)"
    )
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="List available tests"
    )
    parser.add_argument(
        "--health", 
        action="store_true", 
        help="Run quick health check"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        runner.list_tests()
        return True
    
    if args.health:
        return await runner.run_quick_health_check()
    
    if args.test_name:
        # Run specific test
        success = await runner.run_single_test(args.test_name)
        return success
    else:
        # Run all tests
        passed, total = await runner.run_all_tests()
        return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner failed: {e}")
        sys.exit(1) 