"""
Metadata operations: get projects, tags, summary statistics
"""
import logging
from datetime import datetime
from typing import Any, Dict

from fastmcp import FastMCP

from utils.taskwarrior import tw, task_to_model

logger = logging.getLogger("taskwarrior-mcp.tools.metadata")

# Get the MCP instance - this will be injected by the server
mcp: FastMCP = None

def init_tools(mcp_instance: FastMCP):
    """Initialize tools with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register all tools with the MCP instance
    mcp.tool()(get_projects)
    mcp.tool()(get_tags)
    mcp.tool()(get_summary)

async def get_projects() -> Dict[str, Any]:
    """Get all unique project names"""
    try:
        projects = set()
        for task in tw.tasks.all():
            task_model = task_to_model(task)
            if task_model.project:
                projects.add(task_model.project)
        
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

async def get_tags() -> Dict[str, Any]:
    """Get all unique tags"""
    try:
        tags = set()
        for task in tw.tasks.all():
            task_model = task_to_model(task)
            if task_model.tags:
                tags.update(task_model.tags)
        
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
            task_model = task_to_model(task)
            priority = task_model.priority
            if priority in priority_counts:
                priority_counts[priority] += 1
            else:
                priority_counts['None'] += 1
        
        # Count overdue tasks
        from datetime import timezone
        now = datetime.now(timezone.utc)
        overdue = 0
        for task in pending:
            task_model = task_to_model(task)
            due_date = task_model.due
            if due_date:
                # Make due_date timezone-aware if it isn't already
                if due_date.tzinfo is None:
                    due_date = due_date.replace(tzinfo=timezone.utc)
                # Convert to UTC for comparison
                due_date_utc = due_date.astimezone(timezone.utc)
                if due_date_utc < now:
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