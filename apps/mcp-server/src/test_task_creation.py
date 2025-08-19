#!/usr/bin/env python3
"""
Test script to verify task creation with all data fields
"""
import asyncio
import json
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import the server
sys.path.insert(0, os.path.dirname(__file__))

from taskwarrior_mcp_server import tw, task_to_dict, AddTaskParams, ListTasksParams, TaskIdParam
from tasklib import Task

async def test_task_creation():
    """Test creating a task with all possible data and verify it's saved correctly"""
    
    print("🧪 Testing Task Creation with All Data Fields...")
    
    # Create a comprehensive task with all possible fields
    due_date = (datetime.now() + timedelta(days=7)).isoformat()
    
    task_data = AddTaskParams(
        description="Complete project documentation with detailed API references",
        project="Documentation",
        priority="H",  # High priority
        tags=["urgent", "documentation", "api", "review"],
        due=due_date
    )
    
    print(f"\n📝 Creating task with data:")
    print(f"   Description: {task_data.description}")
    print(f"   Project: {task_data.project}")
    print(f"   Priority: {task_data.priority}")
    print(f"   Tags: {task_data.tags}")
    print(f"   Due: {task_data.due}")
    
    # Add the task directly using TaskWarrior
    try:
        # Create the task using tasklib directly
        task = Task(tw, description=task_data.description)
        
        # Set all the fields
        if task_data.project:
            task['project'] = task_data.project
        if task_data.priority:
            task['priority'] = task_data.priority
        if task_data.tags:
            task['tags'] = set(task_data.tags)
        if task_data.due:
            task['due'] = datetime.fromisoformat(task_data.due.replace('Z', '+00:00'))
        
        # Save the task
        task.save()
        
        task_id = task['id']
        print(f"\n✅ Task created successfully with ID: {task_id}")
        
        # Verify the task was created with all data
        print(f"\n🔍 Verifying saved task data...")
        
        # Retrieve the task
        saved_task_obj = tw.tasks.get(id=task_id)
        saved_task = task_to_dict(saved_task_obj)
        
        # Check all fields
        verification_results = []
        
        # Description
        if saved_task['description'] == task_data.description:
            verification_results.append("✅ Description saved correctly")
        else:
            verification_results.append(f"❌ Description mismatch: expected '{task_data.description}', got '{saved_task['description']}'")
        
        # Project
        if saved_task['project'] == task_data.project:
            verification_results.append("✅ Project saved correctly")
        else:
            verification_results.append(f"❌ Project mismatch: expected '{task_data.project}', got '{saved_task['project']}'")
        
        # Priority
        if saved_task['priority'] == task_data.priority:
            verification_results.append("✅ Priority saved correctly")
        else:
            verification_results.append(f"❌ Priority mismatch: expected '{task_data.priority}', got '{saved_task['priority']}'")
        
        # Tags
        saved_tags = set(saved_task['tags'])
        expected_tags = set(task_data.tags)
        if saved_tags == expected_tags:
            verification_results.append("✅ Tags saved correctly")
        else:
            verification_results.append(f"❌ Tags mismatch: expected {expected_tags}, got {saved_tags}")
        
        # Due date (compare just the date part since time zones might differ)
        if saved_task['due']:
            try:
                saved_due = datetime.fromisoformat(saved_task['due'].replace('Z', '+00:00'))
                expected_due = datetime.fromisoformat(task_data.due.replace('Z', '+00:00'))
                # Compare dates with some tolerance for minutes (Taskwarrior might round)
                if abs((saved_due - expected_due).total_seconds()) < 300:
                    verification_results.append("✅ Due date saved correctly")
                else:
                    verification_results.append(f"❌ Due date mismatch: expected '{task_data.due}', got '{saved_task['due']}'")
            except Exception as e:
                verification_results.append(f"❌ Due date comparison failed: {e}")
        else:
            verification_results.append("❌ Due date not saved")
        
        # Additional fields that should be present
        required_fields = ['id', 'uuid', 'status', 'urgency', 'entry']
        for field in required_fields:
            if field in saved_task and saved_task[field] is not None:
                verification_results.append(f"✅ {field.capitalize()} field present")
            else:
                verification_results.append(f"❌ {field.capitalize()} field missing")
        
        # Print verification results
        print("\n📊 Verification Results:")
        for result in verification_results:
            print(f"   {result}")
        
        # Print full task details for manual inspection
        print(f"\n📋 Complete Task Details:")
        print(json.dumps(saved_task, indent=2))
        
        # Check if all verifications passed
        failed_checks = [r for r in verification_results if r.startswith("❌")]
        if not failed_checks:
            print(f"\n🎉 All data fields saved correctly!")
            return True
        else:
            print(f"\n⚠️  {len(failed_checks)} verification(s) failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_task_retrieval_methods():
    """Test different ways to retrieve the created task"""
    
    print(f"\n🔍 Testing Task Retrieval Methods...")
    
    # Test listing tasks by project
    try:
        project_tasks = tw.tasks.filter(project="Documentation")
        project_count = len(project_tasks)
        if project_count > 0:
            print(f"✅ Found {project_count} task(s) in 'Documentation' project")
        else:
            print("❌ Failed to find tasks by project")
    except Exception as e:
        print(f"❌ Project search failed: {e}")
    
    # Test listing tasks by tags
    try:
        all_tasks = tw.tasks.pending()
        tag_tasks = []
        for t in all_tasks:
            try:
                task_tags = t['tags']
                if task_tags and 'urgent' in task_tags:
                    tag_tasks.append(t)
            except KeyError:
                continue  # Task has no tags
        
        if len(tag_tasks) > 0:
            print(f"✅ Found {len(tag_tasks)} task(s) with 'urgent' tag")
        else:
            print("❌ Failed to find tasks by tag")
    except Exception as e:
        print(f"❌ Tag search failed: {e}")
    
    # Test listing pending tasks
    try:
        pending_tasks = tw.tasks.pending()
        print(f"✅ Found {len(pending_tasks)} pending task(s)")
    except Exception as e:
        print(f"❌ Pending tasks search failed: {e}")

if __name__ == "__main__":
    async def main():
        success = await test_task_creation()
        test_task_retrieval_methods()
        return success
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)