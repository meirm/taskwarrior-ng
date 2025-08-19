"""
Basic task operations: add, list, get, complete, modify, delete, start, stop
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastmcp import FastMCP
from tasklib import Task

from utils.taskwarrior import tw, task_to_dict, task_to_model
from utils.models import AddTaskParams, ListTasksParams, TaskIdParam, ModifyTaskParams, RestoreTaskParams

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

async def add_task(params: AddTaskParams) -> Dict[str, Any]:
    """Add a new task to Taskwarrior"""
    try:
        task = Task(tw, description=params.description)
        
        if params.project:
            task['project'] = params.project
        if params.priority:
            task['priority'] = params.priority
        if params.tags:
            task['tags'] = set(params.tags)
        if params.due:
            # Parse the due date and convert to local time for TaskWarrior storage
            due_dt = datetime.fromisoformat(params.due.replace('Z', '+00:00'))
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

async def list_tasks(params: ListTasksParams) -> Dict[str, Any]:
    """List tasks with optional filters"""
    try:
        # Build filter
        filters = {}
        if params.status:
            filters['status'] = params.status
        if params.project:
            filters['project'] = params.project
        
        # Get tasks
        tasks = tw.tasks.filter(**filters)
        
        # Apply tag filter if specified
        if params.tags:
            filtered_tasks = []
            for task in tasks:
                task_model = task_to_model(task)
                if any(tag in task_model.tags for tag in params.tags):
                    filtered_tasks.append(task)
            tasks = filtered_tasks
        
        # Convert to list and limit if needed
        task_list = []
        for i, task in enumerate(tasks):
            if params.limit and i >= params.limit:
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

async def get_task(params: TaskIdParam) -> Dict[str, Any]:
    """Get details of a specific task by ID"""
    try:
        task = tw.tasks.get(id=params.task_id)
        return {
            'success': True,
            'task': task_to_dict(task)
        }
    except Task.DoesNotExist:
        return {
            'success': False,
            'error': f"Task with ID {params.task_id} not found"
        }
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def complete_task(params: TaskIdParam) -> Dict[str, Any]:
    """Mark a task as completed"""
    try:
        task = tw.tasks.get(id=params.task_id)
        task.done()
        return {
            'success': True,
            'message': f"Task {params.task_id} marked as completed"
        }
    except Task.DoesNotExist:
        return {
            'success': False,
            'error': f"Task with ID {params.task_id} not found"
        }
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def uncomplete_task(params: TaskIdParam) -> Dict[str, Any]:
    """Mark a completed task as pending (uncomplete it)"""
    try:
        # Find task by UUID or ID
        task = None
        
        # Try by UUID first (most reliable for completed tasks)
        if params.uuid:
            try:
                task = tw.tasks.get(uuid=params.uuid)
            except Task.DoesNotExist:
                pass
        
        # Try by ID if no UUID or UUID failed
        if not task and params.task_id:
            try:
                task = tw.tasks.get(id=params.task_id)
            except Task.DoesNotExist:
                pass
        
        if not task:
            identifier = params.uuid or f"ID {params.task_id}"
            return {
                'success': False,
                'error': f"Task with {identifier} not found"
            }
        
        # Check if task is actually completed
        if task['status'] != 'completed':
            identifier = params.uuid or f"ID {params.task_id}"
            return {
                'success': False,
                'error': f"Task {identifier} is not completed (current status: {task['status']})"
            }
        
        # Change status back to pending
        task['status'] = 'pending'
        task.save()
        
        identifier = params.uuid or f"ID {params.task_id}"
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

async def modify_task(params: ModifyTaskParams) -> Dict[str, Any]:
    """Modify an existing task"""
    try:
        task = tw.tasks.get(id=params.task_id)
        
        if params.description:
            task['description'] = params.description
        if params.project is not None:
            task['project'] = params.project
        if params.priority is not None:
            task['priority'] = params.priority
        if params.tags is not None:
            task['tags'] = set(params.tags)
        if params.due is not None:
            if params.due:
                # Parse the due date and convert to local time for TaskWarrior storage
                due_dt = datetime.fromisoformat(params.due.replace('Z', '+00:00'))
                # Convert UTC to local time for TaskWarrior
                local_due = due_dt.astimezone()
                task['due'] = local_due
            else:
                task['due'] = None
        
        task.save()
        
        return {
            'success': True,
            'task': task_to_dict(task),
            'message': f"Task {params.task_id} modified successfully"
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

async def delete_task(params: TaskIdParam) -> Dict[str, Any]:
    """Delete a task"""
    try:
        task = tw.tasks.get(id=params.task_id)
        task.delete()
        return {
            'success': True,
            'message': f"Task {params.task_id} deleted successfully"
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

async def start_task(params: TaskIdParam) -> Dict[str, Any]:
    """Start working on a task (time tracking)"""
    try:
        task = tw.tasks.get(id=params.task_id)
        task.start()
        return {
            'success': True,
            'message': f"Started working on task {params.task_id}",
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

async def stop_task(params: TaskIdParam) -> Dict[str, Any]:
    """Stop working on a task (time tracking)"""
    try:
        task = tw.tasks.get(id=params.task_id)
        task.stop()
        return {
            'success': True,
            'message': f"Stopped working on task {params.task_id}",
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

async def restore_task(params: RestoreTaskParams) -> Dict[str, Any]:
    """Restore a deleted task back to active status"""
    try:
        # Find the deleted task
        # Note: Deleted tasks may not have an ID, so we need to search more carefully
        deleted_tasks = list(tw.tasks.filter(status='deleted'))
        target_task = None
        
        # Try to find by UUID first (most reliable)
        if params.uuid:
            for task in deleted_tasks:
                try:
                    if task['uuid'] == params.uuid:
                        target_task = task
                        break
                except (KeyError, AttributeError):
                    pass
        
        # If not found by UUID and task_id provided, try to find by ID
        if not target_task and params.task_id:
            for task in deleted_tasks:
                try:
                    task_id = task.get('id') if hasattr(task, 'get') else task['id']
                    if task_id and task_id == params.task_id:
                        target_task = task
                        break
                except (KeyError, AttributeError):
                    pass
        
        # If still not found and only task_id provided, use it as a hint
        # Get the most recently deleted task as a fallback
        if not target_task and params.task_id and deleted_tasks:
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
        new_status = params.status or 'pending'
        
        # TaskWarrior doesn't allow direct status modification to 'pending' from 'deleted'
        # We need to use the 'modify' command with specific syntax
        import subprocess
        
        # Use task modify with the UUID to restore the task
        uuid = target_task['uuid']
        result = subprocess.run(
            ['task', uuid, 'modify', f'status:{new_status}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Refresh the task to get updated data
            restored_task = tw.tasks.get(uuid=uuid)
            return {
                'success': True,
                'message': f'Successfully restored task {params.task_id}',
                'task': task_to_dict(restored_task)
            }
        else:
            # Try alternative method: undelete command if available
            result = subprocess.run(
                ['task', str(params.task_id), 'undelete'],
                input='yes\n',
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                restored_task = tw.tasks.get(uuid=uuid)
                
                # If status needs to be something other than pending, modify it
                if new_status != 'pending':
                    restored_task['status'] = new_status
                    restored_task.save()
                
                return {
                    'success': True,
                    'message': f'Successfully restored task {params.task_id} with status {new_status}',
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