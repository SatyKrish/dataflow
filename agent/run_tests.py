#!/usr/bin/env python3
"""
Test Runner Launcher for DataFlow Agents

Simple script to run tests from the main agent directory.
Delegates to the comprehensive test runner in the test/ directory.
"""

import sys
import os
import subprocess

def main():
    """Launch the test runner from the test directory"""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_runner_path = os.path.join(script_dir, "test", "test_runner.py")
    
    # Check if test runner exists
    if not os.path.exists(test_runner_path):
        print("❌ Test runner not found at:", test_runner_path)
        return 1
    
    # Pass all arguments to the test runner
    try:
        result = subprocess.run([sys.executable, test_runner_path] + sys.argv[1:])
        return result.returncode
    except Exception as e:
        print(f"❌ Failed to run test runner: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 