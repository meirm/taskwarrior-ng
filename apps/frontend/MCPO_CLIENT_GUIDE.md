# MCPO Client Guide for TaskWarrior-NG Frontend

This guide explains how to use the MCPO (Model Context Protocol to OpenAPI) client in the TaskWarrior-NG frontend application.

## Overview

The MCPO client provides a TypeScript/React interface to interact with MCP servers through a REST API. It includes:
- Type-safe client class
- React hooks for easy integration
- Error handling and loading states
- Direct tool invocation capabilities

## Installation

The MCPO client is already included in the frontend. To use it:

```typescript
// Import the client
import { mcpoClient } from '@/services/mcpo-client';

// Or import the class to create custom instances
import MCPOClient from '@/services/mcpo-client';

// Import React hooks
import { useListTasks, useAddTask } from '@/hooks/useMCPO';
```

## Configuration

### Environment Variables

Configure the MCPO client using environment variables in `.env.local`:

```env
VITE_MCPO_URL=http://localhost:8085
VITE_MCPO_API_KEY=your-api-key-here
```

### Custom Configuration

Create a custom client instance with specific configuration:

```typescript
const customClient = new MCPOClient({
  baseURL: 'http://localhost:8085',
  apiKey: 'your-api-key',
  timeout: 30000, // 30 seconds
  headers: {
    'Custom-Header': 'value'
  }
});
```

## Usage Methods

### 1. Using React Hooks (Recommended)

The easiest way to use MCPO in React components:

```typescript
import { useListTasks, useAddTask, useCompleteTask } from '@/hooks/useMCPO';

function TaskManager() {
  // Auto-load tasks on mount
  const { data, loading, error, execute: refreshTasks } = useListTasks(true, {
    status: 'pending',
    limit: 10
  });

  // Manual execution hooks
  const addTask = useAddTask();
  const completeTask = useCompleteTask();

  const handleAddTask = async () => {
    try {
      await addTask.execute({
        description: 'New task',
        priority: 'H',
        tags: ['important']
      });
      await refreshTasks(); // Refresh the list
    } catch (error) {
      console.error('Failed to add task:', error);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data?.tasks.map(task => (
        <div key={task.id}>
          {task.description}
          <button onClick={() => completeTask.execute(task.id)}>
            Complete
          </button>
        </div>
      ))}
      <button onClick={handleAddTask}>Add Task</button>
    </div>
  );
}
```

### 2. Using the Client Directly

For more control, use the client directly:

```typescript
import { mcpoClient } from '@/services/mcpo-client';

async function fetchTasks() {
  try {
    const result = await mcpoClient.listTasks({
      status: 'pending',
      project: 'work'
    });
    console.log('Tasks:', result.tasks);
  } catch (error) {
    console.error('Error:', error);
  }
}

async function createTask() {
  try {
    const result = await mcpoClient.addTask({
      description: 'Complete documentation',
      priority: 'M',
      due: '2024-12-31',
      tags: ['docs', 'urgent']
    });
    console.log('Created task:', result.data.task);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### 3. Using the MCPO Provider

Wrap your app with the MCPO provider for global configuration:

```typescript
import { MCPOProvider } from '@/hooks/useMCPO';

function App() {
  return (
    <MCPOProvider config={{
      baseURL: 'http://localhost:8085',
      apiKey: 'your-api-key'
    }}>
      <YourComponents />
    </MCPOProvider>
  );
}
```

### 4. Direct Tool Invocation

Invoke any MCP tool directly:

```typescript
import { useMCPOTool } from '@/hooks/useMCPO';

