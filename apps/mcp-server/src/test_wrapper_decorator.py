#!/usr/bin/env python3
"""
Test the JSON compatibility wrapper decorator directly.
This shows how the wrapper transforms JSON to Pydantic models.
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.models import AddTaskParams, ListTasksParams
from utils.fastmcp_wrapper import convert_json_to_pydantic

async def test_wrapper_decorator():
    """Test the wrapper decorator functionality"""
    print("Testing Wrapper Decorator Conversion...\n")

    # Create a test function that expects a Pydantic model
    async def mock_add_task(params: AddTaskParams):
        """Mock function that expects AddTaskParams"""
        return {
            "success": True,
            "description": params.description,
            "project": params.project,
            "priority": params.priority,
            "tags": params.tags
        }

    # Wrap the function with our converter
    wrapped_func = convert_json_to_pydantic(mock_add_task)

    # Test 1: Call with JSON dictionary
    print("Test 1: Calling with JSON dictionary")
    json_input = {
        "description": "Test task",
        "project": "TestProject",
        "priority": "H",
        "tags": ["test", "json"]
    }

    result = await wrapped_func(json_input)
    print(f"✅ Result: {result}")

    # Test 2: Call with MCP wrapper format
    print("\nTest 2: Calling with MCP wrapper format")
    mcp_wrapped = {
        "arguments": {
            "description": "MCP wrapped task",
            "project": "TestProject",
            "priority": "M"
        }
    }

    result = await wrapped_func(mcp_wrapped)
    print(f"✅ Result: {result}")

    # Test 3: Call with Pydantic model
    print("\nTest 3: Calling with Pydantic model")
    pydantic_input = AddTaskParams(
        description="Pydantic task",
        project="TestProject",
        priority="L"
    )

    result = await wrapped_func(pydantic_input)
    print(f"✅ Result: {result}")

    # Test 4: Test with extra fields (should be filtered)
    print("\nTest 4: Calling with extra fields")
    json_with_extras = {
        "description": "Task with extras",
        "project": "TestProject",
        "priority": "H",
        "extra_field": "should be ignored",
        "another_extra": 123
    }

    result = await wrapped_func(json_with_extras)
    print(f"✅ Result (extras filtered): {result}")

    print("\n✨ All wrapper tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_wrapper_decorator())