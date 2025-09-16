#!/usr/bin/env python3
"""
Test script to verify JSON compatibility in the MCP server.
This simulates what Claude sends as an MCP client.
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.models import AddTaskParams, ListTasksParams, TaskIdParam
from tools.basic_operations import add_task, list_tasks, get_task

async def test_json_compatibility():
    """Test that the server handles both JSON and Pydantic models"""
    print("Testing MCP Server JSON Compatibility...\n")

    task_id = None  # Initialize task_id

    # Test 1: Add task with JSON (simulating Claude MCP client)
    print("Test 1: Adding task with JSON input - Converting manually")
    json_input = {
        "description": "Test task from JSON",
        "project": "TestProject",
        "priority": "H",
        "tags": ["test", "json"]
    }

    try:
        # Since we're testing direct calls, convert JSON to Pydantic manually
        # (the wrapper would do this automatically when called through MCP)
        from utils.models import AddTaskParams
        pydantic_model = AddTaskParams(**json_input)
        result = await add_task(pydantic_model)
        print(f"✅ Add task (JSON->Pydantic): {result['success']}")
        if result.get('task'):
            task_id = result['task']['id']
            print(f"   Created task ID: {task_id}")
    except Exception as e:
        print(f"❌ Add task (JSON->Pydantic) failed: {e}")

    # Test 2: Add task with MCP wrapper format
    print("\nTest 2: Adding task with MCP wrapper format")
    mcp_wrapped_input = {
        "arguments": {
            "description": "Test task from MCP wrapper",
            "project": "TestProject",
            "priority": "M"
        }
    }

    try:
        result = await add_task(mcp_wrapped_input)
        print(f"✅ Add task (MCP wrapper): {result['success']}")
    except Exception as e:
        print(f"❌ Add task (MCP wrapper) failed: {e}")

    # Test 3: Add task with Pydantic model (original format)
    print("\nTest 3: Adding task with Pydantic model")
    pydantic_input = AddTaskParams(
        description="Test task from Pydantic",
        project="TestProject",
        priority="L"
    )

    try:
        result = await add_task(pydantic_input)
        print(f"✅ Add task (Pydantic): {result['success']}")
    except Exception as e:
        print(f"❌ Add task (Pydantic) failed: {e}")

    # Test 4: List tasks with JSON
    print("\nTest 4: Listing tasks with JSON input")
    list_json = {"status": "pending", "project": "TestProject"}

    try:
        result = await list_tasks(list_json)
        print(f"✅ List tasks (JSON): {result['success']}")
        print(f"   Found {result.get('count', 0)} tasks")
    except Exception as e:
        print(f"❌ List tasks (JSON) failed: {e}")

    # Test 5: List tasks with no parameters (should default to pending)
    print("\nTest 5: Listing tasks with no parameters")

    try:
        result = await list_tasks(None)
        print(f"✅ List tasks (None): {result['success']}")
        print(f"   Found {result.get('count', 0)} pending tasks")
    except Exception as e:
        print(f"❌ List tasks (None) failed: {e}")

    # Test 6: Get task with JSON
    if task_id:
        print(f"\nTest 6: Getting task {task_id} with JSON input")
        get_json = {"task_id": task_id}

        try:
            result = await get_task(get_json)
            print(f"✅ Get task (JSON): {result['success']}")
            if result.get('task'):
                print(f"   Task description: {result['task']['description']}")
        except Exception as e:
            print(f"❌ Get task (JSON) failed: {e}")

    print("\n✨ All tests completed!")

if __name__ == "__main__":
    # Initialize the tools (this would normally be done by the server)
    from fastmcp import FastMCP
    from utils.fastmcp_wrapper import make_mcp_json_compatible

    mcp_base = FastMCP("Test Server")
    mcp = make_mcp_json_compatible(mcp_base)

    # Import and initialize tools
    from tools import basic_operations
    basic_operations.init_tools(mcp)

    # Run the tests
    asyncio.run(test_json_compatibility())