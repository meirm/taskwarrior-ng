#!/usr/bin/env python3
"""
Simple test for the purge deleted tasks functionality
"""
import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from taskwarrior_mcp_server import initialize_server, mcp

async def test_purge_functionality():
    """Test purge functionality with existing deleted tasks"""
    print("🧪 Simple Purge Deleted Tasks Test")
    print("=" * 40)
    
    # Initialize the server
    initialize_server()
    
    # Import required modules
    from tools.basic_operations import list_tasks, purge_deleted_tasks
    from utils.models import ListTasksParams
    
    try:
        # Step 1: Check current deleted tasks
        print("\n🔍 Step 1: Checking for existing deleted tasks...")
        deleted_list_params = ListTasksParams(status="deleted", limit=20)
        deleted_list_result = await list_tasks(deleted_list_params)
        
        if deleted_list_result['success']:
            deleted_count = deleted_list_result['count']
            print(f"✅ Found {deleted_count} deleted tasks")
            
            if deleted_count > 0:
                print("📋 Sample deleted tasks:")
                for task in deleted_list_result['tasks'][:3]:  # Show first 3
                    print(f"   - [{task['id']}] {task['description']}")
        else:
            print(f"❌ Failed to list deleted tasks: {deleted_list_result.get('error')}")
            return False
        
        # Step 2: Test purge functionality
        print(f"\n🧹 Step 2: Testing purge functionality...")
        print(f"This will purge {deleted_count} deleted tasks")
        
        if deleted_count == 0:
            print("No deleted tasks to purge - testing empty purge")
        
        purge_result = await purge_deleted_tasks()
        
        if purge_result['success']:
            purged_count = purge_result['purged_count']
            print(f"✅ Purge completed successfully")
            print(f"📊 Purged count: {purged_count}")
            print(f"📝 Message: {purge_result['message']}")
            if 'details' in purge_result:
                print(f"📋 Details: {purge_result['details']}")
        else:
            print(f"❌ Purge failed: {purge_result.get('error')}")
            if 'found_deleted_count' in purge_result:
                print(f"📊 Found deleted tasks: {purge_result['found_deleted_count']}")
            return False
        
        # Step 3: Verify purge results
        print(f"\n🔍 Step 3: Verifying purge results...")
        after_purge_result = await list_tasks(deleted_list_params)
        
        if after_purge_result['success']:
            remaining_deleted = after_purge_result['count']
            print(f"📊 Remaining deleted tasks: {remaining_deleted}")
            
            if remaining_deleted == 0:
                print("✅ All deleted tasks successfully purged")
            else:
                print(f"⚠️  {remaining_deleted} deleted tasks still present")
                # Show remaining tasks
                print("📋 Remaining deleted tasks:")
                for task in after_purge_result['tasks'][:3]:
                    print(f"   - [{task['id']}] {task['description']}")
        else:
            print(f"❌ Failed to verify purge: {after_purge_result.get('error')}")
            return False
        
        print("\n" + "=" * 40)
        print("🎉 Purge test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Testing purge deleted tasks functionality...")
    success = await test_purge_functionality()
    
    if success:
        print("\n✅ Purge functionality test passed!")
    else:
        print("\n❌ Purge functionality test failed!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())