function CustomToolUser() {
  const customTool = useMCPOTool('get_task_summary');
  
  const handleInvoke = async () => {
    const result = await customTool.execute({
      include_completed: true,
      group_by: 'project'
    });
    console.log('Summary:', result);
  };

  return (
    <button onClick={handleInvoke} disabled={customTool.loading}>
      Get Summary
    </button>
  );
}
```

## Available Methods

### Task Operations
- `addTask(params)` - Create a new task
- `listTasks(params)` - List tasks with filters
- `getTask(taskId)` - Get a specific task
- `modifyTask(params)` - Modify task properties
- `completeTask(taskId)` - Mark task as complete
- `uncompleteTask(taskId, uuid?)` - Mark task as pending
- `deleteTask(taskId)` - Delete a task
- `startTask(taskId)` - Start task timer
- `stopTask(taskId)` - Stop task timer

### Batch Operations
- `batchCompleteTasks(taskIds)` - Complete multiple tasks
- `batchCompleteByFilter(filters)` - Complete by filter
- `batchDeleteTasks(taskIds)` - Delete multiple tasks
- `batchStartTasks(taskIds)` - Start multiple task timers
- `batchStopTasks(taskIds)` - Stop multiple task timers
- `batchModifyTasks(params)` - Modify multiple tasks

### Metadata Operations
- `getProjects()` - Get all projects with counts
- `getTags()` - Get all tags with counts
- `getSummary()` - Get task statistics summary

### Maintenance Operations
- `purgeTasks()` - Permanently delete all deleted tasks
- `restoreTask(taskId, uuid?)` - Restore a deleted task
- `restoreTasks(taskIds)` - Restore multiple deleted tasks

### MCPO-Specific Methods
- `invokeTool(toolName, args)` - Invoke any MCP tool
- `getServerInfo()` - Get MCP server information
- `listTools()` - List available MCP tools
- `health()` - Check server health

## Available Hooks

### Task Management Hooks
- `useListTasks(autoLoad?, params?)` - List tasks
- `useAddTask()` - Add new tasks
- `useModifyTask()` - Modify tasks
- `useCompleteTask()` - Complete tasks
- `useUncompleteTask()` - Uncomplete tasks
- `useDeleteTask()` - Delete tasks
- `useStartTask()` - Start task timers
- `useStopTask()` - Stop task timers
- `useBatchCompleteTasks()` - Batch complete tasks

### Metadata Hooks
- `useProjects(autoLoad?)` - Get projects
- `useTags(autoLoad?)` - Get tags
- `useSummary(autoLoad?)` - Get summary

### Utility Hooks
- `usePurgeTasks()` - Purge deleted tasks
- `useMCPOTool(toolName)` - Invoke custom tools
- `useMCPOServerInfo(autoLoad?)` - Get server info
- `useMCPOTools(autoLoad?)` - List available tools
- `useMCPOClient()` - Get client from context

## Error Handling

All methods and hooks provide structured error handling:

```typescript
const addTask = useAddTask();

const handleAdd = async () => {
  try {
    const result = await addTask.execute({ description: 'Task' });
    console.log('Success:', result);
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error message:', error.message);
    }
  }
};

// Or check the error state
if (addTask.error) {
  console.error('Operation failed:', addTask.error);
}
```

## Loading States

Hooks provide loading states for UI feedback:

```typescript
const { data, loading, error } = useListTasks();

return (
  <div>
    {loading && <Spinner />}
    {error && <ErrorMessage error={error} />}
    {data && <TaskList tasks={data.tasks} />}
  </div>
);
```

## TypeScript Support

All methods are fully typed:

```typescript
import type { Task, CreateTaskRequest } from '@/types/task';

const params: CreateTaskRequest = {
  description: 'Typed task',
  priority: 'H', // TypeScript will validate this
  tags: ['work']
};

const result = await mcpoClient.addTask(params);
// result is typed as ApiResponse<{ task: Task; message: string }>
```

## Switching Between API Implementations

You can easily switch between the traditional API and MCPO:

```typescript
// Traditional API (direct HTTP)
import taskWarriorAPI from '@/services/api';

// MCPO API (through MCPO server)
import { taskWarriorMCPOAPI } from '@/services/api-mcpo';

// Use the same interface
const api = useMCPO ? taskWarriorMCPOAPI : taskWarriorAPI;
await api.listTasks({ status: 'pending' });
```

## Example Component

See `/src/components/MCPOExample.tsx` for a complete working example that demonstrates:
- Using hooks for task management
- Direct client usage
- Error handling
- Loading states
- Direct tool invocation
- Server information display

## Best Practices

1. **Use Hooks in Components**: Prefer hooks for React components as they handle state management automatically
2. **Handle Errors**: Always handle errors gracefully with try-catch or error states
3. **Show Loading States**: Provide user feedback during async operations
4. **Type Your Data**: Use TypeScript types for better IDE support and error prevention
5. **Configure Once**: Use the MCPOProvider for app-wide configuration
6. **Cache Results**: Consider caching frequently accessed data like projects and tags
7. **Batch Operations**: Use batch methods when operating on multiple tasks

## Troubleshooting

### Connection Issues
```typescript
// Check server health
const health = await mcpoClient.health();
console.log('Server status:', health);
```

### Tool Discovery
```typescript
// List available tools
const tools = await mcpoClient.listTools();
console.log('Available tools:', tools);
```

### Debug Mode
```typescript
// Enable debug logging
const debugClient = new MCPOClient({
  baseURL: 'http://localhost:8085',
  headers: {
    'X-Debug': 'true'
  }
});
```

## Migration from Traditional API

To migrate from the traditional API to MCPO:

1. Replace imports:
```typescript
// Old
import taskWarriorAPI from '@/services/api';

// New
import { taskWarriorMCPOAPI } from '@/services/api-mcpo';
// Or use the client directly
import { mcpoClient } from '@/services/mcpo-client';
```

2. Update method calls (interface is mostly compatible):
```typescript
// Both work the same way
await taskWarriorAPI.listTasks({ status: 'pending' });
await taskWarriorMCPOAPI.listTasks({ status: 'pending' });
```

3. Use hooks for new components:
```typescript
const { data, loading, error } = useListTasks(true, { status: 'pending' });
```

The MCPO client maintains compatibility with the existing API interface while providing additional features like direct tool invocation and better TypeScript support.