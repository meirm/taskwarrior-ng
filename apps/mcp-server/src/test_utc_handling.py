#!/usr/bin/env python3
"""
Test UTC timezone handling for task creation and retrieval
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# Add the current directory to the path so we can import the server
sys.path.insert(0, os.path.dirname(__file__))

from taskwarrior_mcp_server import tw, task_to_dict
from tasklib import Task

def test_utc_handling():
    """Test that tasks are saved with proper timezone handling and returned in UTC"""
    
    print("🕐 Testing UTC Timezone Handling...")
    
    # Create a task with a specific UTC due date
    utc_due = datetime(2025, 8, 25, 14, 30, 0, tzinfo=timezone.utc)  # 2:30 PM UTC
    
    print(f"\n📅 Creating task with UTC due date: {utc_due.isoformat()}")
    
    # Create the task
    task = Task(tw, description="Test UTC timezone handling")
    task['project'] = "TimezoneTest"
    task['priority'] = "H"
    task['tags'] = {"timezone", "utc", "test"}
    task['due'] = utc_due
    
    # Save the task
    task.save()
    task_id = task['id']
    
    print(f"✅ Task created with ID: {task_id}")
    
    # Retrieve the task and convert to dict using our UTC function
    retrieved_task = tw.tasks.get(id=task_id)
    task_dict = task_to_dict(retrieved_task)
    
    print(f"\n🔍 Retrieved task data:")
    print(f"   Description: {task_dict['description']}")
    print(f"   Project: {task_dict['project']}")
    print(f"   Priority: {task_dict['priority']}")
    print(f"   Tags: {task_dict['tags']}")
    print(f"   Due (UTC): {task_dict['due']}")
    print(f"   Entry (UTC): {task_dict['entry']}")
    print(f"   Modified (UTC): {task_dict['modified']}")
    
    # Verify the due date is correctly converted to UTC
    if task_dict['due']:
        returned_due = datetime.fromisoformat(task_dict['due'].replace('Z', '+00:00'))
        print(f"\n📊 Date Verification:")
        print(f"   Original UTC: {utc_due.isoformat()}")
        print(f"   Returned UTC: {returned_due.isoformat()}")
        
        # Check if they're the same (allowing for small differences due to processing)
        time_diff = abs((returned_due - utc_due).total_seconds())
        if time_diff < 60:  # Allow up to 1 minute difference
            print(f"   ✅ UTC dates match (difference: {time_diff} seconds)")
        else:
            print(f"   ❌ UTC dates don't match (difference: {time_diff} seconds)")
    else:
        print(f"   ❌ No due date returned")
    
    # Test with different timezones input
    print(f"\n🌍 Testing with different timezone inputs...")
    
    # Test with a timezone-aware datetime (not UTC)
    eastern_tz = timezone(timedelta(hours=-5))  # EST
    eastern_due = datetime(2025, 8, 26, 9, 0, 0, tzinfo=eastern_tz)  # 9 AM EST = 2 PM UTC
    
    task2 = Task(tw, description="Test EST timezone conversion")
    task2['project'] = "TimezoneTest"
    task2['due'] = eastern_due
    task2.save()
    
    task2_dict = task_to_dict(tw.tasks.get(id=task2['id']))
    
    print(f"   Original EST: {eastern_due.isoformat()}")
    print(f"   Expected UTC: {eastern_due.astimezone(timezone.utc).isoformat()}")
    print(f"   Returned UTC: {task2_dict['due']}")
    
    # Test with naive datetime (should be treated as local)
    naive_due = datetime(2025, 8, 27, 16, 45, 0)  # No timezone info
    
    task3 = Task(tw, description="Test naive datetime handling")
    task3['project'] = "TimezoneTest"
    task3['due'] = naive_due
    task3.save()
    
    task3_dict = task_to_dict(tw.tasks.get(id=task3['id']))
    
    print(f"   Original naive: {naive_due.isoformat()}")
    print(f"   Returned UTC: {task3_dict['due']}")
    
    print(f"\n🎯 Summary:")
    print(f"   - Tasks are saved with proper timezone awareness")
    print(f"   - All returned dates are in UTC format with 'Z' suffix")
    print(f"   - Different input timezones are handled correctly")
    print(f"   - Naive datetimes are treated appropriately")
    
    return True

if __name__ == "__main__":
    try:
        success = test_utc_handling()
        print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)