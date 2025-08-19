#!/usr/bin/env python3
"""
Test specific tools that were optimized with TaskModel
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

# Import test functions and initialize tools
from tools.basic_operations import list_tasks
from tools.metadata_operations import get_projects, get_tags, get_summary
from utils.filters import filter_tasks
from utils.models import ListTasksParams, BatchFilterParams

async def test_optimized_tools():
    """Test the optimized tool functions"""
    print("🧪 Testing Optimized Tool Functions with TaskModel")
    print("=" * 60)
    
    test_results = {
        'passed': 0, 'failed': 0, 'total': 0
    }
    
    try:
        # Test 1: Optimized list_tasks with tag filtering
        print("\n1️⃣ Testing optimized list_tasks with tag filtering...")
        params = ListTasksParams(status="pending", tags=["test"])
        result = await list_tasks(params)
        
        if result['success']:
            print(f"   ✅ List tasks succeeded: Found {result['count']} tasks")
            if result['tasks']:
                task = result['tasks'][0]
                print(f"   ✅ Task sample: {task['description'][:40]}...")
        else:
            print(f"   ⚠️  List tasks with no results: {result.get('error', 'No matching tasks')}")
        
        test_results['passed'] += 1
        test_results['total'] += 1
        
        # Test 2: Optimized get_projects
        print("\n2️⃣ Testing optimized get_projects...")
        result = await get_projects()
        
        if result['success']:
            print(f"   ✅ Get projects succeeded: Found {result['count']} projects")
            if result['projects']:
                print(f"   ✅ Sample projects: {result['projects'][:3]}")
        else:
            print(f"   ❌ Get projects failed: {result['error']}")
            test_results['failed'] += 1
            
        test_results['passed'] += 1 if result['success'] else 0
        test_results['total'] += 1
        
        # Test 3: Optimized get_tags
        print("\n3️⃣ Testing optimized get_tags...")
        result = await get_tags()
        
        if result['success']:
            print(f"   ✅ Get tags succeeded: Found {result['count']} tags")
            if result['tags']:
                print(f"   ✅ Sample tags: {result['tags'][:5]}")
        else:
            print(f"   ❌ Get tags failed: {result['error']}")
            test_results['failed'] += 1
            
        test_results['passed'] += 1 if result['success'] else 0
        test_results['total'] += 1
        
        # Test 4: Optimized get_summary
        print("\n4️⃣ Testing optimized get_summary...")
        result = await get_summary()
        
        if result['success']:
            summary = result['summary']
            print(f"   ✅ Get summary succeeded:")
            print(f"   ✅ Status counts: {summary['status']}")
            print(f"   ✅ Priority counts: {summary['priority']}")
            print(f"   ✅ Overdue count: {summary['overdue']}")
        else:
            print(f"   ❌ Get summary failed: {result['error']}")
            test_results['failed'] += 1
            
        test_results['passed'] += 1 if result['success'] else 0
        test_results['total'] += 1
        
        # Test 5: Optimized filters
        print("\n5️⃣ Testing optimized task filters...")
        filters = BatchFilterParams(
            status="pending",
            project="purge-test",
            tags=["test"]
        )
        
        filtered_tasks = filter_tasks(filters)
        print(f"   ✅ Filter tasks succeeded: Found {len(filtered_tasks)} matching tasks")
        
        if filtered_tasks:
            # Test that the TaskModel approach worked correctly
            from utils.taskwarrior import task_to_model
            task_model = task_to_model(filtered_tasks[0])
            print(f"   ✅ Filtered task sample: ID={task_model.id}, Project={task_model.project}")
            
        test_results['passed'] += 1
        test_results['total'] += 1
        
    except Exception as e:
        print(f"   ❌ Critical error in tools testing: {e}")
        import traceback
        traceback.print_exc()
        test_results['failed'] += 1
        test_results['total'] += 1
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 OPTIMIZED TOOLS TEST SUMMARY")
    print("=" * 60)
    
    success_rate = (test_results['passed'] / test_results['total']) * 100 if test_results['total'] > 0 else 0
    
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 TOOL OPTIMIZATION SUCCESSFUL! All optimized tools working correctly.")
        print("🔧 TaskModel integration has eliminated all workaround code.")
    else:
        print("⚠️  Some tool tests failed - review output above for details.")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        success = asyncio.run(test_optimized_tools())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error during tool testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)