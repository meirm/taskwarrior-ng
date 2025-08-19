"""
Task reporting resources: daily reports, weekly summaries
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastmcp import FastMCP

from utils.taskwarrior import tw, task_to_dict, task_to_model

logger = logging.getLogger("taskwarrior-mcp.resources.reports")

# Get the MCP instance - this will be injected by the server
mcp: FastMCP = None

def init_resources(mcp_instance: FastMCP):
    """Initialize resources with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register all resources with the MCP instance
    mcp.resource("taskwarrior://daily-report")(daily_report)
    mcp.resource("taskwarrior://weekly-summary")(weekly_summary)
    mcp.resource("taskwarrior://live-tasks")(live_tasks)

async def daily_report() -> str:
    """Generate a daily task report in Markdown format"""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get pending tasks
        pending_tasks = tw.tasks.pending()
        
        # Get completed tasks from today
        completed_today = []
        for task in tw.tasks.completed():
            task_model = task_to_model(task)
            if task_model.end and task_model.end.date() == now.date():
                completed_today.append(task)
        
        # Get overdue tasks
        overdue_tasks = []
        for task in pending_tasks:
            task_model = task_to_model(task)
            if task_model.due and task_model.due < now:
                overdue_tasks.append(task)
        
        # Get tasks due today
        due_today = []
        for task in pending_tasks:
            task_model = task_to_model(task)
            if task_model.due and task_model.due.date() == now.date():
                due_today.append(task)
        
        # Build report
        report = f"# Daily Task Report - {now.strftime('%Y-%m-%d')}\n\n"
        
        # Summary
        report += "## Summary\n"
        report += f"- **Total pending tasks**: {len(pending_tasks)}\n"
        report += f"- **Completed today**: {len(completed_today)}\n"
        report += f"- **Overdue tasks**: {len(overdue_tasks)}\n"
        report += f"- **Due today**: {len(due_today)}\n\n"
        
        # Completed tasks
        if completed_today:
            report += "## ✅ Completed Today\n"
            for task in completed_today:
                task_model = task_to_model(task)
                report += f"- [{task_model.id}] {task_model.description}\n"
            report += "\n"
        
        # Overdue tasks
        if overdue_tasks:
            report += "## 🚨 Overdue Tasks\n"
            for task in sorted(overdue_tasks, key=lambda t: task_to_model(t).due or datetime.min):
                task_model = task_to_model(task)
                due_str = task_model.due.strftime('%Y-%m-%d %H:%M') if task_model.due else 'No due date'
                report += f"- [{task_model.id}] {task_model.description} (due: {due_str})\n"
            report += "\n"
        
        # Due today
        if due_today:
            report += "## 📅 Due Today\n"
            for task in sorted(due_today, key=lambda t: task_to_model(t).due or datetime.min):
                task_model = task_to_model(task)
                due_str = task_model.due.strftime('%H:%M') if task_model.due else 'No time'
                report += f"- [{task_model.id}] {task_model.description} (due: {due_str})\n"
            report += "\n"
        
        # High priority pending tasks
        high_priority = [t for t in pending_tasks if task_to_model(t).priority == 'H']
        if high_priority:
            report += "## 🔥 High Priority Tasks\n"
            for task in high_priority[:10]:  # Limit to top 10
                task_model = task_to_model(task)
                report += f"- [{task_model.id}] {task_model.description}\n"
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return f"Error generating daily report: {str(e)}"

async def weekly_summary() -> str:
    """Generate a weekly task summary in Markdown format"""
    try:
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get completed tasks from this week
        completed_this_week = []
        for task in tw.tasks.completed():
            if hasattr(task, 'end') and task['end']:
                end_date = task['end']
                if end_date >= week_start:
                    completed_this_week.append(task)
        
        # Group by project
        projects = {}
        for task in completed_this_week:
            project = task.get('project', 'No Project')
            if project not in projects:
                projects[project] = []
            projects[project].append(task)
        
        # Build summary
        report = f"# Weekly Summary - Week of {week_start.strftime('%Y-%m-%d')}\n\n"
        
        report += f"## Overview\n"
        report += f"- **Total completed**: {len(completed_this_week)}\n"
        report += f"- **Projects involved**: {len(projects)}\n\n"
        
        if projects:
            report += "## Completed by Project\n"
            for project, tasks in sorted(projects.items()):
                report += f"\n### {project} ({len(tasks)} tasks)\n"
                for task in tasks:
                    end_date = task['end'].strftime('%m-%d')
                    report += f"- [{task['id']}] {task['description']} (completed: {end_date})\n"
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating weekly summary: {e}")
        return f"Error generating weekly summary: {str(e)}"

async def live_tasks() -> Dict[str, Any]:
    """Get current task data in JSON format"""
    try:
        pending_tasks = tw.tasks.pending()
        
        # Convert to dictionaries
        tasks = [task_to_dict(task) for task in pending_tasks]
        
        # Sort by urgency descending
        tasks.sort(key=lambda t: t.get('urgency', 0), reverse=True)
        
        # Group by status for summary
        status_summary = {}
        for task in tasks:
            status = task.get('status', 'unknown')
            status_summary[status] = status_summary.get(status, 0) + 1
        
        # Group by project
        project_summary = {}
        for task in tasks:
            project = task.get('project', 'No Project')
            project_summary[project] = project_summary.get(project, 0) + 1
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_tasks': len(tasks),
            'tasks': tasks,
            'status_summary': status_summary,
            'project_summary': project_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting live tasks: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }