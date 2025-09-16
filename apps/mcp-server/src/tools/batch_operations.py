"""
Batch operations: complete, delete, modify multiple tasks at once
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Annotated

from fastmcp import FastMCP
from pydantic import Field
from tasklib import Task

from utils.taskwarrior import tw, task_to_dict, task_to_model
from utils.filters import filter_tasks

logger = logging.getLogger("taskwarrior-mcp.tools.batch")

# Get the MCP instance - this will be injected by the server
mcp: FastMCP = None

def init_tools(mcp_instance: FastMCP):
    """Initialize tools with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register all batch operation tools with the MCP instance
    mcp.tool()(batch_complete_by_ids)
    mcp.tool()(batch_complete_by_filter)
    mcp.tool()(batch_uncomplete_by_ids)
    mcp.tool()(batch_uncomplete_by_filter)
    mcp.tool()(batch_delete_by_ids)
    mcp.tool()(batch_delete_by_filter)
    mcp.tool()(batch_start_by_ids)
    mcp.tool()(batch_stop_by_ids)
    mcp.tool()(batch_modify_tasks)

async def batch_complete_by_ids(
    task_ids: Annotated[List[int], Field(description="List of task IDs to operate on")],
    task_uuids: Annotated[Optional[Dict[int, str]], Field(description="Optional mapping of task IDs to UUIDs for better reliability")] = None
) -> Dict[str, Any]:
    """Complete multiple tasks by their IDs"""
    try:
        results = []
        errors = []

        for task_id in task_ids:
            try:
                task = tw.tasks.get(id=task_id)
                task.done()
                results.append({
                    'task_id': task_id,
                    'success': True,
                    'message': f'Task {task_id} completed'
                })
            except Task.DoesNotExist:
                errors.append(f'Task {task_id} not found')
            except Exception as e:
                errors.append(f'Error completing task {task_id}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'completed_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch complete by IDs: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_complete_by_filter(
    status: Annotated[Optional[str], Field(description="Filter by status: pending, completed, deleted")] = None,
    project: Annotated[Optional[str], Field(description="Filter by project name")] = None,
    tags: Annotated[Optional[List[str]], Field(description="Filter by tags (tasks with ANY of these tags)")] = None,
    priority: Annotated[Optional[str], Field(description="Filter by priority: H, M, L")] = None,
    description_contains: Annotated[Optional[str], Field(description="Filter by description containing text")] = None,
    due_before: Annotated[Optional[str], Field(description="Filter by due date before this date (ISO format)")] = None,
    due_after: Annotated[Optional[str], Field(description="Filter by due date after this date (ISO format)")] = None,
    limit: Annotated[Optional[int], Field(description="Maximum number of tasks to operate on")] = None
) -> Dict[str, Any]:
    """Complete multiple tasks matching filter criteria"""
    try:
        # Create params object for filter_tasks
        class FilterParams:
            def __init__(self):
                self.status = status
                self.project = project
                self.tags = tags
                self.priority = priority
                self.description_contains = description_contains
                self.due_before = due_before
                self.due_after = due_after
                self.limit = limit

        params = FilterParams()
        tasks = filter_tasks(params)
        results = []
        errors = []
        
        for task in tasks:
            try:
                task.done()
                results.append({
                    'task_id': task['id'],
                    'success': True,
                    'message': f'Task {task["id"]} completed'
                })
            except Exception as e:
                errors.append(f'Error completing task {task["id"]}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'completed_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch complete by filter: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_uncomplete_by_ids(
    task_ids: Annotated[List[int], Field(description="List of task IDs to operate on")],
    task_uuids: Annotated[Optional[Dict[int, str]], Field(description="Optional mapping of task IDs to UUIDs for better reliability")] = None
) -> Dict[str, Any]:
    """Uncomplete multiple tasks by their IDs (mark them as pending)"""
    try:
        results = []
        errors = []

        for task_id in task_ids:
            try:
                task = None

                # Try to find by UUID first if provided
                if task_uuids and str(task_id) in task_uuids:
                    uuid = task_uuids[str(task_id)]
                    try:
                        task = tw.tasks.get(uuid=uuid)
                    except Task.DoesNotExist:
                        pass
                
                # Fall back to ID if UUID not found or not provided
                if not task:
                    try:
                        task = tw.tasks.get(id=task_id)
                    except Task.DoesNotExist:
                        pass
                
                if not task:
                    errors.append(f'Task {task_id} not found')
                    continue
                
                # Check if task is actually completed
                if task['status'] != 'completed':
                    errors.append(f'Task {task_id} is not completed (current status: {task["status"]})')
                    continue
                
                # Change status back to pending
                task['status'] = 'pending'
                task.save()
                
                results.append({
                    'task_id': task_id,
                    'success': True,
                    'message': f'Task {task_id} marked as pending'
                })
            except Exception as e:
                errors.append(f'Error uncompleting task {task_id}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'uncompleted_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch uncomplete by IDs: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_uncomplete_by_filter(
    status: Annotated[Optional[str], Field(description="Filter by status: pending, completed, deleted")] = None,
    project: Annotated[Optional[str], Field(description="Filter by project name")] = None,
    tags: Annotated[Optional[List[str]], Field(description="Filter by tags (tasks with ANY of these tags)")] = None,
    priority: Annotated[Optional[str], Field(description="Filter by priority: H, M, L")] = None,
    description_contains: Annotated[Optional[str], Field(description="Filter by description containing text")] = None,
    due_before: Annotated[Optional[str], Field(description="Filter by due date before this date (ISO format)")] = None,
    due_after: Annotated[Optional[str], Field(description="Filter by due date after this date (ISO format)")] = None,
    limit: Annotated[Optional[int], Field(description="Maximum number of tasks to operate on")] = None
) -> Dict[str, Any]:
    """Uncomplete multiple tasks matching filter criteria (mark them as pending)"""
    try:
        # Create params object for filter_tasks
        class FilterParams:
            def __init__(self):
                self.status = status
                self.project = project
                self.tags = tags
                self.priority = priority
                self.description_contains = description_contains
                self.due_before = due_before
                self.due_after = due_after
                self.limit = limit

        params = FilterParams()
        tasks = filter_tasks(params)
        results = []
        errors = []
        
        for task in tasks:
            try:
                # Check if task is actually completed
                if task['status'] != 'completed':
                    errors.append(f'Task {task["id"]} is not completed (current status: {task["status"]})')
                    continue
                
                # Change status back to pending
                task['status'] = 'pending'
                task.save()
                
                results.append({
                    'task_id': task['id'],
                    'success': True,
                    'message': f'Task {task["id"]} marked as pending'
                })
            except Exception as e:
                errors.append(f'Error uncompleting task {task["id"]}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'uncompleted_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch uncomplete by filter: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_delete_by_ids(
    task_ids: Annotated[List[int], Field(description="List of task IDs to operate on")],
    task_uuids: Annotated[Optional[Dict[int, str]], Field(description="Optional mapping of task IDs to UUIDs for better reliability")] = None
) -> Dict[str, Any]:
    """Delete multiple tasks by their IDs"""
    try:
        results = []
        errors = []

        for task_id in task_ids:
            try:
                task = tw.tasks.get(id=task_id)
                task.delete()
                results.append({
                    'task_id': task_id,
                    'success': True,
                    'message': f'Task {task_id} deleted'
                })
            except Task.DoesNotExist:
                errors.append(f'Task {task_id} not found')
            except Exception as e:
                errors.append(f'Error deleting task {task_id}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'deleted_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch delete by IDs: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_delete_by_filter(
    status: Annotated[Optional[str], Field(description="Filter by status: pending, completed, deleted")] = None,
    project: Annotated[Optional[str], Field(description="Filter by project name")] = None,
    tags: Annotated[Optional[List[str]], Field(description="Filter by tags (tasks with ANY of these tags)")] = None,
    priority: Annotated[Optional[str], Field(description="Filter by priority: H, M, L")] = None,
    description_contains: Annotated[Optional[str], Field(description="Filter by description containing text")] = None,
    due_before: Annotated[Optional[str], Field(description="Filter by due date before this date (ISO format)")] = None,
    due_after: Annotated[Optional[str], Field(description="Filter by due date after this date (ISO format)")] = None,
    limit: Annotated[Optional[int], Field(description="Maximum number of tasks to operate on")] = None
) -> Dict[str, Any]:
    """Delete multiple tasks matching filter criteria"""
    try:
        # Create params object for filter_tasks
        class FilterParams:
            def __init__(self):
                self.status = status
                self.project = project
                self.tags = tags
                self.priority = priority
                self.description_contains = description_contains
                self.due_before = due_before
                self.due_after = due_after
                self.limit = limit

        params = FilterParams()
        tasks = filter_tasks(params)
        results = []
        errors = []
        
        for task in tasks:
            try:
                task.delete()
                results.append({
                    'task_id': task['id'],
                    'success': True,
                    'message': f'Task {task["id"]} deleted'
                })
            except Exception as e:
                errors.append(f'Error deleting task {task["id"]}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'deleted_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch delete by filter: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_start_by_ids(
    task_ids: Annotated[List[int], Field(description="List of task IDs to operate on")],
    task_uuids: Annotated[Optional[Dict[int, str]], Field(description="Optional mapping of task IDs to UUIDs for better reliability")] = None
) -> Dict[str, Any]:
    """Start time tracking on multiple tasks by their IDs"""
    try:
        results = []
        errors = []

        for task_id in task_ids:
            try:
                task = tw.tasks.get(id=task_id)
                task.start()
                results.append({
                    'task_id': task_id,
                    'success': True,
                    'message': f'Task {task_id} started'
                })
            except Task.DoesNotExist:
                errors.append(f'Task {task_id} not found')
            except Exception as e:
                errors.append(f'Error starting task {task_id}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'started_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch start by IDs: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_stop_by_ids(
    task_ids: Annotated[List[int], Field(description="List of task IDs to operate on")],
    task_uuids: Annotated[Optional[Dict[int, str]], Field(description="Optional mapping of task IDs to UUIDs for better reliability")] = None
) -> Dict[str, Any]:
    """Stop time tracking on multiple tasks by their IDs"""
    try:
        results = []
        errors = []

        for task_id in task_ids:
            try:
                task = tw.tasks.get(id=task_id)
                task.stop()
                results.append({
                    'task_id': task_id,
                    'success': True,
                    'message': f'Task {task_id} stopped'
                })
            except Task.DoesNotExist:
                errors.append(f'Task {task_id} not found')
            except Exception as e:
                errors.append(f'Error stopping task {task_id}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'stopped_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch stop by IDs: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def batch_modify_tasks(
    # Either provide specific task IDs or filter criteria
    task_ids: Annotated[Optional[List[int]], Field(description="Specific task IDs to modify")] = None,
    # Filter criteria to select tasks
    status: Annotated[Optional[str], Field(description="Filter by status: pending, completed, deleted")] = None,
    filter_project: Annotated[Optional[str], Field(description="Filter by project name")] = None,
    filter_tags: Annotated[Optional[List[str]], Field(description="Filter by tags (tasks with ANY of these tags)")] = None,
    filter_priority: Annotated[Optional[str], Field(description="Filter by priority: H, M, L")] = None,
    filter_description_contains: Annotated[Optional[str], Field(description="Filter by description containing text")] = None,
    filter_due_before: Annotated[Optional[str], Field(description="Filter by due date before this date (ISO format)")] = None,
    filter_due_after: Annotated[Optional[str], Field(description="Filter by due date after this date (ISO format)")] = None,
    filter_limit: Annotated[Optional[int], Field(description="Maximum number of tasks to operate on")] = None,
    # Fields to update
    project: Annotated[Optional[str], Field(description="Set project for all selected tasks")] = None,
    priority: Annotated[Optional[str], Field(description="Set priority for all selected tasks")] = None,
    add_tags: Annotated[Optional[List[str]], Field(description="Tags to add to all selected tasks")] = None,
    remove_tags: Annotated[Optional[List[str]], Field(description="Tags to remove from all selected tasks")] = None,
    due: Annotated[Optional[str], Field(description="Set due date for all selected tasks")] = None
) -> Dict[str, Any]:
    """Modify multiple tasks at once using either IDs or filter criteria"""
    try:
        # Get tasks to modify
        if task_ids:
            tasks = []
            for task_id in task_ids:
                try:
                    task = tw.tasks.get(id=task_id)
                    tasks.append(task)
                except Task.DoesNotExist:
                    continue
        elif any([status, filter_project, filter_tags, filter_priority, filter_description_contains,
                  filter_due_before, filter_due_after, filter_limit]):
            # Create params object for filter_tasks
            class FilterParams:
                def __init__(self):
                    self.status = status
                    self.project = filter_project
                    self.tags = filter_tags
                    self.priority = filter_priority
                    self.description_contains = filter_description_contains
                    self.due_before = filter_due_before
                    self.due_after = filter_due_after
                    self.limit = filter_limit

            filters = FilterParams()
            tasks = filter_tasks(filters)
        else:
            return {
                'success': False,
                'error': 'Either task_ids or filters must be provided'
            }

        results = []
        errors = []

        for task in tasks:
            try:
                # Apply modifications
                if project is not None:
                    task['project'] = project

                if priority is not None:
                    task['priority'] = priority

                if add_tags:
                    task_model = task_to_model(task)
                    current_tags = set(task_model.tags)
                    current_tags.update(add_tags)
                    task['tags'] = current_tags

                if remove_tags:
                    task_model = task_to_model(task)
                    current_tags = set(task_model.tags)
                    current_tags -= set(remove_tags)
                    task['tags'] = current_tags
                
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
                results.append({
                    'task_id': task['id'],
                    'success': True,
                    'message': f'Task {task["id"]} modified',
                    'task': task_to_dict(task)
                })
            except Exception as e:
                errors.append(f'Error modifying task {task["id"]}: {str(e)}')
        
        return {
            'success': len(errors) == 0,
            'modified_count': len(results),
            'results': results,
            'errors': errors
        }
    except Exception as e:
        logger.error(f"Error in batch modify tasks: {e}")
        return {
            'success': False,
            'error': str(e)
        }