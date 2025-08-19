"""
Batch operations: complete, delete, modify multiple tasks at once
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

from fastmcp import FastMCP
from tasklib import Task

from utils.taskwarrior import tw, task_to_dict, task_to_model
from utils.models import BatchTaskIdsParams, BatchFilterParams, BatchModifyParams
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

async def batch_complete_by_ids(params: BatchTaskIdsParams) -> Dict[str, Any]:
    """Complete multiple tasks by their IDs"""
    try:
        results = []
        errors = []
        
        for task_id in params.task_ids:
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

async def batch_complete_by_filter(params: BatchFilterParams) -> Dict[str, Any]:
    """Complete multiple tasks matching filter criteria"""
    try:
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

async def batch_uncomplete_by_ids(params: BatchTaskIdsParams) -> Dict[str, Any]:
    """Uncomplete multiple tasks by their IDs (mark them as pending)"""
    try:
        results = []
        errors = []
        
        for task_id in params.task_ids:
            try:
                task = None
                
                # Try to find by UUID first if provided
                if params.task_uuids and str(task_id) in params.task_uuids:
                    uuid = params.task_uuids[str(task_id)]
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

async def batch_uncomplete_by_filter(params: BatchFilterParams) -> Dict[str, Any]:
    """Uncomplete multiple tasks matching filter criteria (mark them as pending)"""
    try:
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

async def batch_delete_by_ids(params: BatchTaskIdsParams) -> Dict[str, Any]:
    """Delete multiple tasks by their IDs"""
    try:
        results = []
        errors = []
        
        for task_id in params.task_ids:
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

async def batch_delete_by_filter(params: BatchFilterParams) -> Dict[str, Any]:
    """Delete multiple tasks matching filter criteria"""
    try:
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

async def batch_start_by_ids(params: BatchTaskIdsParams) -> Dict[str, Any]:
    """Start time tracking on multiple tasks by their IDs"""
    try:
        results = []
        errors = []
        
        for task_id in params.task_ids:
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

async def batch_stop_by_ids(params: BatchTaskIdsParams) -> Dict[str, Any]:
    """Stop time tracking on multiple tasks by their IDs"""
    try:
        results = []
        errors = []
        
        for task_id in params.task_ids:
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

async def batch_modify_tasks(params: BatchModifyParams) -> Dict[str, Any]:
    """Modify multiple tasks at once using either IDs or filter criteria"""
    try:
        # Get tasks to modify
        if params.task_ids:
            tasks = []
            for task_id in params.task_ids:
                try:
                    task = tw.tasks.get(id=task_id)
                    tasks.append(task)
                except Task.DoesNotExist:
                    continue
        elif params.filters:
            tasks = filter_tasks(params.filters)
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
                if params.project is not None:
                    task['project'] = params.project
                
                if params.priority is not None:
                    task['priority'] = params.priority
                
                if params.add_tags:
                    task_model = task_to_model(task)
                    current_tags = set(task_model.tags)
                    current_tags.update(params.add_tags)
                    task['tags'] = current_tags
                
                if params.remove_tags:
                    task_model = task_to_model(task)
                    current_tags = set(task_model.tags)
                    current_tags -= set(params.remove_tags)
                    task['tags'] = current_tags
                
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