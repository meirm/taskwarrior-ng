"""
Basic task operations: add, list, get, complete, modify, delete, start, stop
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Annotated

from fastmcp import FastMCP
from pydantic import Field
from tasklib import Task

from utils.taskwarrior import tw, task_to_dict, task_to_model

logger = logging.getLogger("taskwarrior-mcp.tools.basic")

# MCP instance will be injected by the server
mcp: FastMCP = None

def init_tools(mcp_instance: FastMCP):
    """Initialize tools with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register all tools with the MCP instance
    mcp.tool()(add_task)
    mcp.tool()(list_tasks)
    mcp.tool()(get_task)
    mcp.tool()(complete_task)
    mcp.tool()(uncomplete_task)
    mcp.tool()(modify_task)
    mcp.tool()(delete_task)
    mcp.tool()(start_task)
    mcp.tool()(stop_task)
    mcp.tool()(restore_task)
    mcp.tool()(purge_deleted_tasks)

async def add_task(
    description: Annotated[str, Field(description="Task description")],
    project: Annotated[Optional[str], Field(description="Project name")] = None,
    priority: Annotated[Optional[str], Field(description="Priority: H (High), M (Medium), L (Low)")] = None,
    tags: Annotated[Optional[List[str]], Field(description="List of tags")] = None,
    due: Annotated[Optional[str], Field(description="Due date in ISO format (UTC), e.g., '2025-08-22T18:00:00Z'")] = None
) -> Dict[str, Any]:
    """Add a new task to Taskwarrior"""
    try:
        task = Task(tw, description=description)

        if project:
            task['project'] = project
        if priority:
            task['priority'] = priority
        if tags:
            task['tags'] = set(tags)
        if due:
            # Parse the due date and convert to local time for TaskWarrior storage
            due_dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
            # Convert UTC to local time for TaskWarrior
            local_due = due_dt.astimezone()
            task['due'] = local_due
        
        task.save()
        
        return {
            'success': True,
            'task': task_to_dict(task),
            'message': f"Task created with ID {task['id']}"
        }
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def list_tasks(
    status: Annotated[str, Field(description="Task status filter: pending, completed, deleted")] = "pending",
    project: Annotated[Optional[str], Field(description="Filter by project name")] = None,
    tags: Annotated[Optional[List[str]], Field(description="Filter by tags")] = None,
    limit: Annotated[Optional[int], Field(description="Maximum number of tasks to return")] = None
) -> Dict[str, Any]:
    """List tasks with optional filters"""
    try:
        # Build filter
        filters = {}
        if status:
            filters['status'] = status
        if project:
            filters['project'] = project

        # Get tasks
        tasks = tw.tasks.filter(**filters)

        # Apply tag filter if specified
        if tags:
            filtered_tasks = []
            for task in tasks:
                task_model = task_to_model(task)
                if any(tag in task_model.tags for tag in tags):
                    filtered_tasks.append(task)
            tasks = filtered_tasks

        # Convert to list and limit if needed
        task_list = []
        for i, task in enumerate(tasks):
            if limit and i >= limit:
                break
            task_list.append(task_to_dict(task))
        
        return {
            'success': True,
            'tasks': task_list,
            'count': len(task_list)
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def get_task(
    task_id: Annotated[Optional[int], Field(description="Task ID")] = None,
    uuid: Annotated[Optional[str], Field(description="Task UUID")] = None
) -> Dict[str, Any]:
    """Get details of a specific task by ID or UUID"""
    try:
        if not task_id and not uuid:
            return {
                'success': False,
                'error': "Either task_id or uuid must be provided"
            }

        if task_id:
            task = tw.tasks.get(id=task_id)
        else:
            task = tw.tasks.get(uuid=uuid)

        return {
            'success': True,
            'task': task_to_dict(task)
        }
    except Task.DoesNotExist:
        identifier = f"ID {task_id}" if task_id else f"UUID {uuid}"
        return {
            'success': False,
            'error': f"Task with {identifier} not found"
        }
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def complete_task(
    task_id: Annotated[Optional[int], Field(description="Task ID")] = None,
    uuid: Annotated[Optional[str], Field(description="Task UUID")] = None
) -> Dict[str, Any]:
    """Mark a task as completed"""
    try:
        if not task_id and not uuid:
            return {
                'success': False,
                'error': "Either task_id or uuid must be provided"
            }

        if task_id:
            task = tw.tasks.get(id=task_id)
        else:
            task = tw.tasks.get(uuid=uuid)

        task.done()
        identifier = task_id if task_id else uuid
        return {
            'success': True,
            'message': f"Task {identifier} marked as completed"
        }
    except Task.DoesNotExist:
        identifier = f"ID {task_id}" if task_id else f"UUID {uuid}"
        return {
            'success': False,
            'error': f"Task with {identifier} not found"
        }
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def uncomplete_task(
    task_id: Annotated[Optional[int], Field(description="Task ID")] = None,
    uuid: Annotated[Optional[str], Field(description="Task UUID")] = None
) -> Dict[str, Any]:
    """Mark a completed task as pending (uncomplete it)"""
    try:
        if not task_id and not uuid:
            return {
                'success': False,
                'error': "Either task_id or uuid must be provided"
            }

        # Find task by UUID or ID
        task = None

        # Try by UUID first (most reliable for completed tasks)
        if uuid:
            try:
                task = tw.tasks.get(uuid=uuid)
            except Task.DoesNotExist:
                pass

        # Try by ID if no UUID or UUID failed
        if not task and task_id:
            try:
                task = tw.tasks.get(id=task_id)
            except Task.DoesNotExist:
                pass

        if not task:
            identifier = uuid or f"ID {task_id}"
            return {
                'success': False,
                'error': f"Task with {identifier} not found"
            }

        # Check if task is actually completed
        if task['status'] != 'completed':
            identifier = uuid or f"ID {task_id}"
            return {
                'success': False,
                'error': f"Task {identifier} is not completed (current status: {task['status']})"
            }

        # Change status back to pending
        task['status'] = 'pending'
        task.save()

        identifier = uuid or f"ID {task_id}"
        return {
            'success': True,
            'message': f"Task {identifier} marked as pending",
            'task': task_to_dict(task)
        }
    except Exception as e:
        logger.error(f"Error uncompleting task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def modify_task(
    task_id: Annotated[int, Field(description="Task ID to modify")],
    description: Annotated[Optional[str], Field(description="New task description")] = None,
    project: Annotated[Optional[str], Field(description="New project name")] = None,
    priority: Annotated[Optional[str], Field(description="New priority (H/M/L)")] = None,
    tags: Annotated[Optional[List[str]], Field(description="New list of tags")] = None,
    due: Annotated[Optional[str], Field(description="New due date in ISO format (UTC), e.g., '2025-08-22T18:00:00Z'")] = None
) -> Dict[str, Any]:
    """Modify an existing task"""
    try:
        task = tw.tasks.get(id=task_id)

        if description:
            task['description'] = description
        if project is not None:
            task['project'] = project
        if priority is not None:
            task['priority'] = priority
        if tags is not None:
            task['tags'] = set(tags)
        if due is not None:
            if due:
                # Parse the due date and convert to local time for TaskWarrior storage
                due_dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
                # Convert UTC to local time for TaskWarrior
                local_due = due_dt.astimezone()
                task['due'] = local_due
            else:
                task['due'] = None

        task.save()

        return {
            'success': True,
            'task': task_to_dict(task),
            'message': f"Task {task_id} modified successfully"
        }
    except Task.DoesNotExist:
        return {
            'success': False,
            'error': f"Task with ID {params.task_id} not found"
        }
    except Exception as e:
        logger.error(f"Error modifying task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def delete_task(
    task_id: Annotated[Optional[int], Field(description="Task ID")] = None,
    uuid: Annotated[Optional[str], Field(description="Task UUID")] = None
) -> Dict[str, Any]:
    """Delete a task"""
    try:
        if not task_id and not uuid:
            return {
                'success': False,
                'error': "Either task_id or uuid must be provided"
            }

        if task_id:
            task = tw.tasks.get(id=task_id)
        else:
            task = tw.tasks.get(uuid=uuid)

        task.delete()
        identifier = task_id if task_id else uuid
        return {
            'success': True,
            'message': f"Task {identifier} deleted successfully"
        }
    except Task.DoesNotExist:
        return {
            'success': False,
            'error': f"Task with ID {params.task_id} not found"
        }
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def start_task(
    task_id: Annotated[Optional[int], Field(description="Task ID")] = None,
    uuid: Annotated[Optional[str], Field(description="Task UUID")] = None
) -> Dict[str, Any]:
    """Start working on a task (time tracking)"""
    try:
        if not task_id and not uuid:
            return {
                'success': False,
                'error': "Either task_id or uuid must be provided"
            }

        if task_id:
            task = tw.tasks.get(id=task_id)
        else:
            task = tw.tasks.get(uuid=uuid)

        task.start()
        identifier = task_id if task_id else uuid
        return {
            'success': True,
            'message': f"Started working on task {identifier}",
            'task': task_to_dict(task)
        }
    except Task.DoesNotExist:
        return {
            'success': False,
            'error': f"Task with ID {params.task_id} not found"
        }
    except Exception as e:
        logger.error(f"Error starting task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def stop_task(
    task_id: Annotated[Optional[int], Field(description="Task ID")] = None,
    uuid: Annotated[Optional[str], Field(description="Task UUID")] = None
) -> Dict[str, Any]:
    """Stop working on a task (time tracking)"""
    try:
        if not task_id and not uuid:
            return {
                'success': False,
                'error': "Either task_id or uuid must be provided"
            }

        if task_id:
            task = tw.tasks.get(id=task_id)
        else:
            task = tw.tasks.get(uuid=uuid)

        task.stop()
        identifier = task_id if task_id else uuid
        return {
            'success': True,
            'message': f"Stopped working on task {identifier}",
            'task': task_to_dict(task)
        }
    except Task.DoesNotExist:
        return {
            'success': False,
            'error': f"Task with ID {params.task_id} not found"
        }
    except Exception as e:
        logger.error(f"Error stopping task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def restore_task(
    task_id: Annotated[Optional[int], Field(description="ID of the deleted task to restore (may not exist for deleted tasks)")] = None,
    uuid: Annotated[Optional[str], Field(description="UUID of the deleted task to restore")] = None,
    status: Annotated[Optional[str], Field(description="Status to set for restored task (default: pending)")] = "pending"
) -> Dict[str, Any]:
    """Restore a deleted task back to active status"""
    try:
        if not task_id and not uuid:
            return {
                'success': False,
                'error': "Either task_id or uuid must be provided"
            }

        # Find the deleted task
        # Note: Deleted tasks may not have an ID, so we need to search more carefully
        deleted_tasks = list(tw.tasks.filter(status='deleted'))
        target_task = None

        # Try to find by UUID first (most reliable)
        if uuid:
            for task in deleted_tasks:
                try:
                    if task['uuid'] == uuid:
                        target_task = task
                        break
                except (KeyError, AttributeError):
                    pass

        # If not found by UUID and task_id provided, try to find by ID
        if not target_task and task_id:
            for task in deleted_tasks:
                try:
                    tid = task.get('id') if hasattr(task, 'get') else task['id']
                    if tid and tid == task_id:
                        target_task = task
                        break
                except (KeyError, AttributeError):
                    pass

        # If still not found and only task_id provided, use it as a hint
        # Get the most recently deleted task as a fallback
        if not target_task and task_id and deleted_tasks:
            # Sort by end time (deletion time) and get the most recent
            def get_sort_key(t):
                try:
                    if hasattr(t, 'get'):
                        return str(t.get('end') or t.get('modified') or '')
                    else:
                        return str(t['end'] if 'end' in t else (t['modified'] if 'modified' in t else ''))
                except:
                    return ''

            sorted_deleted = sorted(deleted_tasks, key=get_sort_key, reverse=True)
            if sorted_deleted:
                target_task = sorted_deleted[0]  # Get the most recently deleted

        if not target_task:
            return {
                'success': False,
                'error': f'No deleted tasks found to restore'
            }

        # Restore the task by modifying its status
        # Default to 'pending' if no status specified
        new_status = status or 'pending'
        
        # TaskWarrior doesn't allow direct status modification to 'pending' from 'deleted'
        # We need to use the 'modify' command with specific syntax
        import subprocess
        
        # Use task modify with the UUID to restore the task
        uuid_val = target_task['uuid']
        result = subprocess.run(
            ['task', uuid_val, 'modify', f'status:{new_status}'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # Refresh the task to get updated data
            restored_task = tw.tasks.get(uuid=uuid_val)
            return {
                'success': True,
                'message': f'Successfully restored task {task_id}',
                'task': task_to_dict(restored_task)
            }
        else:
            # Try alternative method: undelete command if available
            result = subprocess.run(
                ['task', str(task_id), 'undelete'],
                input='yes\n',
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                restored_task = tw.tasks.get(uuid=uuid_val)

                # If status needs to be something other than pending, modify it
                if new_status != 'pending':
                    restored_task['status'] = new_status
                    restored_task.save()

                return {
                    'success': True,
                    'message': f'Successfully restored task {task_id} with status {new_status}',
                    'task': task_to_dict(restored_task)
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to restore task: {result.stderr}'
                }
            
    except Exception as e:
        logger.error(f"Error restoring task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def purge_deleted_tasks() -> Dict[str, Any]:
    """Permanently remove all deleted tasks from the database"""
    try:
        # Get deleted tasks before purging to report count
        deleted_tasks = list(tw.tasks.filter(status='deleted'))
        deleted_count = len(deleted_tasks)
        
        if deleted_count == 0:
            return {
                'success': True,
                'message': 'No deleted tasks to purge',
                'purged_count': 0
            }
        
        # Execute purge command
        # Note: TaskWarrior's purge operation removes all deleted tasks permanently
        # Requires two confirmations: "yes" for modifying all tasks, "all" for purging all deleted tasks
        import subprocess
        result = subprocess.run(['task', 'purge'], 
                              input='yes\nall\n',  # Confirm: yes to modify all tasks, all to purge all deleted
                              capture_output=True, 
                              text=True,
                              timeout=30)
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'Successfully purged {deleted_count} deleted tasks',
                'purged_count': deleted_count,
                'details': 'Deleted tasks have been permanently removed from the database'
            }
        else:
            return {
                'success': False,
                'error': f'Purge command failed: {result.stderr}',
                'found_deleted_count': deleted_count
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Purge operation timed out after 30 seconds'
        }
    except Exception as e:
        logger.error(f"Error purging deleted tasks: {e}")
        return {
            'success': False,
            'error': str(e)
        }