# Quick Start Guide

## Setup Instructions

1. **Make sure Taskwarrior is installed:**
   ```bash
   brew install task  # macOS
   task --version     # Verify installation
   ```

2. **Install Python dependencies:**
   ```bash
   cd /Users/meirm/git/riunx/taskwarrior-ng
   pip install -r requirements.txt
   ```

3. **Test the server:**
   ```bash
   python test_taskwarrior_mcp.py
   ```

4. **Run the MCP server:**
   ```bash
   python taskwarrior_mcp_server.py
   ```

## Claude Desktop Integration

Add this to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "taskwarrior": {
      "command": "python",
      "args": ["/Users/meirm/git/riunx/taskwarrior-ng/taskwarrior_mcp_server.py"]
    }
  }
}
```

## File Overview

- `taskwarrior_mcp_server.py` - Main MCP server implementation
- `test_taskwarrior_mcp.py` - Test client to verify functionality
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation
- `config.json` - Example MCP configuration
- `setup.py` - Package setup file
- `install.sh` - Automated installation script

## Basic Usage Examples

### Task Management
Once connected to Claude Desktop, you can say things like:

- "Add a task to review the project proposal with high priority"
- "Show me all pending tasks in the work project"
- "Mark task 3 as completed"
- "Start working on the presentation task"
- "Give me a summary of my current tasks"

### Using Smart Prompts
The server includes intelligent prompts that analyze your data:

- "Use the daily planning prompt to help me organize today"
- "Run the task review prompt for this week"
- "Help me with productivity analysis for my work project"
- "Use the task prioritization prompt"
- "Help me plan my new website project using the project planning prompt"

### Accessing Resources
Get formatted reports and live data:

- "Show me the daily report resource"
- "What's in the weekly summary resource?"
- "Give me the overdue tasks resource"
- "Show me all projects and their task counts"

## What's Available

### 11 Tools
Complete task management including add, list, modify, complete, delete, start/stop, projects, tags, and summary.

### 5 Smart Prompts
- **daily_planning** - Personalized daily task organization
- **task_review** - Analyze completion patterns and trends
- **productivity_analysis** - Deep productivity insights
- **task_prioritization** - Help prioritize current workload
- **project_planning** - Break down projects into tasks

### 7 Resources
- **daily-report** - Daily task status (Markdown)
- **weekly-summary** - Weekly productivity report (Markdown)
- **task-summary** - Overall statistics (JSON)
- **pending-tasks** - All pending tasks (JSON)
- **overdue-tasks** - Overdue tasks (JSON)
- **projects** - Project list and counts (JSON)
- **tags** - Tag list and usage (JSON)

The server provides natural language access to your complete Taskwarrior workflow with intelligent assistance!
