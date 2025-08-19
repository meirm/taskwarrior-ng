#!/usr/bin/env python3
"""
Complete test of task creation with all data fields and UTC timezone handling
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# Add the current directory to the path so we can import the server
sys.path.insert(0, os.path.dirname(__file__))

from taskwarrior_mcp_server import tw, task_to_dict
from tasklib import Task

def test_complete_task_creation():
    """Test creating a task with all possible data fields and UTC dates"""
    
    print("🚀 Complete Task Creation Test with UTC Handling")
    print("=" * 60)
    
    # Define all task data with UTC timezone
    utc_due = datetime.now(timezone.utc) + timedelta(days=5, hours=3)
    
    task_data = {
        'description': 'Comprehensive task with all fields: documentation, testing, and deployment',
        'project': 'FullStackApp',
        'priority': 'H',
        'tags': {'urgent', 'documentation', 'testing', 'deployment', 'fullstack'},
        'due': utc_due
    }
    
    print(f"\n📝 Creating task with comprehensive data:")
    print(f"   📋 Description: {task_data['description']}")
    print(f"   📁 Project: {task_data['project']}")
    print(f"   🔥 Priority: {task_data['priority']}")
    print(f"   🏷️  Tags: {task_data['tags']}")
    print(f"   📅 Due (UTC): {task_data['due'].isoformat()}")
    
    # Create and save the task
    task = Task(tw, description=task_data['description'])
    
    # Set all fields
    task['project'] = task_data['project']
    task['priority'] = task_data['priority']
    task['tags'] = task_data['tags']
    task['due'] = task_data['due']
    
    # Save the task
    task.save()
    task_id = task['id']
    
    print(f"\n✅ Task created successfully with ID: {task_id}")
    
    # Retrieve and verify all data
    print(f"\n🔍 Retrieving and verifying all task data...")
    
    retrieved_task = tw.tasks.get(id=task_id)
    task_dict = task_to_dict(retrieved_task)
    
    # Verification checklist
    verifications = []
    
    # Check description
    if task_dict['description'] == task_data['description']:
        verifications.append(("Description", "✅", task_dict['description'][:50] + "..."))
    else:
        verifications.append(("Description", "❌", f"Expected: {task_data['description']}, Got: {task_dict['description']}"))
    
    # Check project
    if task_dict['project'] == task_data['project']:
        verifications.append(("Project", "✅", task_dict['project']))
    else:
        verifications.append(("Project", "❌", f"Expected: {task_data['project']}, Got: {task_dict['project']}"))
    
    # Check priority
    if task_dict['priority'] == task_data['priority']:
        verifications.append(("Priority", "✅", task_dict['priority']))
    else:
        verifications.append(("Priority", "❌", f"Expected: {task_data['priority']}, Got: {task_dict['priority']}"))
    
    # Check tags
    expected_tags = set(task_data['tags'])
    actual_tags = set(task_dict['tags'])
    if expected_tags == actual_tags:
        verifications.append(("Tags", "✅", f"{len(actual_tags)} tags"))
    else:
        verifications.append(("Tags", "❌", f"Expected: {expected_tags}, Got: {actual_tags}"))
    
    # Check due date (UTC)
    if task_dict['due']:
        returned_due = datetime.fromisoformat(task_dict['due'].replace('Z', '+00:00'))
        time_diff = abs((returned_due - task_data['due']).total_seconds())
        if time_diff < 60:  # Allow 1 minute tolerance
            verifications.append(("Due Date", "✅", f"UTC: {task_dict['due']}"))
        else:
            verifications.append(("Due Date", "❌", f"Time difference: {time_diff} seconds"))
    else:
        verifications.append(("Due Date", "❌", "No due date returned"))
    
    # Check auto-generated fields
    auto_fields = [
        ("ID", task_dict['id']),
        ("UUID", task_dict['uuid']),
        ("Status", task_dict['status']),
        ("Urgency", task_dict['urgency']),
        ("Entry", task_dict['entry']),
        ("Modified", task_dict['modified'])
    ]
    
    for field_name, field_value in auto_fields:
        if field_value is not None:
            verifications.append((field_name, "✅", str(field_value)[:30]))
        else:
            verifications.append((field_name, "❌", "Not set"))
    
    # Print verification results
    print(f"\n📊 Verification Results:")
    print("-" * 50)
    
    passed = 0
    failed = 0
    
    for field, status, details in verifications:
        print(f"   {status} {field:12}: {details}")
        if status == "✅":
            passed += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"   📈 Summary: {passed} passed, {failed} failed")
    
    # Show complete task data
    print(f"\n📋 Complete Task Data (JSON):")
    print("-" * 30)
    import json
    print(json.dumps(task_dict, indent=2))
    
    # Test task retrieval by different methods
    print(f"\n🔎 Testing Task Retrieval Methods:")
    print("-" * 40)
    
    # By project
    project_tasks = tw.tasks.filter(project=task_data['project'])
    print(f"   📁 By Project '{task_data['project']}': {len(project_tasks)} task(s)")
    
    # By priority
    priority_tasks = tw.tasks.filter(priority=task_data['priority'])
    print(f"   🔥 By Priority '{task_data['priority']}': {len(priority_tasks)} task(s)")
    
    # By status
    pending_tasks = tw.tasks.pending()
    print(f"   📋 Pending tasks: {len(pending_tasks)} task(s)")
    
    # By tags
    tag_count = 0
    for t in pending_tasks:
        try:
            if t['tags'] and 'urgent' in t['tags']:
                tag_count += 1
        except KeyError:
            continue
    print(f"   🏷️  With 'urgent' tag: {tag_count} task(s)")
    
    success = failed == 0
    
    print(f"\n{'🎉 All data saved and retrieved correctly!' if success else '⚠️  Some verifications failed!'}")
    print(f"✨ Task creation with UTC timezone handling: {'PASSED' if success else 'FAILED'}")
    
    return success

if __name__ == "__main__":
    try:
        success = test_complete_task_creation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)