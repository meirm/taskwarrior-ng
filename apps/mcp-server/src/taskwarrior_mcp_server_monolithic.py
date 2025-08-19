#!/usr/bin/env python3
"""
Taskwarrior MCP Server using FastMCP - Version 2

An MCP server that provides access to Taskwarrior functionality through the tasklib library.
Fixed version that properly handles FastMCP resource and prompt expectations.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

try:
    from tasklib import TaskWarrior, Task
except ImportError:
    raise ImportError("tasklib is required. Install with: pip install tasklib")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskwarrior-mcp")

# Initialize FastMCP server
mcp = FastMCP("taskwarrior-mcp", dependencies=["tasklib>=2.5.1"])

# Initialize TaskWarrior connection
try:
    tw = TaskWarrior()
    logger.info("Connected to Taskwarrior successfully")
except Exception as e:
    logger.error(f"Failed to connect to Taskwarrior: {e}")
    raise

def task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert a Task object to a dictionary with UTC timestamps"""
    
    def safe_get(field):
        """Safely get a field from a Task object"""
        try:
            return task[field]
        except KeyError:
            return None
    
    def to_utc_iso(dt):
        """Convert datetime to UTC ISO format"""
        if dt is None:
            return None
        # If datetime is naive (no timezone), assume it's in local time
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Convert to UTC
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt.isoformat().replace('+00:00', 'Z')
    
    task_dict = {
        'id': safe_get('id'),
        'uuid': safe_get('uuid'),
        'description': safe_get('description') or '',
        'status': safe_get('status') or 'pending',
        'project': safe_get('project'),
        'priority': safe_get('priority'),
        'tags': list(safe_get('tags')) if safe_get('tags') else [],
        'due': to_utc_iso(safe_get('due')),
        'urgency': safe_get('urgency') or 0,
        'entry': to_utc_iso(safe_get('entry')),
        'modified': to_utc_iso(safe_get('modified')),
    }
    
    # Add optional fields if they exist with UTC conversion
    annotations = safe_get('annotations')
    if annotations:
        task_dict['annotations'] = [
            {
                'entry': to_utc_iso(ann['entry']) if isinstance(ann['entry'], datetime) else ann['entry'],
                'description': ann['description']
            }
            for ann in annotations
        ]
    
    depends = safe_get('depends')
    if depends:
        task_dict['depends'] = list(depends)
    
    start = safe_get('start')
    if start:
        task_dict['start'] = to_utc_iso(start)
    
    end = safe_get('end')
    if end:
        task_dict['end'] = to_utc_iso(end)
    
    wait = safe_get('wait')
    if wait:
        task_dict['wait'] = to_utc_iso(wait)
    
    until = safe_get('until')
    if until:
        task_dict['until'] = to_utc_iso(until)
    
    recur = safe_get('recur')
    if recur:
        task_dict['recur'] = recur
    
    return task_dict

# Define Pydantic models for better type safety
class AddTaskParams(BaseModel):
    description: str = Field(..., description="Task description")
    project: Optional[str] = Field(None, description="Project name")
    priority: Optional[str] = Field(None, description="Priority: H (High), M (Medium), L (Low)")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    due: Optional[str] = Field(None, description="Due date in ISO format (UTC), e.g., '2025-08-22T18:00:00Z'")

class ListTasksParams(BaseModel):
    status: str = Field("pending", description="Task status filter: pending, completed, deleted")
    project: Optional[str] = Field(None, description="Filter by project name")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: Optional[int] = Field(None, description="Maximum number of tasks to return")

class TaskIdParam(BaseModel):
    task_id: int = Field(..., description="Task ID")

class ModifyTaskParams(BaseModel):
    task_id: int = Field(..., description="Task ID to modify")
    description: Optional[str] = Field(None, description="New task description")
    project: Optional[str] = Field(None, description="New project name")
    priority: Optional[str] = Field(None, description="New priority (H/M/L)")
    tags: Optional[List[str]] = Field(None, description="New list of tags")
    due: Optional[str] = Field(None, description="New due date in ISO format (UTC), e.g., '2025-08-22T18:00:00Z'")

