# 🚀 Batch Operations Documentation

The Taskwarrior MCP Server now includes comprehensive batch operations for handling multiple tasks efficiently.

## 📋 New MCP Tools Added

### 🔢 By Task IDs

**`batch_complete_tasks`** - Mark multiple tasks as completed
```json
{
  "task_ids": [1, 2, 3, 4, 5]
}
```

**`batch_delete_tasks`** - Delete multiple tasks
```json
{
  "task_ids": [10, 11, 12]
}
```

### 🔍 By Filter Criteria

**`batch_complete_by_filter`** - Complete tasks matching filters
```json
{
  "project": "OldProject",
  "priority": "L",
  "limit": 10
}
```

**`batch_delete_by_filter`** - Delete tasks matching filters
```json
{
  "status": "pending",
  "tags": ["deprecated", "old"],
  "due_before": "2025-01-01T00:00:00Z"
}
```

### 🛠️ Batch Modifications

**`batch_modify_tasks`** - Modify multiple tasks at once
```json
{
  "filters": {
    "project": "Migration",
    "status": "pending"
  },
  "project": "NewProject",
  "priority": "M",
  "add_tags": ["migrated", "updated"],
  "remove_tags": ["old", "deprecated"]
}
```

### 👁️ Preview Operations

**`preview_batch_operation`** - Preview which tasks would be affected
```json
{
  "project": "TestProject",
  "priority": "H",
  "limit": 20
}
```

## 🔧 Advanced Filtering System

### Filter Parameters

- **`status`**: `pending`, `completed`, `deleted`
- **`project`**: Exact project name match
- **`priority`**: `H` (High), `M` (Medium), `L` (Low)
- **`tags`**: Array of tags (tasks with ANY of these tags)
- **`description_contains`**: Text search in description
- **`due_before`**: Tasks due before this date (ISO format)
- **`due_after`**: Tasks due after this date (ISO format)
- **`limit`**: Maximum number of tasks to operate on

### Example Complex Filter
```json
{
  "status": "pending",
  "project": "WebApp",
  "priority": "H",
  "tags": ["urgent", "bug"],
  "due_before": "2025-12-31T23:59:59Z",
  "limit": 50
}
```

## 📊 Common Use Cases

### 1. Clean Up Completed Tasks
```json
// Delete all completed tasks older than 30 days
{
  "tool": "batch_delete_by_filter",
  "params": {
    "status": "completed",
    "due_before": "2025-07-15T00:00:00Z"
  }
}
```

### 2. Mass Project Migration
```json
// Move all tasks from OldProject to NewProject
{
  "tool": "batch_modify_tasks",
  "params": {
    "filters": {
      "project": "OldProject"
    },
    "project": "NewProject",
    "add_tags": ["migrated"]
  }
}
```

### 3. Priority Adjustment
```json
// Lower priority of all low-priority tasks
{
  "tool": "batch_modify_tasks", 
  "params": {
    "filters": {
      "priority": "L",
      "status": "pending"
    },
    "priority": null,
    "add_tags": ["review-later"]
  }
}
```

### 4. Bulk Task Completion
```json
// Complete all documentation tasks
{
  "tool": "batch_complete_by_filter",
  "params": {
    "tags": ["documentation"],
    "status": "pending",
    "project": "Release2024"
  }
}
```

### 5. Deadline-Based Operations
```json
// Complete all overdue low-priority tasks
{
  "tool": "batch_complete_by_filter",
  "params": {
    "priority": "L",
    "due_before": "2025-08-15T00:00:00Z",
    "status": "pending"
  }
}
```

## ⚡ Performance Features

- **Smart Filtering**: Efficient task selection with multiple criteria
- **Error Handling**: Individual task failures don't stop batch operations
- **Progress Tracking**: Detailed success/failure reporting
- **Safety Limits**: Built-in limits to prevent accidental mass operations
- **Preview Mode**: See what would be affected before executing

## 🛡️ Safety Features

- **Preview First**: Always use `preview_batch_operation` before destructive operations
- **Granular Results**: Detailed reporting of success and failure for each task
- **Rollback Info**: Failed operations preserve original state
- **Limit Protection**: Built-in limits prevent accidental mass deletion

## 📈 Server Stats Updated

- **Total Tools**: 18 (was 11)
  - 11 individual task operations
  - 7 new batch operations
- **New Capabilities**: 
  - `batch_operations`
  - `advanced_filtering`

## 🧪 Testing Results

✅ **All batch operations tested and verified**:
- Filter functionality: PASS
- Batch complete by IDs: PASS  
- Batch complete by filter: PASS
- Batch modify: PASS
- Preview operation: PASS

The batch operations system is production-ready and provides powerful bulk task management capabilities while maintaining data safety and integrity.