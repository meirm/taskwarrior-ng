# Taskwarrior MCP Server - Usage Examples

This document provides examples of how to use all the features of the Taskwarrior MCP server.

## 1. Tools (Task Management)

### Basic Task Operations
```
# Add tasks
"Add a task 'Review quarterly report' with high priority in the work project"
"Create a task to 'Buy groceries' due tomorrow with tags shopping and personal"

# List and filter tasks
"Show me all pending tasks"
"List tasks in the work project"
"Show me all high priority tasks"
"What tasks do I have with the urgent tag?"

# Modify tasks
"Mark task 5 as completed"
"Change task 3 priority to high"
"Add the tag 'urgent' to task 7"
"Set task 12 due date to next Friday"

# Time tracking
"Start working on task 4"
"Stop working on the current task"

# Get information
"Show me details for task 8"
"Get a summary of all my tasks"
"List all my projects"
"What tags do I use?"
```

## 2. Smart Prompts

### Daily Planning Prompt
```
"Use the daily planning prompt to help me organize today"
"Run the daily planning prompt with focus on my work project"
"Help me plan my day using the daily planning prompt"
```

**What it does:**
- Analyzes your current tasks, overdue items, and priorities
- Provides personalized recommendations for your daily schedule
- Suggests time blocking and task grouping strategies
- Identifies potential scheduling conflicts

### Task Review Prompt
```
"Use the task review prompt for this week"
"Run the weekly task review prompt"
"Analyze my task completion patterns using the task review prompt"
```

**What it does:**
- Reviews your completion patterns and productivity trends
- Identifies areas where you're excelling
- Spots potential bottlenecks or recurring issues
- Provides constructive feedback and improvement suggestions

### Productivity Analysis Prompt
```
"Run the productivity analysis prompt"
"Analyze my productivity for the work project"
"Use the productivity analysis prompt to review my efficiency"
```

**What it does:**
- Deep analysis of your task completion efficiency
- Examines time management patterns
- Evaluates priority handling effectiveness
- Provides specific, actionable recommendations

### Task Prioritization Prompt
```
"Use the task prioritization prompt to help organize my workload"
"Help me prioritize my current tasks"
"Run the prioritization prompt"
```

**What it does:**
- Analyzes all your pending tasks
- Considers urgency, importance, and dependencies
- Suggests optimal priority ordering
- Recommends task grouping and scheduling

### Project Planning Prompt
```
"Use the project planning prompt for my website redesign project"
"Help me plan the mobile app project with deadline December 31st"
"Break down my marketing campaign project using the planning prompt"
```

**What it does:**
- Breaks down complex projects into manageable tasks
- Identifies task dependencies and sequences
- Suggests priorities and timelines
- Provides specific tasks you can add to Taskwarrior

## 3. Resources (Live Data Access)

### Daily Report Resource
```
"Show me the daily report resource"
"What's in my daily task report?"
"Give me today's task overview"
```

**Contains:**
- Currently active tasks
- Tasks due today
- Overdue tasks with days overdue
- High priority tasks
- Summary statistics

### Weekly Summary Resource
```
"Show me the weekly summary resource"
"What does my weekly report look like?"
"Give me this week's productivity summary"
```

**Contains:**
- Tasks completed this week
- Tasks due this week
- Weekly statistics and trends
- Daily completion averages

### Task Summary Resource
```
"Show me the task summary resource"
"What are my overall task statistics?"
"Give me the summary data"
```

**Contains:**
- Total task counts by status
- Overdue task count
- Due today count
- High priority task count

### Live Task Resources
```
"Show me the pending tasks resource"
"What's in the overdue tasks resource?"
"Give me all my projects data"
"Show me the tags resource"
```

**Contains:**
- Real-time task data
- Project and tag statistics
- Detailed task information in JSON format

## 4. Advanced Usage Patterns

### Morning Planning Routine
```
"Show me the daily report resource"
"Use the daily planning prompt to organize my day"
"What high priority tasks do I have?"
"Start working on my most important task"
```

### Weekly Review Workflow
```
"Show me the weekly summary resource"
"Use the task review prompt for this week"
"Run the productivity analysis prompt"
"What projects need attention?"
```

### Project Management
```
"Use the project planning prompt for my new project"
"Show me all tasks in the development project"
"Analyze productivity for the marketing project"
"What's the completion rate for project X?"
```

### Real-time Task Management
```
"What overdue tasks do I have?" (uses overdue-tasks resource)
"Show me today's priorities" (uses daily-report resource)  
"Help me prioritize" (uses task-prioritization prompt)
"Start working on the most urgent task"
```

## 5. Integration Examples

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "taskwarrior": {
      "command": "python",
      "args": ["/Users/meirm/git/riunx/taskwarrior-ng/taskwarrior_mcp_server.py"],
      "env": {
        "TASKDATA": "/path/to/custom/taskdata"
      }
    }
  }
}
```

### Custom Data Location
If you want to use a specific Taskwarrior database:
```json
{
  "mcpServers": {
    "taskwarrior": {
      "command": "python",
      "args": ["/Users/meirm/git/riunx/taskwarrior-ng/taskwarrior_mcp_server.py"],
      "env": {
        "TASKDATA": "/Users/meirm/Documents/work-tasks"
      }
    }
  }
}
```

## 6. Natural Language Examples

The beauty of the MCP server is that you can use natural language:

```
"I need to plan my day - what should I focus on?"
→ Uses daily planning prompt and daily report resource

"How productive was I this week?"
→ Uses task review prompt and weekly summary resource

"I have too many tasks - help me prioritize"
→ Uses task prioritization prompt

"I'm starting a new project called 'website redesign' - help me break it down"
→ Uses project planning prompt

"What am I supposed to be working on right now?"
→ Accesses daily report and active tasks

"Show me everything that's overdue"
→ Uses overdue tasks resource

"I finished the presentation task"
→ Uses complete_task tool

"Track time on my coding task"
→ Uses start_task tool
```

This MCP server transforms Taskwarrior from a command-line tool into an intelligent task management assistant that understands natural language and provides contextual insights!
