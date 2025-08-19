"""
Task filtering utilities for batch operations
"""
import logging
from datetime import datetime
from typing import List

from tasklib import Task
from utils.taskwarrior import tw, task_to_model
from utils.models import BatchFilterParams

logger = logging.getLogger("taskwarrior-mcp.filters")

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
        # Apply filters using TaskModel for safe field access
        task_model = task_to_model(task)
        matches = True
        
        # Project filter
        if filters.project:
            if task_model.project != filters.project:
                matches = False
        
        # Priority filter
        if filters.priority:
            if task_model.priority != filters.priority:
                matches = False
        
        # Tags filter (task must have ANY of the specified tags)
        if filters.tags:
            if not task_model.tags or not any(tag in task_model.tags for tag in filters.tags):
                matches = False
        
        # Description contains filter
        if filters.description_contains:
            if not task_model.description or filters.description_contains.lower() not in task_model.description.lower():
                matches = False
        
        # Due date filters
        task_due = task_model.due
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