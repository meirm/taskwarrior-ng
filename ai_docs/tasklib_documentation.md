# Tasklib Documentation - Python Library for Taskwarrior

*Last Updated: January 2025*

## Overview

Tasklib is a Python library for interacting with Taskwarrior databases, using a queryset API similar to Django's ORM. It provides a Pythonic interface to manage tasks programmatically.

## Official Resources

- **GitHub Repository**: [github.com/GothenburgBitFactory/tasklib](https://github.com/GothenburgBitFactory/tasklib)
- **Documentation**: [tasklib.readthedocs.io](https://tasklib.readthedocs.io/en/latest/)
- **PyPI Package**: [pypi.org/project/tasklib](https://pypi.org/project/tasklib)

## Requirements (2025)

- Python 3.5 and above (Python 3.11+ recommended for best performance)
- Taskwarrior 2.4.x and above (Latest stable: 2.6.x or 3.x)
- pytz for timezone support (optional but recommended)

## Installation

```bash
pip install tasklib
```

## Basic Usage

### Initialization

```python
from tasklib import TaskWarrior

# Initialize with default location (~/.task)
tw = TaskWarrior()

# Or specify custom data location
tw = TaskWarrior(data_location='/path/to/task/data')

# With custom taskrc configuration
tw = TaskWarrior(taskrc_location='/path/to/.taskrc')
```

### Creating Tasks

```python
from tasklib import Task

# Create a new task
task = Task(tw, description="Write documentation")

# Add attributes before saving
task['project'] = 'work'
task['priority'] = 'H'
task['due'] = datetime.datetime(2024, 12, 31)
task['tags'] = ['urgent', 'documentation']

# Save to database
task.save()
```

### Querying Tasks

```python
# Get all pending tasks
pending_tasks = tw.tasks.pending()

# Filter tasks
work_tasks = tw.tasks.filter(project='work')
urgent_tasks = tw.tasks.filter(tags__contains=['urgent'])
overdue_tasks = tw.tasks.filter(status='pending', due__before=datetime.datetime.now())

# Combine filters
important_work = tw.tasks.filter(
    project='work',
    priority='H',
    status='pending'
)

# Get a specific task by ID
task = tw.tasks.get(id=5)
```

### Modifying Tasks

```python
# Get a task
task = tw.tasks.get(id=1)

# Modify attributes
task['description'] = "Updated description"
task['priority'] = 'M'
task['tags'].add('modified')

# Save changes
task.save()

# Mark as completed
task.done()

# Delete a task
task.delete()
```

### Working with Dates

```python
import datetime
from pytz import timezone

# Tasklib handles timezone conversions automatically
eastern = timezone('US/Eastern')
due_date = eastern.localize(datetime.datetime(2024, 12, 31, 23, 59))

task = Task(tw, description="New Year's Eve task")
task['due'] = due_date
task.save()

# Dates are returned as timezone-aware datetime objects
print(task['due'])  # Will be in local timezone
```

## Advanced Features

### User Defined Attributes (UDAs)

```python
# UDAs defined in .taskrc are automatically recognized
task = Task(tw, description="Custom task")
task['my_custom_uda'] = "custom value"
task.save()

# Query by UDA
custom_tasks = tw.tasks.filter(my_custom_uda='custom value')
```

### Annotations

```python
# Add annotations to a task
task = tw.tasks.get(id=1)
task.add_annotation("This is a note about the task")
task.add_annotation("Another important note")

# Access annotations
for annotation in task['annotations']:
    print(f"{annotation['entry']}: {annotation['description']}")
```

### Dependencies

```python
# Create task dependencies
task1 = Task(tw, description="First task")
task1.save()

task2 = Task(tw, description="Second task depends on first")
task2['depends'] = [task1['uuid']]
task2.save()

# Query dependencies
dependent_tasks = tw.tasks.filter(depends__contains=[task1['uuid']])
```

### Recurrence

```python
# Create a recurring task
task = Task(tw, description="Daily standup")
task['recur'] = 'daily'
task['due'] = datetime.datetime.now() + datetime.timedelta(days=1)
task.save()
```

## Hook Scripts Support

Tasklib supports TaskWarrior hook scripts (2.4.0+):

```python
#!/usr/bin/env python
from tasklib import TaskWarrior, Task

def on_add_hook(task):
    """Hook called when a task is added"""
    if 'project' not in task:
        task['project'] = 'inbox'
    return task

def on_modify_hook(original, modified):
    """Hook called when a task is modified"""
    if modified['status'] == 'completed':
        # Log completion
        print(f"Task completed: {modified['description']}")
    return modified
```

## Django-like QuerySet API

```python
# Chaining filters
tasks = tw.tasks.filter(project='work').filter(status='pending')

# Exclude
non_urgent = tw.tasks.exclude(priority='H')

# Count
pending_count = tw.tasks.pending().count()

# Iteration
for task in tw.tasks.pending():
    print(task['description'])

# Slicing
first_ten = tw.tasks.pending()[:10]
```

## Complex Queries with Q Objects

```python
from tasklib import Q

# OR queries
urgent_or_work = tw.tasks.filter(
    Q(priority='H') | Q(project='work')
)

# AND queries with negation
important_not_done = tw.tasks.filter(
    Q(priority='H') & ~Q(status='completed')
)

# Complex combinations
complex_query = tw.tasks.filter(
    (Q(project='work') | Q(project='personal')) &
    Q(status='pending') &
    ~Q(tags__contains=['someday'])
)
```

## Error Handling

```python
from tasklib.exceptions import TaskWarriorException

try:
    task = tw.tasks.get(id=999)
except Task.DoesNotExist:
    print("Task not found")
except TaskWarriorException as e:
    print(f"TaskWarrior error: {e}")
```

## Serialization

```python
# Convert task to dictionary
task_dict = task.export_data()

# Create task from dictionary
imported_task = Task(tw)
imported_task.import_data(task_dict)
imported_task.save()

# JSON serialization
import json
json_data = json.dumps(task.export_data(), default=str)
```

## Performance Tips

1. **Use filters efficiently**: Filter at the query level rather than in Python
2. **Batch operations**: Save multiple changes together
3. **Cache TaskWarrior instance**: Reuse the same TaskWarrior object
4. **Limit query results**: Use slicing to limit large result sets

## Alternative: taskw Library

For simpler use cases, consider `taskw`:

```python
from taskw import TaskWarrior

tw = TaskWarrior()

# Load tasks
tasks = tw.load_tasks()

# Add a task
tw.task_add("New task")

# Update a task
tw.task_update({"id": 1, "description": "Updated"})

# Mark as done
tw.task_done(id=1)
```

## Best Practices

1. **Always use timezone-aware datetimes** when working with dates
2. **Handle exceptions** properly, especially Task.DoesNotExist
3. **Use UDAs** for custom fields instead of hacking the description
4. **Leverage filters** instead of loading all tasks and filtering in Python
5. **Save once** after making multiple changes to a task
6. **Use appropriate data types** - dates as datetime objects, not strings

## Important Notes for 2025

### Task Object Access Patterns
```python
# Task objects DON'T support .get() method
# Use direct access with error handling instead

# WRONG - This will raise AttributeError
value = task.get('project', 'default')

# CORRECT - Use try/except or check existence
try:
    value = task['project']
except KeyError:
    value = 'default'

# Or check if key exists
if 'project' in task:
    value = task['project']
```

### Task Creation Best Practice
```python
# Use Task constructor directly, not .create()
task = Task(tw, description="New task")
task['project'] = 'work'
task.save()

# NOT: tw.tasks.pending().create(...)  # This doesn't exist
```

### Serialization for APIs
```python
# Use export_data() for JSON serialization
task_json = task.export_data()  # Returns JSON string
# Parse if needed
import json
task_dict = json.loads(task_json)
```

## Common Patterns

### Inbox Processing
```python
# Get all inbox tasks (no project assigned)
inbox = tw.tasks.filter(project=None, status='pending')
for task in inbox:
    # Process and assign project
    task['project'] = determine_project(task['description'])
    task.save()
```

### Daily Review
```python
from datetime import datetime, timedelta

# Tasks due today
today = datetime.now().date()
due_today = tw.tasks.filter(
    due__gte=today,
    due__lt=today + timedelta(days=1)
)

# Overdue tasks
overdue = tw.tasks.filter(
    due__lt=datetime.now(),
    status='pending'
)
```

### Project Summary
```python
# Get project statistics
projects = {}
for task in tw.tasks.pending():
    project = task.get('project', 'No Project')
    if project not in projects:
        projects[project] = {'count': 0, 'high_priority': 0}
    projects[project]['count'] += 1
    if task.get('priority') == 'H':
        projects[project]['high_priority'] += 1
```

## Troubleshooting

1. **ImportError**: Ensure tasklib is installed: `pip install tasklib`
2. **TaskWarrior not found**: Make sure `task` command is in PATH
3. **Permission errors**: Check file permissions on task data directory
4. **Timezone issues**: Install pytz: `pip install pytz`
5. **Version incompatibility**: Check TaskWarrior version (2.4.0+ required)

## Additional Resources

- [TaskWarrior Documentation](https://taskwarrior.org/docs/)
- [TaskWarrior Tools](https://taskwarrior.org/tools/)
- [tasklib GitHub Issues](https://github.com/GothenburgBitFactory/tasklib/issues)
- [tasklib ReadTheDocs](https://tasklib.readthedocs.io)