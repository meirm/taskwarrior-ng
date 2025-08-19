"""
Task planning and prioritization prompts
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastmcp import FastMCP

from utils.taskwarrior import tw, task_to_dict, task_to_model

logger = logging.getLogger("taskwarrior-mcp.prompts.planning")

# Get the MCP instance - this will be injected by the server
mcp: FastMCP = None

def init_prompts(mcp_instance: FastMCP):
    """Initialize prompts with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register all prompts with the MCP instance
    mcp.prompt("daily-planning")(daily_planning_prompt)
    mcp.prompt("task-prioritization")(task_prioritization_prompt)
    mcp.prompt("task-formatter")(task_formatter_prompt)

async def daily_planning_prompt() -> str:
    """Generate a prompt for daily task planning based on current tasks"""
    try:
        pending_tasks = tw.tasks.pending()
        now = datetime.now(timezone.utc)
        
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
        
        # Get high priority tasks
        high_priority = [t for t in pending_tasks if task_to_model(t).priority == 'H']
        
        # Build context
        context = f"""You are helping with daily task planning. Here's the current situation:

## Current Task Status
- Total pending tasks: {len(pending_tasks)}
- Overdue tasks: {len(overdue_tasks)}
- Tasks due today: {len(due_today)}
- High priority tasks: {len(high_priority)}

"""
        
        if overdue_tasks:
            context += "## 🚨 OVERDUE TASKS (Needs immediate attention)\n"
            for task in overdue_tasks[:5]:  # Show top 5 overdue
                task_model = task_to_model(task)
                due_str = task_model.due.strftime('%Y-%m-%d %H:%M') if task_model.due else 'No due date'
                context += f"- [{task_model.id}] {task_model.description} (was due: {due_str})\n"
            context += "\n"
        
        if due_today:
            context += "## 📅 DUE TODAY\n"
            for task in due_today[:5]:  # Show top 5 due today
                task_model = task_to_model(task)
                due_str = task_model.due.strftime('%H:%M') if task_model.due else 'No time'
                context += f"- [{task_model.id}] {task_model.description} (due: {due_str})\n"
            context += "\n"
        
        if high_priority:
            context += "## 🔥 HIGH PRIORITY TASKS\n"
            for task in high_priority[:5]:  # Show top 5 high priority
                task_model = task_to_model(task)
                context += f"- [{task_model.id}] {task_model.description}\n"
            context += "\n"
        
        context += """## Your Task
Please help me plan my day by:

1. **Prioritizing tasks**: Which tasks should I focus on first based on deadlines, priority, and importance?
2. **Time estimation**: Roughly how much time might each priority task take?
3. **Scheduling suggestions**: In what order should I tackle these tasks?
4. **Potential issues**: Are there any dependencies or potential blockers I should be aware of?
5. **Realistic goals**: Given a typical 8-hour work day, what's a realistic set of tasks to complete?

Please provide a structured daily plan with your recommendations."""
        
        return context
        
    except Exception as e:
        logger.error(f"Error generating daily planning prompt: {e}")
        return f"Error generating daily planning prompt: {str(e)}"

async def task_prioritization_prompt() -> str:
    """Generate a prompt for task prioritization analysis"""
    try:
        pending_tasks = tw.tasks.pending()
        
        # Sort by urgency for analysis
        sorted_tasks = sorted(pending_tasks, key=lambda t: task_to_model(t).urgency, reverse=True)
        
        # Group by project
        projects = {}
        for task in pending_tasks:
            task_model = task_to_model(task)
            project = task_model.project or 'No Project'
            if project not in projects:
                projects[project] = []
            projects[project].append(task)
        
        context = f"""You are helping with task prioritization analysis. Here's the current task landscape:

## Task Overview
- Total pending tasks: {len(pending_tasks)}
- Active projects: {len(projects)}

## Top Tasks by Urgency Score
"""
        
        for task in sorted_tasks[:10]:  # Show top 10 by urgency
            task_model = task_to_model(task)
            due_info = f" (due: {task_model.due.strftime('%Y-%m-%d %H:%M')})" if task_model.due else ""
            
            context += f"- [{task_model.id}] {task_model.description}\n"
            context += f"  - Urgency: {task_model.urgency:.1f}, Priority: {task_model.priority or 'None'}, Project: {task_model.project or 'No Project'}{due_info}\n"
        
        context += f"\n## Projects and Task Distribution\n"
        for project, tasks in sorted(projects.items(), key=lambda x: len(x[1]), reverse=True):
            context += f"- **{project}**: {len(tasks)} tasks\n"
        
        context += """
## Your Task
Please help me prioritize my tasks by analyzing:

1. **Priority Matrix**: Which tasks are urgent vs important? Help me categorize them into:
   - Urgent & Important (do first)
   - Important but not urgent (schedule)
   - Urgent but not important (delegate if possible)
   - Neither urgent nor important (eliminate if possible)

2. **Project Balance**: Am I overloaded in any particular project? Should I balance my focus?

3. **Quick Wins**: Are there any small, high-value tasks I can complete quickly to build momentum?

4. **Dependencies**: Do any tasks block others? Which should be done first?

5. **Energy Matching**: Which tasks require high energy/focus vs low energy? How should I sequence them throughout my day?

Please provide specific recommendations for prioritizing and organizing these tasks."""
        
        return context
        
    except Exception as e:
        logger.error(f"Error generating task prioritization prompt: {e}")
        return f"Error generating task prioritization prompt: {str(e)}"

async def task_formatter_prompt() -> str:
    """Generate a prompt to help format task descriptions using markdown"""
    return """You are helping to format and improve task descriptions. When creating or modifying tasks, please structure them using markdown format with these guidelines:

## Task Description Format

### Structure Template
```
# [Descriptive Title]

## Context/Background
Brief explanation of why this task is needed or the problem it solves.

## Objectives
- Clear, actionable goal 1
- Clear, actionable goal 2
- Specific outcome or deliverable

## Acceptance Criteria
- [ ] Specific requirement 1
- [ ] Specific requirement 2
- [ ] Definition of "done"

## Notes
- Any additional details
- Dependencies or prerequisites
- Resources or links
```

### Examples

#### Before (poor):
"Fix the bug"

#### After (good):
```
# Fix Login Authentication Timeout Bug

## Context/Background
Users are experiencing timeout errors during login attempts, particularly during peak hours.

## Objectives
- Identify root cause of authentication timeouts
- Implement fix to prevent timeout errors
- Ensure login process is reliable under load

## Acceptance Criteria
- [ ] Bug reproduced and root cause identified
- [ ] Fix implemented and tested
- [ ] Login success rate > 99% during peak hours
- [ ] No regression in login performance

## Notes
- Affects approximately 15% of users during 9-11 AM
- Check database connection pooling
- May need to optimize authentication query
```

### Guidelines
1. **Start with a descriptive title** that clearly indicates what needs to be done
2. **Provide context** so anyone can understand why this task matters
3. **Define clear objectives** that are specific and measurable
4. **Use checkboxes** for acceptance criteria to track progress
5. **Include relevant details** in notes section
6. **Keep it concise** but comprehensive enough to be actionable

When I provide a task description, please reformat it using this structure, expanding on the details where necessary to make it clear, actionable, and well-organized."""