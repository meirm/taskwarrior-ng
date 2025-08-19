#!/usr/bin/env python3
"""
Debug script to see how TaskWarrior stores task data
"""
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to the path so we can import the server
sys.path.insert(0, os.path.dirname(__file__))

from taskwarrior_mcp_server import tw
from tasklib import Task

def debug_task_creation():
    """Debug task creation to see actual data structure"""
    
    print("🔍 Debugging Task Creation...")
    
    # Create a simple task first
    task = Task(tw, description="Test task for debugging")
    task['project'] = "TestProject"
    task['priority'] = "H"
    task['tags'] = {"test", "debug"}
    task['due'] = datetime.now() + timedelta(days=1)
    
    print(f"Before save:")
    print(f"  Description: {task['description'] if 'description' in task else 'NOT SET'}")
    print(f"  Project: {task['project'] if 'project' in task else 'NOT SET'}")
    print(f"  Priority: {task['priority'] if 'priority' in task else 'NOT SET'}")
    print(f"  Tags: {task['tags'] if 'tags' in task else 'NOT SET'}")
    print(f"  Due: {task['due'] if 'due' in task else 'NOT SET'}")
    
    # Save the task
    task.save()
    task_id = task['id']
    
    print(f"\nAfter save (ID: {task_id}):")
    print(f"  Description: {task['description'] if 'description' in task else 'NOT SET'}")
    print(f"  Project: {task['project'] if 'project' in task else 'NOT SET'}")
    print(f"  Priority: {task['priority'] if 'priority' in task else 'NOT SET'}")
    print(f"  Tags: {task['tags'] if 'tags' in task else 'NOT SET'}")
    print(f"  Due: {task['due'] if 'due' in task else 'NOT SET'}")
    print(f"  ID: {task['id'] if 'id' in task else 'NOT SET'}")
    print(f"  UUID: {task['uuid'] if 'uuid' in task else 'NOT SET'}")
    
    # Try to retrieve it again
    print(f"\nRetrieving task {task_id} from TaskWarrior:")
    retrieved_task = tw.tasks.get(id=task_id)
    
    print(f"Retrieved task type: {type(retrieved_task)}")
    print(f"Retrieved task dir: {[attr for attr in dir(retrieved_task) if not attr.startswith('_')]}")
    
    print(f"Retrieved data:")
    print(f"  Description: {retrieved_task['description'] if 'description' in retrieved_task else 'NOT SET'}")
    print(f"  Project: {retrieved_task['project'] if 'project' in retrieved_task else 'NOT SET'}")
    print(f"  Priority: {retrieved_task['priority'] if 'priority' in retrieved_task else 'NOT SET'}")
    print(f"  Tags: {retrieved_task['tags'] if 'tags' in retrieved_task else 'NOT SET'}")
    print(f"  Due: {retrieved_task['due'] if 'due' in retrieved_task else 'NOT SET'}")
    print(f"  ID: {retrieved_task['id'] if 'id' in retrieved_task else 'NOT SET'}")
    print(f"  UUID: {retrieved_task['uuid'] if 'uuid' in retrieved_task else 'NOT SET'}")
    
    # Try accessing with direct indexing
    print(f"\nDirect indexing:")
    try:
        print(f"  Description: {retrieved_task['description']}")
    except Exception as e:
        print(f"  Description error: {e}")
    
    try:
        print(f"  Project: {retrieved_task['project']}")
    except Exception as e:
        print(f"  Project error: {e}")
    
    try:
        print(f"  Priority: {retrieved_task['priority']}")
    except Exception as e:
        print(f"  Priority error: {e}")
    
    try:
        print(f"  Tags: {retrieved_task['tags']}")
    except Exception as e:
        print(f"  Tags error: {e}")
        
    # Try to see all available data
    print(f"\nAll task data (as dict):")
    try:
        task_data = dict(retrieved_task)
        for key, value in task_data.items():
            print(f"  {key}: {value} (type: {type(value)})")
    except Exception as e:
        print(f"  Error converting to dict: {e}")

if __name__ == "__main__":
    debug_task_creation()