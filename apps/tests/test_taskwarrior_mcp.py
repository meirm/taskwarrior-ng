#!/usr/bin/env python3
"""
Test client for Taskwarrior MCP Server

This script demonstrates how to interact with the Taskwarrior MCP server
and can be used to test functionality before integrating with AI assistants.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

class TaskwarriorMCPTest:
    """Test client for the Taskwarrior MCP server"""
    
    def __init__(self, server_script: str = "taskwarrior_mcp_server.py"):
        self.server_script = server_script
    
    async def test_add_task(self):
        """Test adding a new task"""
        print("\n=== Testing: Add Task ===")
        
        # Test basic task
        result = await self.call_tool("add_task", {
            "description": "Test task from MCP client",
            "project": "testing",
            "priority": "H",
            "tags": ["mcp", "test"]
        })
        print("Basic task creation:", json.dumps(result, indent=2))
        
        # Test task with due date
        result = await self.call_tool("add_task", {
            "description": "Task with due date",
            "due": "2024-12-31T23:59:59"
        })
        print("Task with due date:", json.dumps(result, indent=2))
    
    async def test_list_tasks(self):
        """Test listing tasks"""
        print("\n=== Testing: List Tasks ===")
        
        # List all pending tasks
        result = await self.call_tool("list_tasks", {"status": "pending"})
        print("Pending tasks:", json.dumps(result, indent=2))
        
        # List tasks in testing project
        result = await self.call_tool("list_tasks", {
            "project": "testing",
            "limit": 10
        })
        print("Testing project tasks:", json.dumps(result, indent=2))
    
    async def test_task_operations(self):
        """Test various task operations"""
        print("\n=== Testing: Task Operations ===")
        
        # First, get a task to work with
        tasks = await self.call_tool("list_tasks", {"limit": 1})
        if tasks.get("success") and tasks.get("tasks"):
            task_id = tasks["tasks"][0]["id"]
            print(f"Working with task ID: {task_id}")
            
            # Test getting task details
            result = await self.call_tool("get_task", {"task_id": task_id})
            print("Task details:", json.dumps(result, indent=2))
            
            # Test modifying task
            result = await self.call_tool("modify_task", {
                "task_id": task_id,
                "priority": "M",
                "tags": ["modified", "test"]
            })
            print("Modified task:", json.dumps(result, indent=2))
            
            # Test starting task
            result = await self.call_tool("start_task", {"task_id": task_id})
            print("Started task:", json.dumps(result, indent=2))
            
            # Test stopping task
            result = await self.call_tool("stop_task", {"task_id": task_id})
            print("Stopped task:", json.dumps(result, indent=2))
            
        else:
            print("No tasks available for operations test")
    
    async def test_projects_and_tags(self):
        """Test getting projects and tags"""
        print("\n=== Testing: Projects and Tags ===")
        
        result = await self.call_tool("get_projects", {})
        print("Projects:", json.dumps(result, indent=2))
        
        result = await self.call_tool("get_tags", {})
        print("Tags:", json.dumps(result, indent=2))
    
    async def test_summary(self):
        """Test getting task summary"""
        print("\n=== Testing: Summary ===")
        
        result = await self.call_tool("get_summary", {})
        print("Summary:", json.dumps(result, indent=2))
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            # Create the MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # For this test, we'll import and call the server directly
            # In a real MCP setup, this would go through the protocol
            
            # Import the server module
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server', 'src'))
            from taskwarrior_mcp_server import tw_mcp
            
            # Call the appropriate method
            if tool_name == "add_task":
                result = await tw_mcp.add_task(**arguments)
            elif tool_name == "list_tasks":
                result = await tw_mcp.list_tasks(**arguments)
            elif tool_name == "get_task":
                result = await tw_mcp.get_task(**arguments)
            elif tool_name == "complete_task":
                result = await tw_mcp.complete_task(**arguments)
            elif tool_name == "modify_task":
                task_id = arguments.pop('task_id')
                result = await tw_mcp.modify_task(task_id, **arguments)
            elif tool_name == "delete_task":
                result = await tw_mcp.delete_task(**arguments)
            elif tool_name == "start_task":
                result = await tw_mcp.start_task(**arguments)
            elif tool_name == "stop_task":
                result = await tw_mcp.stop_task(**arguments)
            elif tool_name == "get_projects":
                result = await tw_mcp.get_projects()
            elif tool_name == "get_tags":
                result = await tw_mcp.get_tags()
            elif tool_name == "get_summary":
                result = await tw_mcp.get_summary()
            else:
                result = {"success": False, "error": f"Unknown tool: {tool_name}"}
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error calling {tool_name}: {e}"
            }
    
    async def run_all_tests(self):
        """Run all test functions"""
        print("Starting Taskwarrior MCP Server Tests")
        print("====================================")
        
        try:
            await self.test_add_task()
            await self.test_list_tasks()
            await self.test_task_operations()
            await self.test_projects_and_tags()
            await self.test_summary()
            
            print("\n=== All Tests Completed ===")
            
        except Exception as e:
            print(f"\nTest failed with error: {e}")
            sys.exit(1)

async def main():
    """Main function to run tests"""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python test_taskwarrior_mcp.py")
        print("Tests the Taskwarrior MCP server functionality")
        print("\nMake sure you have:")
        print("1. Taskwarrior installed and configured")
        print("2. tasklib Python library installed")
        print("3. The taskwarrior_mcp_server.py file in the same directory")
        return
    
    # Check if taskwarrior is available
    try:
        subprocess.run(["task", "--version"], capture_output=True, check=True)
        print("✓ Taskwarrior is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Taskwarrior is not available. Please install it first.")
        sys.exit(1)
    
    # Check if tasklib is available
    try:
        import tasklib
        print("✓ tasklib is available")
    except ImportError:
        print("✗ tasklib is not available. Please install it: pip install tasklib")
        sys.exit(1)
    
    # Run the tests
    test_client = TaskwarriorMCPTest()
    await test_client.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
