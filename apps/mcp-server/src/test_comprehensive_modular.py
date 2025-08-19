#!/usr/bin/env python3
"""
Comprehensive test for all components of the modular Taskwarrior MCP Server
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from server import initialize_server, mcp

async def test_all_components():
    """Test all tools, resources, and prompts"""
    print("🧪 Comprehensive Modular Server Test")
    print("=" * 50)
    
    # Initialize the server
    initialize_server()
    
    # Import all modules
    from tools.basic_operations import add_task, list_tasks, get_task, complete_task, modify_task, delete_task, start_task, stop_task
    from tools.metadata_operations import get_projects, get_tags, get_summary
    from tools.batch_operations import batch_complete_by_ids, batch_delete_by_ids, batch_start_by_ids, batch_stop_by_ids, batch_modify_tasks
    from resources.reports import daily_report, weekly_summary, live_tasks
    from prompts.planning import daily_planning_prompt, task_prioritization_prompt, task_formatter_prompt
    from utils.models import AddTaskParams, ListTasksParams, TaskIdParam, ModifyTaskParams, BatchTaskIdsParams, BatchModifyParams, BatchFilterParams
    
    test_results = []
    
    # Test basic operations
    print("\n📋 Testing Basic Operations...")
    
    # Add a test task
    add_params = AddTaskParams(
        description="Test task for modular server",
        project="testing",
        priority="H",
        tags=["test", "modular"],
        due=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace('+00:00', 'Z')
    )
    
    add_result = await add_task(add_params)
    if add_result['success']:
        print(f"✅ Add task: Created task {add_result['task']['id']}")
        test_task_id = add_result['task']['id']
        test_results.append("add_task: PASS")
    else:
        print(f"❌ Add task failed: {add_result.get('error')}")
        test_results.append("add_task: FAIL")
        return False
    
    # List tasks
    list_params = ListTasksParams(status="pending", limit=10)
    list_result = await list_tasks(list_params)
    if list_result['success']:
        print(f"✅ List tasks: Found {list_result['count']} tasks")
        test_results.append("list_tasks: PASS")
    else:
        print(f"❌ List tasks failed: {list_result.get('error')}")
        test_results.append("list_tasks: FAIL")
    
    # Get specific task
    get_params = TaskIdParam(task_id=test_task_id)
    get_result = await get_task(get_params)
    if get_result['success']:
        print(f"✅ Get task: Retrieved task {test_task_id}")
        test_results.append("get_task: PASS")
    else:
        print(f"❌ Get task failed: {get_result.get('error')}")
        test_results.append("get_task: FAIL")
    
    # Test metadata operations
    print("\n🏷️  Testing Metadata Operations...")
    
    # Get projects
    projects_result = await get_projects()
    if projects_result['success']:
        print(f"✅ Get projects: Found {projects_result['count']} projects")
        test_results.append("get_projects: PASS")
    else:
        print(f"❌ Get projects failed: {projects_result.get('error')}")
        test_results.append("get_projects: FAIL")
    
    # Get tags
    tags_result = await get_tags()
    if tags_result['success']:
        print(f"✅ Get tags: Found {tags_result['count']} tags")
        test_results.append("get_tags: PASS")
    else:
        print(f"❌ Get tags failed: {tags_result.get('error')}")
        test_results.append("get_tags: FAIL")
    
    # Get summary
    summary_result = await get_summary()
    if summary_result['success']:
        print(f"✅ Get summary: {summary_result['summary']['status']}")
        test_results.append("get_summary: PASS")
    else:
        print(f"❌ Get summary failed: {summary_result.get('error')}")
        test_results.append("get_summary: FAIL")
    
    # Test batch operations
    print("\n🔄 Testing Batch Operations...")
    
    # Start the test task
    start_params = TaskIdParam(task_id=test_task_id)
    start_result = await start_task(start_params)
    if start_result['success']:
        print(f"✅ Start task: Started task {test_task_id}")
        test_results.append("start_task: PASS")
    else:
        print(f"❌ Start task failed: {start_result.get('error')}")
        test_results.append("start_task: FAIL")
    
    # Stop the test task
    stop_params = TaskIdParam(task_id=test_task_id)
    stop_result = await stop_task(stop_params)
    if stop_result['success']:
        print(f"✅ Stop task: Stopped task {test_task_id}")
        test_results.append("stop_task: PASS")
    else:
        print(f"❌ Stop task failed: {stop_result.get('error')}")
        test_results.append("stop_task: FAIL")
    
    # Batch modify tasks
    batch_modify_params = BatchModifyParams(
        task_ids=[test_task_id],
        priority="M",
        add_tags=["batch-test"]
    )
    batch_modify_result = await batch_modify_tasks(batch_modify_params)
    if batch_modify_result['success']:
        print(f"✅ Batch modify: Modified {batch_modify_result['modified_count']} tasks")
        test_results.append("batch_modify: PASS")
    else:
        print(f"❌ Batch modify failed: {batch_modify_result.get('error')}")
        test_results.append("batch_modify: FAIL")
    
    # Test resources
    print("\n📊 Testing Resources...")
    
    # Daily report
    daily_report_result = await daily_report()
    if "Daily Task Report" in daily_report_result:
        print(f"✅ Daily report: Generated {len(daily_report_result)} chars")
        test_results.append("daily_report: PASS")
    else:
        print(f"❌ Daily report failed: {daily_report_result[:100]}...")
        test_results.append("daily_report: FAIL")
    
    # Weekly summary
    weekly_summary_result = await weekly_summary()
    if "Weekly Summary" in weekly_summary_result:
        print(f"✅ Weekly summary: Generated {len(weekly_summary_result)} chars")
        test_results.append("weekly_summary: PASS")
    else:
        print(f"❌ Weekly summary failed: {weekly_summary_result[:100]}...")
        test_results.append("weekly_summary: FAIL")
    
    # Live tasks
    live_tasks_result = await live_tasks()
    if isinstance(live_tasks_result, dict) and 'timestamp' in live_tasks_result:
        print(f"✅ Live tasks: Found {live_tasks_result.get('total_tasks', 0)} tasks")
        test_results.append("live_tasks: PASS")
    else:
        print(f"❌ Live tasks failed: {str(live_tasks_result)[:100]}...")
        test_results.append("live_tasks: FAIL")
    
    # Test prompts
    print("\n💡 Testing Prompts...")
    
    # Daily planning prompt
    daily_planning_result = await daily_planning_prompt()
    if "daily task planning" in daily_planning_result:
        print(f"✅ Daily planning prompt: Generated {len(daily_planning_result)} chars")
        test_results.append("daily_planning_prompt: PASS")
    else:
        print(f"❌ Daily planning prompt failed: {daily_planning_result[:100]}...")
        test_results.append("daily_planning_prompt: FAIL")
    
    # Task prioritization prompt
    prioritization_result = await task_prioritization_prompt()
    if "task prioritization" in prioritization_result:
        print(f"✅ Task prioritization prompt: Generated {len(prioritization_result)} chars")
        test_results.append("task_prioritization_prompt: PASS")
    else:
        print(f"❌ Task prioritization prompt failed: {prioritization_result[:100]}...")
        test_results.append("task_prioritization_prompt: FAIL")
    
    # Task formatter prompt
    formatter_result = await task_formatter_prompt()
    if "markdown format" in formatter_result:
        print(f"✅ Task formatter prompt: Generated {len(formatter_result)} chars")
        test_results.append("task_formatter_prompt: PASS")
    else:
        print(f"❌ Task formatter prompt failed: {formatter_result[:100]}...")
        test_results.append("task_formatter_prompt: FAIL")
    
    # Clean up - complete the test task
    complete_params = TaskIdParam(task_id=test_task_id)
    complete_result = await complete_task(complete_params)
    if complete_result['success']:
        print(f"✅ Complete task: Completed test task {test_task_id}")
        test_results.append("complete_task: PASS")
    else:
        print(f"❌ Complete task failed: {complete_result.get('error')}")
        test_results.append("complete_task: FAIL")
    
    # Final results
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("=" * 50)
    
    passed_tests = [r for r in test_results if "PASS" in r]
    failed_tests = [r for r in test_results if "FAIL" in r]
    
    for result in test_results:
        status_icon = "✅" if "PASS" in result else "❌"
        print(f"{status_icon} {result}")
    
    print(f"\n🎯 Results: {len(passed_tests)} passed, {len(failed_tests)} failed")
    
    if len(failed_tests) == 0:
        print("\n🎉 All modular components working perfectly!")
        return True
    else:
        print(f"\n⚠️  {len(failed_tests)} components need attention")
        return False

async def main():
    """Main test function"""
    success = await test_all_components()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())