#!/usr/bin/env python3
"""
Test script to verify the MCP tools work correctly by simulating MCP calls
"""
import asyncio
import json
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import the server
sys.path.insert(0, os.path.dirname(__file__))

# Import the tool functions directly (the actual functions, not the decorated ones)
import taskwarrior_mcp_server
from taskwarrior_mcp_server import AddTaskParams, ListTasksParams, TaskIdParam, ModifyTaskParams

async def test_mcp_add_task():
    """Test adding a task through the MCP interface"""
    
    print("🧪 Testing MCP Tool: add_task")
    
    # Create task data
    due_date = (datetime.now() + timedelta(days=3)).isoformat()
    task_params = AddTaskParams(
        description="Test MCP task creation with all fields",
        project="MCPTest",
        priority="M",
        tags=["mcp", "test", "automation"],
        due=due_date
    )
    
    # Call the actual function that the MCP tool would call
    result = await taskwarrior_mcp_server.add_task(task_params)
    
    if result['success']:
        task_id = result['task']['id']
        print(f"✅ Task created successfully with ID: {task_id}")
        print(f"   Description: {result['task']['description']}")
        print(f"   Project: {result['task']['project']}")
        print(f"   Priority: {result['task']['priority']}")
        print(f"   Tags: {result['task']['tags']}")
        print(f"   Due: {result['task']['due']}")
        return task_id
    else:
        print(f"❌ Task creation failed: {result.get('error', 'Unknown error')}")
        return None

async def test_mcp_list_tasks():
    """Test listing tasks through MCP interface"""
    
    print(f"\n🧪 Testing MCP Tool: list_tasks")
    
    # Test different filtering options
    test_cases = [
        ("All pending tasks", ListTasksParams(status="pending", limit=5)),
        ("MCPTest project", ListTasksParams(status="pending", project="MCPTest")),
        ("Tasks with 'mcp' tag", ListTasksParams(status="pending", tags=["mcp"])),
    ]
    
    for description, params in test_cases:
        result = await taskwarrior_mcp_server.list_tasks(params)
        
        if result['success']:
            print(f"✅ {description}: Found {result['count']} task(s)")
            for task in result['tasks'][:2]:  # Show first 2 tasks
                print(f"   - [{task['id']}] {task['description'][:50]}...")
        else:
            print(f"❌ {description} failed: {result.get('error', 'Unknown error')}")

async def test_mcp_get_task(task_id):
    """Test getting a specific task"""
    
    if not task_id:
        print(f"\n⏭️  Skipping get_task test (no task ID)")
        return
        
    print(f"\n🧪 Testing MCP Tool: get_task (ID: {task_id})")
    
    params = TaskIdParam(task_id=task_id)
    result = await taskwarrior_mcp_server.get_task(params)
    
    if result['success']:
        task = result['task']
        print(f"✅ Task retrieved successfully:")
        print(f"   ID: {task['id']}")
        print(f"   Description: {task['description']}")
        print(f"   Project: {task['project']}")
        print(f"   Status: {task['status']}")
        print(f"   Tags: {task['tags']}")
    else:
        print(f"❌ Get task failed: {result.get('error', 'Unknown error')}")

async def test_mcp_modify_task(task_id):
    """Test modifying a task"""
    
    if not task_id:
        print(f"\n⏭️  Skipping modify_task test (no task ID)")
        return
        
    print(f"\n🧪 Testing MCP Tool: modify_task (ID: {task_id})")
    
    params = ModifyTaskParams(
        task_id=task_id,
        description="Modified: Test MCP task creation with all fields [UPDATED]",
        priority="L",
        tags=["mcp", "test", "automation", "modified"]
    )
    
    result = await taskwarrior_mcp_server.modify_task(params)
    
    if result['success']:
        task = result['task']
        print(f"✅ Task modified successfully:")
        print(f"   Description: {task['description']}")
        print(f"   Priority: {task['priority']}")
        print(f"   Tags: {task['tags']}")
    else:
        print(f"❌ Modify task failed: {result.get('error', 'Unknown error')}")

async def test_mcp_get_summary():
    """Test getting task summary"""
    
    print(f"\n🧪 Testing MCP Tool: get_summary")
    
    result = await taskwarrior_mcp_server.get_summary()
    
    if result['success']:
        summary = result['summary']
        print(f"✅ Summary retrieved successfully:")
        print(f"   Pending: {summary['status']['pending']}")
        print(f"   Completed: {summary['status']['completed']}")
        print(f"   Total: {summary['status']['total']}")
        print(f"   Overdue: {summary['overdue']}")
        print(f"   High Priority: {summary['priority']['H']}")
        print(f"   Medium Priority: {summary['priority']['M']}")
        print(f"   Low Priority: {summary['priority']['L']}")
    else:
        print(f"❌ Get summary failed: {result.get('error', 'Unknown error')}")

async def test_mcp_get_projects():
    """Test getting all projects"""
    
    print(f"\n🧪 Testing MCP Tool: get_projects")
    
    result = await taskwarrior_mcp_server.get_projects()
    
    if result['success']:
        print(f"✅ Projects retrieved successfully:")
        print(f"   Count: {result['count']}")
        print(f"   Projects: {result['projects']}")
    else:
        print(f"❌ Get projects failed: {result.get('error', 'Unknown error')}")

async def test_mcp_get_tags():
    """Test getting all tags"""
    
    print(f"\n🧪 Testing MCP Tool: get_tags")
    
    result = await taskwarrior_mcp_server.get_tags()
    
    if result['success']:
        print(f"✅ Tags retrieved successfully:")
        print(f"   Count: {result['count']}")
        print(f"   Tags: {result['tags']}")
    else:
        print(f"❌ Get tags failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    async def main():
        print("🚀 Testing All MCP Tools\n")
        
        # Test adding a task
        task_id = await test_mcp_add_task()
        
        # Test listing tasks
        await test_mcp_list_tasks()
        
        # Test getting specific task
        await test_mcp_get_task(task_id)
        
        # Test modifying task
        await test_mcp_modify_task(task_id)
        
        # Test summary functions
        await test_mcp_get_summary()
        await test_mcp_get_projects()
        await test_mcp_get_tags()
        
        print(f"\n🎉 All MCP tool tests completed!")
        
        return True
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)