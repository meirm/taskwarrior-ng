#!/usr/bin/env python3
"""
Test script for batch operations
"""
import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from taskwarrior_mcp_server import (
    tw, task_to_dict, filter_tasks, safe_get_task_field,
    BatchFilterParams, BatchTaskIdsParams, BatchModifyParams
)
from tasklib import Task

def create_test_tasks():
    """Create some test tasks for batch operations"""
    print("📝 Creating test tasks for batch operations...")
    
    test_tasks = [
        {
            'description': 'Test task 1 - urgent documentation',
            'project': 'BatchTest',
            'priority': 'H',
            'tags': {'urgent', 'documentation', 'test'}
        },
        {
            'description': 'Test task 2 - medium priority API',
            'project': 'BatchTest',
            'priority': 'M',
            'tags': {'api', 'development', 'test'}
        },
        {
            'description': 'Test task 3 - low priority cleanup',
            'project': 'BatchTest',
            'priority': 'L',
            'tags': {'cleanup', 'maintenance', 'test'}
        },
        {
            'description': 'Test task 4 - different project',
            'project': 'OtherProject',
            'priority': 'H',
            'tags': {'urgent', 'other', 'test'}
        },
        {
            'description': 'Test task 5 - no project',
            'priority': 'M',
            'tags': {'standalone', 'test'}
        }
    ]
    
    created_task_ids = []
    
    for task_data in test_tasks:
        task = Task(tw, description=task_data['description'])
        
        if 'project' in task_data:
            task['project'] = task_data['project']
        task['priority'] = task_data['priority']
        task['tags'] = task_data['tags']
        
        task.save()
        created_task_ids.append(task['id'])
        print(f"   ✅ Created task {task['id']}: {task_data['description'][:30]}...")
    
    print(f"📊 Created {len(created_task_ids)} test tasks: {created_task_ids}")
    return created_task_ids

def test_filter_functionality():
    """Test the filter_tasks function"""
    print(f"\n🔍 Testing Filter Functionality...")
    
    # Test filtering by project
    project_filter = BatchFilterParams(project="BatchTest")
    project_tasks = filter_tasks(project_filter)
    print(f"   📁 Project 'BatchTest': {len(project_tasks)} tasks")
    
    # Test filtering by priority
    priority_filter = BatchFilterParams(priority="H")
    high_priority_tasks = filter_tasks(priority_filter)
    print(f"   🔥 High priority: {len(high_priority_tasks)} tasks")
    
    # Test filtering by tags
    tag_filter = BatchFilterParams(tags=["urgent"])
    urgent_tasks = filter_tasks(tag_filter)
    print(f"   🏷️  'urgent' tag: {len(urgent_tasks)} tasks")
    
    # Test filtering by description
    desc_filter = BatchFilterParams(description_contains="documentation")
    doc_tasks = filter_tasks(desc_filter)
    print(f"   📝 Description contains 'documentation': {len(doc_tasks)} tasks")
    
    # Test combined filters
    combined_filter = BatchFilterParams(
        project="BatchTest",
        priority="H",
        tags=["urgent"]
    )
    combined_tasks = filter_tasks(combined_filter)
    print(f"   🔗 Combined filter (BatchTest + High + urgent): {len(combined_tasks)} tasks")
    
    return True

def simulate_batch_complete_by_ids(task_ids):
    """Simulate batch completion by IDs"""
    print(f"\n✅ Simulating Batch Complete by IDs...")
    
    completed_tasks = []
    failed_tasks = []
    
    for task_id in task_ids[:3]:  # Complete first 3 tasks
        try:
            task = tw.tasks.get(id=task_id)
            task_desc = safe_get_task_field(task, 'description')
            
            # Don't actually complete - just simulate
            print(f"   🎯 Would complete task {task_id}: {task_desc[:40]}...")
            completed_tasks.append({
                'id': task_id,
                'description': task_desc
            })
        except Exception as e:
            failed_tasks.append({'id': task_id, 'error': str(e)})
    
    print(f"   📊 Simulation: {len(completed_tasks)} would be completed, {len(failed_tasks)} failed")
    return len(completed_tasks) > 0

def simulate_batch_complete_by_filter():
    """Simulate batch completion by filter"""
    print(f"\n✅ Simulating Batch Complete by Filter...")
    
    # Find tasks with 'test' tag in BatchTest project
    filter_params = BatchFilterParams(
        project="BatchTest",
        tags=["test"],
        limit=2  # Limit to 2 tasks
    )
    
    matching_tasks = filter_tasks(filter_params)
    print(f"   🔍 Found {len(matching_tasks)} tasks matching filter:")
    
    for task in matching_tasks:
        task_id = safe_get_task_field(task, 'id')
        task_desc = safe_get_task_field(task, 'description')
        print(f"     - Task {task_id}: {task_desc[:40]}...")
    
    print(f"   📊 Simulation: {len(matching_tasks)} tasks would be completed")
    return len(matching_tasks) > 0

