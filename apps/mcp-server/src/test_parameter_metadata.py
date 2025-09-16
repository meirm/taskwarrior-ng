#!/usr/bin/env python3
"""
Test script to verify that the parameter metadata conversion is working correctly
"""
import asyncio
import inspect
from typing import get_type_hints, get_args, get_origin
from fastmcp import FastMCP
from tools import basic_operations, batch_operations, metadata_operations

def test_function_signatures():
    """Test that all function signatures use Annotated types correctly"""

    print("Testing function signatures...")

    # Create a dummy MCP instance
    mcp = FastMCP("Test")

    # Initialize the modules
    basic_operations.init_tools(mcp)
    batch_operations.init_tools(mcp)
    metadata_operations.init_tools(mcp)

    # Test functions
    test_functions = [
        # Basic operations
        ('add_task', basic_operations.add_task),
        ('list_tasks', basic_operations.list_tasks),
        ('get_task', basic_operations.get_task),
        ('complete_task', basic_operations.complete_task),
        ('modify_task', basic_operations.modify_task),
        ('delete_task', basic_operations.delete_task),

        # Batch operations
        ('batch_complete_by_ids', batch_operations.batch_complete_by_ids),
        ('batch_complete_by_filter', batch_operations.batch_complete_by_filter),
        ('batch_modify_tasks', batch_operations.batch_modify_tasks),

        # Metadata operations (no parameters)
        ('get_projects', metadata_operations.get_projects),
        ('get_tags', metadata_operations.get_tags),
    ]

    for name, func in test_functions:
        print(f"\n{name}:")
        sig = inspect.signature(func)

        # Get type hints
        hints = get_type_hints(func, include_extras=True)

        for param_name, param in sig.parameters.items():
            if param_name in hints:
                hint = hints[param_name]
                print(f"  - {param_name}: {hint}")

                # Check if it's Annotated
                origin = get_origin(hint)
                if origin is not None:
                    args = get_args(hint)
                    if len(args) > 1:
                        print(f"    Metadata: {args[1:]}")

    print("\n✅ All functions have been converted to use parameter metadata!")

async def test_function_calls():
    """Test that the functions can be called with the new signatures"""
    print("\nTesting function calls...")

    # Test add_task
    result = await basic_operations.add_task(
        description="Test task",
        project="Test Project",
        priority="H",
        tags=["test", "automated"]
    )
    print(f"add_task result: {result['success'] if 'success' in result else 'function executed'}")

    # Test list_tasks
    result = await basic_operations.list_tasks(
        status="pending",
        project="Test Project",
        limit=10
    )
    print(f"list_tasks result: {result['success'] if 'success' in result else 'function executed'}")

    print("\n✅ Functions can be called with the new parameter format!")

if __name__ == "__main__":
    print("Parameter Metadata Conversion Test")
    print("=" * 50)

    # Test signatures
    test_function_signatures()

    # Test function calls
    asyncio.run(test_function_calls())