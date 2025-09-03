# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-09-02-project-selector-ui/spec.md

> Created: 2025-09-02
> Version: 1.0.0

## Endpoints

### GET /api/projects

**Purpose:** Retrieve list of all unique project names from tasks
**Parameters:** None
**Response:** 
```json
{
  "success": true,
  "projects": ["Work", "Personal", "Work.Backend", "Work.Frontend"],
  "count": 4
}
```
**Errors:** 
- 500: Server error if TaskWarrior connection fails

**Note:** This endpoint already exists in the MCP server as `get_projects` tool

### POST /api/tasks

**Purpose:** Create a new task with optional project assignment
**Parameters:**
```json
{
  "description": "string",
  "project": "string (optional)",
  "priority": "H|M|L (optional)",
  "due": "ISO 8601 date (optional)",
  "tags": ["array", "of", "strings"] 
}
```
**Response:**
```json
{
  "success": true,
  "task": {
    "id": 123,
    "uuid": "uuid-string",
    "description": "Task description",
    "project": "ProjectName",
    "status": "pending"
  }
}
```
**Errors:**
- 400: Invalid request body
- 500: TaskWarrior operation failed

**Note:** Project is created automatically if it doesn't exist

### PUT /api/tasks/:id

**Purpose:** Modify an existing task including project assignment
**Parameters:**
```json
{
  "project": "string (optional, null to remove)",
  "description": "string (optional)",
  "priority": "H|M|L (optional)",
  "due": "ISO 8601 date (optional)"
}
```
**Response:**
```json
{
  "success": true,
  "task": {
    "id": 123,
    "project": "NewProject",
    "modified": "2025-09-02T10:30:00Z"
  }
}
```
**Errors:**
- 404: Task not found
- 400: Invalid modification parameters
- 500: TaskWarrior operation failed

## Controllers

### ProjectController

**Actions:**
- `getProjects()`: Retrieve unique project list from TaskWarrior
- `getProjectStats()`: Get task counts per project (future enhancement)

**Business Logic:**
- Extract unique project names from all tasks
- Sort projects alphabetically
- Handle hierarchical project names (dot notation)

**Error Handling:**
- Catch TaskWarrior connection errors
- Return empty array if no projects exist
- Log errors for debugging

### TaskController Extensions

**Actions:**
- `createTaskWithProject()`: Handle task creation with project
- `updateTaskProject()`: Modify task's project assignment

**Business Logic:**
- Auto-create projects on task assignment (TaskWarrior behavior)
- Validate project name format (no special characters except dots)
- Handle null/empty project to remove assignment

**Error Handling:**
- Validate project name before assignment
- Handle TaskWarrior save failures
- Provide meaningful error messages

## Purpose

### Endpoint Rationale

The project-related API endpoints enable the frontend to:
1. Fetch available projects for the dropdown selector
2. Create tasks with project assignments in a single operation
3. Modify task project assignments including removal
4. Leverage TaskWarrior's automatic project creation

### Integration with Features

- **ProjectSelector Component**: Uses GET /api/projects for dropdown population
- **Task Creation Form**: POSTs to /api/tasks with project field
- **Task Edit Form**: PUTs to /api/tasks/:id to update project
- **Optimistic Updates**: Frontend updates immediately, API confirms
- **Cache Management**: TanStack Query handles caching and invalidation