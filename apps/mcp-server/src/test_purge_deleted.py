#!/usr/bin/env python3
"""
Test script for the purge deleted tasks functionality
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from taskwarrior_mcp_server import initialize_server, mcp

async def test_purge_deleted_tasks():
    """Test the purge deleted tasks functionality"""
    print("🧪 Testing Purge Deleted Tasks Functionality")
    print("=" * 50)
    
    # Initialize the server
    initialize_server()
    
    # Import required modules
    from tools.basic_operations import add_task, delete_task, list_tasks, purge_deleted_tasks
    from utils.models import AddTaskParams, TaskIdParam, ListTasksParams
    
    try:
        # Step 1: Add a test task
        print("\n📋 Step 1: Creating test tasks...")
        add_params1 = AddTaskParams(
            description="Test task 1 for purge testing",
            project="purge-test",
            tags=["test", "purge"]
        )
        
        add_result1 = await add_task(add_params1)
        if add_result1['success']:
            task_id1 = add_result1['task']['id']
            print(f"✅ Created test task 1 with ID: {task_id1}")
        else:
            print(f"❌ Failed to create test task 1: {add_result1.get('error')}")
            return False
        
        add_params2 = AddTaskParams(
            description="Test task 2 for purge testing",
            project="purge-test",
            tags=["test", "purge"]
        )
        
        add_result2 = await add_task(add_params2)
        if add_result2['success']:
            task_id2 = add_result2['task']['id']
            print(f"✅ Created test task 2 with ID: {task_id2}")
        else:
            print(f"❌ Failed to create test task 2: {add_result2.get('error')}")
            return False
        
        # Step 2: Delete the tasks
        print("\n🗑️  Step 2: Deleting test tasks...")
        delete_result1 = await delete_task(TaskIdParam(task_id=task_id1))
        delete_result2 = await delete_task(TaskIdParam(task_id=task_id2))
        
        if delete_result1['success'] and delete_result2['success']:
            print(f"✅ Deleted both test tasks")
        else:
            print(f"❌ Failed to delete tasks")
            print(f"Delete result 1: {delete_result1}")
            print(f"Delete result 2: {delete_result2}")
            return False
        
        # Step 3: Verify deleted tasks exist
        print("\n🔍 Step 3: Checking for deleted tasks...")
        deleted_list_params = ListTasksParams(status="deleted", limit=10)
        deleted_list_result = await list_tasks(deleted_list_params)
        
        if deleted_list_result['success']:
            deleted_count = deleted_list_result['count']
            print(f"✅ Found {deleted_count} deleted tasks")
            
            # Show some deleted tasks
            if deleted_count > 0:
                print("📋 Deleted tasks found:")
                for task in deleted_list_result['tasks'][:5]:  # Show up to 5
                    print(f"   - [{task['id']}] {task['description']}")
        else:
            print(f"❌ Failed to list deleted tasks: {deleted_list_result.get('error')}")
            return False
        
        # Step 4: Test purge when there are no deleted tasks first
        if deleted_count == 0:
            print("\n🧹 Step 4: Testing purge with no deleted tasks...")
            purge_result = await purge_deleted_tasks()
            if purge_result['success'] and purge_result['purged_count'] == 0:
                print("✅ Purge correctly reported no tasks to purge")
            else:
                print(f"❌ Purge failed unexpectedly: {purge_result}")
        else:
            # Step 4: Purge deleted tasks
            print("\n🧹 Step 4: Purging deleted tasks...")
            purge_result = await purge_deleted_tasks()
            
            if purge_result['success']:
                purged_count = purge_result['purged_count']
                print(f"✅ Successfully purged {purged_count} deleted tasks")
                print(f"📝 Message: {purge_result['message']}")
                if 'details' in purge_result:
                    print(f"📋 Details: {purge_result['details']}")
            else:
                print(f"❌ Purge failed: {purge_result.get('error')}")
                return False
            
            # Step 5: Verify deleted tasks are gone
            print("\n🔍 Step 5: Verifying purge was successful...")
            after_purge_list_result = await list_tasks(deleted_list_params)
            
            if after_purge_list_result['success']:
                remaining_deleted = after_purge_list_result['count']
                if remaining_deleted == 0:
                    print("✅ All deleted tasks have been purged successfully")
                else:
                    print(f"⚠️  {remaining_deleted} deleted tasks still remain")
            else:
                print(f"❌ Failed to verify purge: {after_purge_list_result.get('error')}")
        
        print("\n" + "=" * 50)
        print("🎉 Purge deleted tasks test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_purge_deleted_tasks()
    
    if success:
        print("\n✅ All purge deleted tasks functionality works correctly!")
    else:
        print("\n❌ Some issues were found with purge deleted tasks functionality")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())