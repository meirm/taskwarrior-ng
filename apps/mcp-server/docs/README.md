# Taskwarrior MCP Server

A modern, feature-complete Model Context Protocol (MCP) server built with FastMCP that provides AI assistants with comprehensive access to Taskwarrior functionality through the tasklib Python library.

## Features

- **Complete Task Management**: 11 tools for full CRUD operations
- **Smart Resources**: 7 resources providing reports and live data  
- **AI Prompts**: 5 intelligent prompts for task planning and analysis
- **FastMCP Implementation**: Modern MCP 1.13.0+ compatibility with FastMCP
- **Type Safety**: Pydantic models for robust parameter validation
- **Rich Reporting**: Markdown reports and JSON data feeds
- **Error Handling**: Comprehensive error handling with structured responses
- **Flexible Integration**: Works with Claude Desktop and any MCP-compatible AI assistant

## Prerequisites

- Python 3.8+ (Python 3.11+ recommended for best performance)
- Taskwarrior 2.4.x+ installed and configured
- FastMCP 2.11.3+ and dependencies

## Installation

1. **Install dependencies:**
   ```bash
   cd apps/mcp-server/config
   pip install -r requirements.txt
   ```

2. **Verify Taskwarrior installation:**
   ```bash
   task --version
   ```

3. **Run installation script:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

## Usage

### Running the Server

```bash
python taskwarrior_mcp_server.py
```

### Available Tools

1. **add_task** - Create new tasks with optional project, priority, tags, and due dates
2. **list_tasks** - List tasks with filtering by status, project, or tags
3. **get_task** - Get detailed information about a specific task
4. **complete_task** - Mark tasks as completed
5. **modify_task** - Update task properties
6. **delete_task** - Remove tasks
7. **start_task** - Begin time tracking on a task
8. **stop_task** - End time tracking on a task
9. **get_projects** - List all project names
10. **get_tags** - List all tag names
11. **get_summary** - Get task statistics and summary

### Available Prompts

1. **daily_planning** - Help plan your daily tasks and priorities
2. **task_review** - Review and analyze your task completion patterns
3. **productivity_analysis** - Analyze your productivity and suggest improvements
4. **task_prioritization** - Help prioritize your current tasks based on various factors
5. **project_planning** - Help plan and break down a project into tasks

### Available Resources

1. **taskwarrior://daily-report** - Current daily task status and priorities (Markdown)
2. **taskwarrior://weekly-summary** - Weekly task completion and upcoming deadlines (Markdown)
3. **taskwarrior://task-summary** - Overall task statistics and counts (JSON)
4. **taskwarrior://pending-tasks** - All pending tasks with details (JSON)
5. **taskwarrior://overdue-tasks** - Tasks that are past their due date (JSON)
6. **taskwarrior://projects** - All project names and task counts (JSON)
7. **taskwarrior://tags** - All tag names and usage counts (JSON)

### Example Usage

Once connected to an MCP client, you can interact with Taskwarrior:

**Basic Task Management:**
```
"Add a task to review the quarterly report with high priority"
"List all tasks in the work project"
"Show me overdue tasks"
"Mark task 5 as completed"
"Get a summary of my current tasks"
```

**Using Prompts:**
```
"Use the daily planning prompt to help me organize today"
"Run the productivity analysis prompt for my work project"
"Help me prioritize my current tasks"
```

**Accessing Resources:**
```
"Show me the daily report resource"
"What does the weekly summary resource contain?"
"Give me the overdue tasks resource"
```

## Configuration

The server uses your default Taskwarrior configuration. To use a custom data location:

```python
tw_mcp = TaskWarriorMCP(data_location='/path/to/custom/taskdata')
```

## Integration with Claude Desktop

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "taskwarrior": {
      "command": "python",
      "args": ["/path/to/taskwarrior_mcp_server.py"]
    }
  }
}
```

## Advanced Features

### Smart Prompts
The server includes intelligent prompts that analyze your task data and provide contextual assistance:
- **Daily Planning**: Get personalized daily task recommendations
- **Task Review**: Analyze completion patterns and productivity trends
- **Productivity Analysis**: Deep dive into your task management effectiveness
- **Task Prioritization**: Get help organizing your current workload
- **Project Planning**: Break down complex projects into manageable tasks

### Rich Resources
Access formatted reports and live task data:
- **Daily Reports**: Markdown-formatted daily task summaries
- **Weekly Summaries**: Weekly productivity and completion reports
- **Live Data**: Real-time access to task statistics, projects, and tags

## Error Handling

The server includes comprehensive error handling and returns structured responses with success indicators and error messages.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the server.

## License

This project is open source. Please check the license file for details.
