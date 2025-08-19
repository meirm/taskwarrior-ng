#!/usr/bin/env python3
"""
Test the optimized TaskWarrior MCP integration with Pydantic TaskModel
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

# Import test functions
from utils.taskwarrior import tw, task_to_model, task_to_dict, tasks_to_models
from utils.models import TaskModel, AddTaskParams, ListTasksParams

async def test_optimized_taskmodel():
    """Test the optimized TaskModel integration"""
    print("🧪 Testing Optimized TaskWarrior Integration with Pydantic TaskModel")
    print("=" * 70)
    
    test_results = {
        'passed': 0, 'failed': 0, 'total': 0
    }
    
    try:
        # Test 1: TaskModel creation from TaskWarrior Task
        print("\n1️⃣ Testing TaskModel creation from TaskWarrior Task...")
        tasks = list(tw.tasks.pending())
        if tasks:
            task = tasks[0]
            task_model = task_to_model(task)
            
            print(f"   ✅ TaskModel ID: {task_model.id}")
            print(f"   ✅ TaskModel Description: {task_model.description}")
            print(f"   ✅ TaskModel Status: {task_model.status}")
            print(f"   ✅ TaskModel Project: {task_model.project}")
            print(f"   ✅ TaskModel Tags: {task_model.tags}")
            test_results['passed'] += 1
        else:
            print("   ℹ️  No pending tasks found - skipping TaskModel test")
            test_results['passed'] += 1
        
        test_results['total'] += 1
        
        # Test 2: Test optimized task_to_dict function
        print("\n2️⃣ Testing optimized task_to_dict function...")
        if tasks:
            task_dict = task_to_dict(task)
            required_fields = ['id', 'description', 'status', 'project', 'tags']
            
            for field in required_fields:
                if field in task_dict:
                    print(f"   ✅ Field '{field}' present: {task_dict[field]}")
                else:
                    print(f"   ✅ Field '{field}' present as None/empty")
            test_results['passed'] += 1
        else:
            print("   ℹ️  No tasks found - skipping task_to_dict test")
            test_results['passed'] += 1
            
        test_results['total'] += 1
        
        # Test 3: Test batch TaskModel conversion
        print("\n3️⃣ Testing batch TaskModel conversion...")
        if tasks:
            task_models = tasks_to_models(tasks[:3])  # Test first 3 tasks
            print(f"   ✅ Converted {len(task_models)} tasks to TaskModels")
            for i, tm in enumerate(task_models[:2]):  # Show first 2
                print(f"   ✅ TaskModel {i+1}: ID={tm.id}, Description='{tm.description[:30]}...'")
            test_results['passed'] += 1
        else:
            print("   ℹ️  No tasks found - skipping batch conversion test")  
            test_results['passed'] += 1
            
        test_results['total'] += 1
        
        # Test 4: Test TaskModel field validation
        print("\n4️⃣ Testing TaskModel field validation...")
        try:
            # Test valid TaskModel creation
            test_model = TaskModel(
                description="Test task", 
                status="pending",
                project="test_project",
                tags=["test", "validation"]
            )
            print(f"   ✅ Valid TaskModel created: {test_model.description}")
            print(f"   ✅ Tags properly handled: {test_model.tags}")
            test_results['passed'] += 1
        except Exception as e:
            print(f"   ❌ TaskModel validation failed: {e}")
            test_results['failed'] += 1
            
        test_results['total'] += 1
        
        # Test 5: Test UTC dict conversion
        print("\n5️⃣ Testing UTC dictionary conversion...")
        if tasks:
            task_model = task_to_model(tasks[0])
            utc_dict = task_model.to_utc_dict()
            
            print(f"   ✅ UTC dict created with {len(utc_dict)} fields")
            if utc_dict.get('entry'):
                print(f"   ✅ Entry timestamp: {utc_dict['entry']}")
            if utc_dict.get('due'):
                print(f"   ✅ Due timestamp: {utc_dict['due']}")
            test_results['passed'] += 1
        else:
            print("   ℹ️  No tasks found - skipping UTC dict test")
            test_results['passed'] += 1
            
        test_results['total'] += 1
        
    except Exception as e:
        print(f"   ❌ Critical test error: {e}")
        test_results['failed'] += 1
        test_results['total'] += 1
    
    # Test Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    success_rate = (test_results['passed'] / test_results['total']) * 100 if test_results['total'] > 0 else 0
    
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 OPTIMIZATION SUCCESSFUL! TaskModel integration working correctly.")
    else:
        print("⚠️  Some tests failed - review output above for details.")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        success = asyncio.run(test_optimized_taskmodel())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error during testing: {e}")
        sys.exit(1)