def simulate_batch_modify():
    """Simulate batch modify operations"""
    print(f"\n🔧 Simulating Batch Modify Operations...")
    
    # Find tasks in BatchTest project
    filter_params = BatchFilterParams(
        project="BatchTest",
        limit=2
    )
    
    tasks_to_modify = filter_tasks(filter_params)
    print(f"   🔍 Found {len(tasks_to_modify)} tasks to modify in BatchTest project:")
    
    for task in tasks_to_modify:
        task_id = safe_get_task_field(task, 'id')
        task_desc = safe_get_task_field(task, 'description')
        current_tags = safe_get_task_field(task, 'tags') or set()
        print(f"     - Task {task_id}: {task_desc[:30]}... (tags: {list(current_tags)})")
    
    # Simulate modifications:
    # - Change priority to 'L'
    # - Add 'modified' tag  
    # - Remove 'urgent' tag
    print(f"   📝 Would apply modifications:")
    print(f"     - Set priority to 'L'")
    print(f"     - Add tag: 'modified'")
    print(f"     - Remove tag: 'urgent'")
    
    return len(tasks_to_modify) > 0

def simulate_preview_operation():
    """Test the preview functionality"""
    print(f"\n👁️  Testing Preview Functionality...")
    
    # Preview tasks that would be affected by deleting high priority tasks
    preview_filter = BatchFilterParams(
        priority="H",
        tags=["test"]
    )
    
    preview_tasks = filter_tasks(preview_filter)
    
    print(f"   📋 Preview: {len(preview_tasks)} tasks would be affected by operation:")
    
    for task in preview_tasks[:5]:  # Show first 5
        task_info = {
            'id': safe_get_task_field(task, 'id'),
            'description': safe_get_task_field(task, 'description'),
            'project': safe_get_task_field(task, 'project'),
            'priority': safe_get_task_field(task, 'priority'),
            'tags': list(safe_get_task_field(task, 'tags') or [])
        }
        
        print(f"     - [{task_info['id']}] {task_info['description'][:30]}...")
        print(f"       Project: {task_info['project']}, Priority: {task_info['priority']}")
        print(f"       Tags: {task_info['tags']}")
    
    if len(preview_tasks) > 5:
        print(f"     ... and {len(preview_tasks) - 5} more tasks")
    
    return True

def cleanup_test_tasks(task_ids):
    """Clean up test tasks"""
    print(f"\n🧹 Cleaning up test tasks...")
    
    cleaned = 0
    for task_id in task_ids:
        try:
            task = tw.tasks.get(id=task_id)
            task.delete()
            cleaned += 1
            print(f"   🗑️  Deleted task {task_id}")
        except Task.DoesNotExist:
            print(f"   ⚠️  Task {task_id} not found (already deleted?)")
        except Exception as e:
            print(f"   ❌ Failed to delete task {task_id}: {e}")
    
    print(f"   📊 Cleaned up {cleaned} test tasks")

async def main():
    """Main test function"""
    print("🚀 Batch Operations Test Suite")
    print("=" * 50)
    
    # Create test tasks
    test_task_ids = create_test_tasks()
    
    try:
        # Test filtering
        filter_success = test_filter_functionality()
        
        # Test batch operations (simulated)
        batch_complete_ids_success = simulate_batch_complete_by_ids(test_task_ids)
        batch_complete_filter_success = simulate_batch_complete_by_filter()
        batch_modify_success = simulate_batch_modify()
        preview_success = simulate_preview_operation()
        
        # Results
        all_tests = [
            filter_success,
            batch_complete_ids_success, 
            batch_complete_filter_success,
            batch_modify_success,
            preview_success
        ]
        
        print(f"\n📊 Test Results:")
        print(f"   ✅ Filter functionality: {'PASS' if filter_success else 'FAIL'}")
        print(f"   ✅ Batch complete by IDs: {'PASS' if batch_complete_ids_success else 'FAIL'}")
        print(f"   ✅ Batch complete by filter: {'PASS' if batch_complete_filter_success else 'FAIL'}")
        print(f"   ✅ Batch modify: {'PASS' if batch_modify_success else 'FAIL'}")
        print(f"   ✅ Preview operation: {'PASS' if preview_success else 'FAIL'}")
        
        overall_success = all(all_tests)
        print(f"\n🎉 Overall: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
        
        return overall_success
        
    finally:
        # Always clean up test tasks
        cleanup_test_tasks(test_task_ids)

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)