class BatchTaskIdsParams(BaseModel):
    task_ids: List[int] = Field(..., description="List of task IDs to operate on")

class BatchFilterParams(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status: pending, completed, deleted")
    project: Optional[str] = Field(None, description="Filter by project name")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (tasks with ANY of these tags)")
    priority: Optional[str] = Field(None, description="Filter by priority: H, M, L")
    description_contains: Optional[str] = Field(None, description="Filter by description containing text")
    due_before: Optional[str] = Field(None, description="Filter by due date before this date (ISO format)")
    due_after: Optional[str] = Field(None, description="Filter by due date after this date (ISO format)")
    limit: Optional[int] = Field(None, description="Maximum number of tasks to operate on")

class BatchModifyParams(BaseModel):
    # Either provide specific task IDs or filter criteria
    task_ids: Optional[List[int]] = Field(None, description="Specific task IDs to modify")
    filters: Optional[BatchFilterParams] = Field(None, description="Filter criteria to select tasks")
    # Fields to update
    project: Optional[str] = Field(None, description="Set project for all selected tasks")
    priority: Optional[str] = Field(None, description="Set priority for all selected tasks")
    add_tags: Optional[List[str]] = Field(None, description="Tags to add to all selected tasks")
    remove_tags: Optional[List[str]] = Field(None, description="Tags to remove from all selected tasks")
    due: Optional[str] = Field(None, description="Set due date for all selected tasks")

# Helper functions for batch operations
def safe_get_task_field(task: Task, field: str):
    """Safely get a field from a Task object"""
    try:
        return task[field]
    except KeyError:
        return None

def filter_tasks(filters: BatchFilterParams) -> List[Task]:
    """Filter tasks based on criteria"""
    
    # Start with all tasks or filter by status
    if filters.status:
        if filters.status == 'pending':
            tasks = tw.tasks.pending()
        elif filters.status == 'completed':
            tasks = tw.tasks.completed()
        elif filters.status == 'deleted':
            tasks = tw.tasks.filter(status='deleted')
        else:
            tasks = tw.tasks.filter(status=filters.status)
    else:
        tasks = tw.tasks.all()
    
    filtered_tasks = []
    
    for task in tasks:
        # Apply filters
        matches = True
        
        # Project filter
        if filters.project:
            task_project = safe_get_task_field(task, 'project')
            if task_project != filters.project:
                matches = False
        
        # Priority filter
        if filters.priority:
            task_priority = safe_get_task_field(task, 'priority')
            if task_priority != filters.priority:
                matches = False
        
        # Tags filter (task must have ANY of the specified tags)
        if filters.tags:
            task_tags = safe_get_task_field(task, 'tags')
            if not task_tags or not any(tag in task_tags for tag in filters.tags):
                matches = False
        
        # Description contains filter
        if filters.description_contains:
            task_desc = safe_get_task_field(task, 'description')
            if not task_desc or filters.description_contains.lower() not in task_desc.lower():
                matches = False
        
        # Due date filters
        task_due = safe_get_task_field(task, 'due')
        if filters.due_before and task_due:
            due_before = datetime.fromisoformat(filters.due_before.replace('Z', '+00:00'))
            if task_due >= due_before:
                matches = False
        
        if filters.due_after and task_due:
            due_after = datetime.fromisoformat(filters.due_after.replace('Z', '+00:00'))
            if task_due <= due_after:
                matches = False
        
        if matches:
            filtered_tasks.append(task)
    
    # Apply limit
    if filters.limit and len(filtered_tasks) > filters.limit:
        filtered_tasks = filtered_tasks[:filters.limit]
    
    return filtered_tasks

# Tool definitions
@mcp.tool()
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

@mcp.tool()
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
            tasks = [t for t in tasks if any(tag in t.get('tags', []) for tag in params.tags)]
        
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
async def get_projects() -> Dict[str, Any]:
    """Get all unique project names"""
    try:
        projects = set()
        for task in tw.tasks.all():
            if 'project' in task and task['project']:
                projects.add(task['project'])
        
        return {
            'success': True,
            'projects': sorted(list(projects)),
            'count': len(projects)
        }
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@mcp.tool()
async def get_tags() -> Dict[str, Any]:
    """Get all unique tags"""
    try:
        tags = set()
        for task in tw.tasks.all():
            if 'tags' in task and task['tags']:
                tags.update(task['tags'])
        
        return {
            'success': True,
            'tags': sorted(list(tags)),
            'count': len(tags)
        }
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@mcp.tool()
async def get_summary() -> Dict[str, Any]:
    """Get task summary statistics"""
    try:
        pending = tw.tasks.pending()
        completed = tw.tasks.completed()
        
        # Count by status
        status_counts = {
            'pending': len(pending),
            'completed': len(completed),
            'total': len(tw.tasks.all())
        }
        
        # Count by priority for pending tasks
        priority_counts = {'H': 0, 'M': 0, 'L': 0, 'None': 0}
        for task in pending:
            priority = task.get('priority', None)
            if priority in priority_counts:
                priority_counts[priority] += 1
            else:
                priority_counts['None'] += 1
        
        # Count overdue tasks
        now = datetime.now()
        overdue = 0
        for task in pending:
            if 'due' in task and task['due'] and task['due'] < now:
                overdue += 1
        
        return {
            'success': True,
            'summary': {
                'status': status_counts,
                'priority': priority_counts,
                'overdue': overdue
            }
        }
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Batch operation tools
@mcp.tool()
async def batch_complete_tasks(params: BatchTaskIdsParams) -> Dict[str, Any]:
    """Mark multiple tasks as completed by their IDs"""
    try:
        completed_tasks = []
        failed_tasks = []
        
        for task_id in params.task_ids:
            try:
                task = tw.tasks.get(id=task_id)
                task.done()
                completed_tasks.append({
                    'id': task_id,
                    'description': safe_get_task_field(task, 'description')
                })
            except Task.DoesNotExist:
                failed_tasks.append({'id': task_id, 'error': 'Task not found'})
            except Exception as e:
                failed_tasks.append({'id': task_id, 'error': str(e)})
        
        return {
            'success': True,
            'completed': completed_tasks,
            'failed': failed_tasks,
            'completed_count': len(completed_tasks),
            'failed_count': len(failed_tasks),
            'message': f"Completed {len(completed_tasks)} tasks, {len(failed_tasks)} failed"
        }
    except Exception as e:
        logger.error(f"Error in batch complete: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@mcp.tool()
async def batch_delete_tasks(params: BatchTaskIdsParams) -> Dict[str, Any]:
    """Delete multiple tasks by their IDs"""
    try:
        deleted_tasks = []
        failed_tasks = []
        
        for task_id in params.task_ids:
            try:
                task = tw.tasks.get(id=task_id)
                task_info = {
                    'id': task_id,
                    'description': safe_get_task_field(task, 'description')
                }
                task.delete()
                deleted_tasks.append(task_info)
            except Task.DoesNotExist:
                failed_tasks.append({'id': task_id, 'error': 'Task not found'})
            except Exception as e:
                failed_tasks.append({'id': task_id, 'error': str(e)})
        
        return {
            'success': True,
            'deleted': deleted_tasks,
            'failed': failed_tasks,
            'deleted_count': len(deleted_tasks),
            'failed_count': len(failed_tasks),
            'message': f"Deleted {len(deleted_tasks)} tasks, {len(failed_tasks)} failed"
        }
    except Exception as e:
        logger.error(f"Error in batch delete: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@mcp.tool()
async def batch_complete_by_filter(params: BatchFilterParams) -> Dict[str, Any]:
    """Mark multiple tasks as completed based on filter criteria"""
    try:
        # Find tasks matching the filter
        matching_tasks = filter_tasks(params)
        
        completed_tasks = []
        failed_tasks = []
        
        for task in matching_tasks:
            try:
                task_id = safe_get_task_field(task, 'id')
                task_desc = safe_get_task_field(task, 'description')
                task.done()
                completed_tasks.append({
                    'id': task_id,
                    'description': task_desc
                })
            except Exception as e:
                failed_tasks.append({
                    'id': safe_get_task_field(task, 'id'),
                    'error': str(e)
                })
        
        return {
            'success': True,
            'filter_matched': len(matching_tasks),
            'completed': completed_tasks,
            'failed': failed_tasks,
            'completed_count': len(completed_tasks),
            'failed_count': len(failed_tasks),
            'message': f"Found {len(matching_tasks)} matching tasks, completed {len(completed_tasks)}, {len(failed_tasks)} failed"
        }
    except Exception as e:
        logger.error(f"Error in batch complete by filter: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@mcp.tool()
async def batch_delete_by_filter(params: BatchFilterParams) -> Dict[str, Any]:
    """Delete multiple tasks based on filter criteria"""
    try:
        # Find tasks matching the filter
        matching_tasks = filter_tasks(params)
        
        deleted_tasks = []
        failed_tasks = []
        
        for task in matching_tasks:
            try:
                task_id = safe_get_task_field(task, 'id')
                task_desc = safe_get_task_field(task, 'description')
                task.delete()
                deleted_tasks.append({
                    'id': task_id,
                    'description': task_desc
                })
            except Exception as e:
                failed_tasks.append({
                    'id': safe_get_task_field(task, 'id'),
                    'error': str(e)
                })
        
        return {
            'success': True,
            'filter_matched': len(matching_tasks),
            'deleted': deleted_tasks,
            'failed': failed_tasks,
            'deleted_count': len(deleted_tasks),
            'failed_count': len(failed_tasks),
            'message': f"Found {len(matching_tasks)} matching tasks, deleted {len(deleted_tasks)}, {len(failed_tasks)} failed"
        }
    except Exception as e:
        logger.error(f"Error in batch delete by filter: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@mcp.tool()
async def batch_modify_tasks(params: BatchModifyParams) -> Dict[str, Any]:
    """Modify multiple tasks at once"""
    try:
        # Get tasks to modify
        if params.task_ids:
            # Use specific task IDs
            tasks_to_modify = []
            for task_id in params.task_ids:
                try:
                    tasks_to_modify.append(tw.tasks.get(id=task_id))
                except Task.DoesNotExist:
                    continue
        elif params.filters:
            # Use filter criteria
            tasks_to_modify = filter_tasks(params.filters)
        else:
            return {
                'success': False,
                'error': 'Either task_ids or filters must be provided'
            }
        
        modified_tasks = []
        failed_tasks = []
        
        for task in tasks_to_modify:
            try:
                task_id = safe_get_task_field(task, 'id')
                task_desc = safe_get_task_field(task, 'description')
                
                # Apply modifications
                if params.project is not None:
                    task['project'] = params.project
                
                if params.priority is not None:
                    task['priority'] = params.priority
                
                if params.due is not None:
                    if params.due:
                        due_dt = datetime.fromisoformat(params.due.replace('Z', '+00:00'))
                        local_due = due_dt.astimezone()
                        task['due'] = local_due
                    else:
                        task['due'] = None
                
                # Handle tags
                current_tags = safe_get_task_field(task, 'tags') or set()
                if not isinstance(current_tags, set):
                    current_tags = set(current_tags) if current_tags else set()
                
                if params.add_tags:
                    current_tags.update(params.add_tags)
                
                if params.remove_tags:
                    current_tags.difference_update(params.remove_tags)
                
                if params.add_tags or params.remove_tags:
                    task['tags'] = current_tags
                
                task.save()
                
                modified_tasks.append({
                    'id': task_id,
                    'description': task_desc,
                    'changes': []
                })
                
            except Exception as e:
                failed_tasks.append({
                    'id': safe_get_task_field(task, 'id'),
                    'error': str(e)
                })
        
        return {
            'success': True,
            'found_tasks': len(tasks_to_modify),
            'modified': modified_tasks,
            'failed': failed_tasks,
            'modified_count': len(modified_tasks),
            'failed_count': len(failed_tasks),
            'message': f"Found {len(tasks_to_modify)} tasks, modified {len(modified_tasks)}, {len(failed_tasks)} failed"
        }
    except Exception as e:
        logger.error(f"Error in batch modify: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@mcp.tool()
async def preview_batch_operation(params: BatchFilterParams) -> Dict[str, Any]:
    """Preview which tasks would be affected by a batch operation with the given filters"""
    try:
        matching_tasks = filter_tasks(params)
        
        task_previews = []
        for task in matching_tasks:
            task_previews.append({
                'id': safe_get_task_field(task, 'id'),
                'description': safe_get_task_field(task, 'description'),
                'project': safe_get_task_field(task, 'project'),
                'priority': safe_get_task_field(task, 'priority'),
                'status': safe_get_task_field(task, 'status'),
                'tags': list(safe_get_task_field(task, 'tags')) if safe_get_task_field(task, 'tags') else []
            })
        
        return {
            'success': True,
            'matched_count': len(matching_tasks),
            'tasks': task_previews,
            'message': f"Found {len(matching_tasks)} tasks matching the criteria"
        }
    except Exception as e:
        logger.error(f"Error in preview batch operation: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Resource definitions - simplified approach
@mcp.resource("taskwarrior://daily-report")
async def daily_report() -> str:
    """Generate daily task report"""
    try:
        pending = tw.tasks.pending()
        completed = tw.tasks.completed()
        
        # Count overdue tasks
        now = datetime.now()
        overdue = len([t for t in pending if 'due' in t and t['due'] and t['due'] < now])
        
        # Count by priority
        priority_counts = {'H': 0, 'M': 0, 'L': 0, 'None': 0}
        for task in pending:
            priority = task.get('priority', None)
            if priority in priority_counts:
                priority_counts[priority] += 1
            else:
                priority_counts['None'] += 1
        
        report = "# Daily Task Report\n\n"
        report += f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        report += "## Summary\n"
        report += f"- **Pending Tasks**: {len(pending)}\n"
        report += f"- **Completed Tasks**: {len(completed)}\n"
        report += f"- **Overdue**: {overdue}\n\n"
        
        report += "## Priority Breakdown\n"
        for priority, count in priority_counts.items():
            if count > 0:
                report += f"- **{priority}**: {count} tasks\n"
        
        report += "\n## Today's Tasks\n"
        today_tasks = [
            task for task in pending 
            if 'due' in task and task['due'] and task['due'].date() == datetime.now().date()
        ]
        if today_tasks:
            for task in today_tasks:
                report += f"- [{task['id']}] {task['description']}"
                if 'project' in task and task['project']:
                    report += f" ({task['project']})"
                report += "\n"
        else:
            report += "*No tasks due today*\n"
        
        return report
    except Exception as e:
        return f"Error generating daily report: {e}"

@mcp.resource("taskwarrior://task-summary")
async def task_summary() -> str:
    """Get task summary statistics in JSON format"""
    try:
        summary_data = await get_summary()
        return json.dumps(summary_data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)})

@mcp.resource("taskwarrior://pending-tasks")
async def pending_tasks() -> str:
    """Get all pending tasks in JSON format"""
    try:
        params = ListTasksParams(status='pending')
        tasks_data = await list_tasks(params)
        return json.dumps(tasks_data, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)})

# Prompt definitions - simplified approach
@mcp.prompt()
async def daily_planning() -> str:
    """Help plan daily tasks and priorities"""
    try:
        summary_data = await get_summary()
        if summary_data['success']:
            summary = summary_data['summary']
            context = f"""
Current Task Status:
- Pending: {summary['status']['pending']}
- Completed: {summary['status']['completed']}
- Overdue: {summary['overdue']}

Priority Distribution:
- High: {summary['priority']['H']}
- Medium: {summary['priority']['M']}
- Low: {summary['priority']['L']}
"""
            return f"Help me plan my day. Here's my current task situation:\n\n{context}\n\nProvide recommendations for today's focus."
    except Exception as e:
        logger.error(f"Error in daily_planning prompt: {e}")
    
    return "Help me plan my daily tasks."

@mcp.prompt()
async def task_prioritization() -> str:
    """Help prioritize current tasks"""
    try:
        summary_data = await get_summary()
        if summary_data['success']:
            summary = summary_data['summary']
            context = f"""
Current Task Status:
- Pending: {summary['status']['pending']}
- Overdue: {summary['overdue']}

Priority Distribution:
- High: {summary['priority']['H']}
- Medium: {summary['priority']['M']}
- Low: {summary['priority']['L']}
"""
            return f"Help me prioritize my tasks:\n\n{context}\n\nSuggest an optimal order for tackling tasks."
    except Exception as e:
        logger.error(f"Error in task_prioritization prompt: {e}")
    
    return "Help me prioritize my current tasks."

@mcp.prompt()
async def task_formatter() -> str:
    """Help format task descriptions with proper markdown structure and descriptive titles"""
    try:
        # Get some context about existing tasks for consistency
        pending = tw.tasks.pending()
        recent_tasks = []
        
        # Get up to 3 recent tasks as examples
        for task in sorted(pending, key=lambda t: safe_get_task_field(t, 'entry') or datetime.min, reverse=True)[:3]:
            task_desc = safe_get_task_field(task, 'description')
            task_project = safe_get_task_field(task, 'project')
            if task_desc:
                recent_tasks.append({
                    'description': task_desc[:80] + '...' if len(task_desc) > 80 else task_desc,
                    'project': task_project or 'No project'
                })
        
        context = ""
        if recent_tasks:
            context = f"""
Recent tasks for reference:
"""
            for i, task in enumerate(recent_tasks, 1):
                context += f"{i}. {task['description']} (Project: {task['project']})\n"
        
        return f"""I need to create a new task, but I want to format the description properly using markdown with a clear structure. 

Please help me rewrite task descriptions using this format:

**Format Guidelines:**
- Start with a descriptive title using ## heading
- Include a brief summary of what needs to be done
- Add specific details, requirements, or steps using bullet points
- Include any relevant context, links, or references
- Use markdown formatting for better readability

**Example Format:**
```
## Fix User Authentication Bug

Fix the login form validation that's preventing users from signing in with special characters in passwords.

**Details:**
- Issue affects users with passwords containing @, #, $ symbols
- Error occurs on both web and mobile interfaces
- Need to update regex validation pattern
- Test with various special character combinations

**Acceptance Criteria:**
- [ ] Users can login with special characters
- [ ] Validation provides clear error messages
- [ ] Changes work on all platforms
```

{context}

Please rewrite my task description following this markdown structure to make it more organized and actionable."""
    except Exception as e:
        logger.error(f"Error in task_formatter prompt: {e}")
    
    return """I need help formatting a task description using markdown structure.

Please rewrite my task description with:
- A descriptive ## title
- Brief summary
- Bullet points for details/steps
- Clear acceptance criteria when relevant

Use proper markdown formatting to make the task more organized and actionable."""

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run(transport='stdio')