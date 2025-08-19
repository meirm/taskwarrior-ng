/**
 * Example Component demonstrating MCPO Client usage
 * 
 * This component shows different ways to use the MCPO client:
 * - Direct client usage
 * - Using React hooks
 * - Error handling
 * - Loading states
 */

import React, { useState } from 'react';
import { mcpoClient } from '@/services/mcpo-client';
import { 
  useListTasks, 
  useAddTask, 
  useCompleteTask,
  useMCPOServerInfo,
  useMCPOTools,
  useMCPOTool
} from '@/hooks/useMCPO';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/Badge';
import { Loader2, Plus, Check, Info, Wrench, RefreshCw } from 'lucide-react';

export function MCPOExample() {
  const [taskDescription, setTaskDescription] = useState('');
  const [directToolName, setDirectToolName] = useState('');
  const [directToolArgs, setDirectToolArgs] = useState('{}');
  
  // Using hooks for common operations
  const listTasks = useListTasks(false, { status: 'pending', limit: 5 });
  const addTask = useAddTask();
  const completeTask = useCompleteTask();
  
  // Using hooks for server info
  const serverInfo = useMCPOServerInfo(true);
  const availableTools = useMCPOTools(true);
  
  // Using generic tool hook
  const customTool = useMCPOTool(directToolName);

  // Handle adding a new task
  const handleAddTask = async () => {
    if (!taskDescription.trim()) return;
    
    try {
      await addTask.execute({
        description: taskDescription,
        priority: 'M',
        tags: ['mcpo-example'],
      });
      
      setTaskDescription('');
      // Refresh the task list
      await listTasks.execute();
    } catch (error) {
      console.error('Failed to add task:', error);
    }
  };

  // Handle completing a task
  const handleCompleteTask = async (taskId: number) => {
    try {
      await completeTask.execute(taskId);
      // Refresh the task list
      await listTasks.execute();
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  // Handle direct tool invocation
  const handleDirectToolInvocation = async () => {
    if (!directToolName) return;
    
    try {
      const args = JSON.parse(directToolArgs);
      await customTool.execute(args);
    } catch (error) {
      console.error('Failed to invoke tool:', error);
    }
  };

  // Direct client usage example
  const handleDirectClientExample = async () => {
    try {
      // Example of using the client directly without hooks
      const summary = await mcpoClient.getSummary();
      console.log('Summary fetched directly:', summary);
      
      const projects = await mcpoClient.getProjects();
      console.log('Projects fetched directly:', projects);
    } catch (error) {
      console.error('Direct client error:', error);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">MCPO Client Example</h1>
      
      {/* Server Information */}
      <Card className="p-4">
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Info className="w-5 h-5" />
          Server Information
        </h2>
        {serverInfo.loading ? (
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading server info...
          </div>
        ) : serverInfo.error ? (
          <div className="text-red-500">Error: {serverInfo.error.message}</div>
        ) : serverInfo.data ? (
          <div className="space-y-2">
            <div>Name: {serverInfo.data.name}</div>
            <div>Version: {serverInfo.data.version}</div>
            <div>Protocol: {serverInfo.data.protocol_version}</div>
            <div className="flex gap-2">
              Capabilities:
              {serverInfo.data.capabilities.tools && <Badge>Tools</Badge>}
              {serverInfo.data.capabilities.prompts && <Badge>Prompts</Badge>}
              {serverInfo.data.capabilities.resources && <Badge>Resources</Badge>}
            </div>
          </div>
        ) : null}
      </Card>

      {/* Task Management with Hooks */}
      <Card className="p-4">
        <h2 className="text-lg font-semibold mb-3">Task Management (Using Hooks)</h2>
        
        {/* Add Task */}
        <div className="flex gap-2 mb-4">
          <Input
            value={taskDescription}
            onChange={(e) => setTaskDescription(e.target.value)}
            placeholder="Enter task description..."
            onKeyPress={(e) => e.key === 'Enter' && handleAddTask()}
          />
          <Button 
            onClick={handleAddTask}
            disabled={addTask.loading || !taskDescription.trim()}
          >
            {addTask.loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            Add Task
          </Button>
        </div>
        
        {addTask.error && (
          <div className="text-red-500 text-sm mb-2">Error: {addTask.error.message}</div>
        )}
        
        {/* List Tasks */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="font-medium">Recent Tasks</h3>
            <Button
              size="sm"
              variant="outline"
              onClick={() => listTasks.execute()}
              disabled={listTasks.loading}
            >
              {listTasks.loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4" />
              )}
              Refresh
            </Button>
          </div>
          
          {listTasks.loading && !listTasks.data ? (
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading tasks...
            </div>
          ) : listTasks.error ? (
            <div className="text-red-500">Error: {listTasks.error.message}</div>
          ) : listTasks.data ? (
            <div className="space-y-2">
              {listTasks.data.tasks.length === 0 ? (
                <div className="text-gray-500">No pending tasks</div>
              ) : (
                listTasks.data.tasks.map((task) => (
                  <div key={task.id} className="flex items-center justify-between p-2 border rounded">
                    <div>
                      <span className="font-medium">{task.description}</span>
                      {task.priority && (
                        <Badge className="ml-2" variant={
                          task.priority === 'H' ? 'destructive' : 
                          task.priority === 'M' ? 'default' : 
                          'secondary'
                        }>
                          Priority: {task.priority}
                        </Badge>
                      )}
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleCompleteTask(task.id)}
                      disabled={completeTask.loading}
                    >
                      {completeTask.loading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Check className="w-4 h-4" />
                      )}
                      Complete
                    </Button>
                  </div>
                ))
              )}
            </div>
          ) : null}
        </div>
      </Card>

      {/* Available Tools */}
      <Card className="p-4">
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Wrench className="w-5 h-5" />
          Available MCP Tools
        </h2>
        {availableTools.loading ? (
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading tools...
          </div>
        ) : availableTools.error ? (
          <div className="text-red-500">Error: {availableTools.error.message}</div>
        ) : availableTools.data ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {availableTools.data.map((tool) => (
              <Badge key={tool.name} variant="outline">
                {tool.name}
              </Badge>
            ))}
          </div>
        ) : null}
      </Card>

      {/* Direct Tool Invocation */}
      <Card className="p-4">
        <h2 className="text-lg font-semibold mb-3">Direct Tool Invocation</h2>
        <div className="space-y-2">
          <Input
            value={directToolName}
            onChange={(e) => setDirectToolName(e.target.value)}
            placeholder="Tool name (e.g., get_summary)"
          />
          <textarea
            className="w-full p-2 border rounded"
            rows={3}
            value={directToolArgs}
            onChange={(e) => setDirectToolArgs(e.target.value)}
            placeholder="Tool arguments (JSON)"
          />
          <Button
            onClick={handleDirectToolInvocation}
            disabled={customTool.loading || !directToolName}
          >
            {customTool.loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : null}
            Invoke Tool
          </Button>
          
          {customTool.data && (
            <div className="mt-2 p-2 bg-gray-100 rounded">
              <pre className="text-xs overflow-auto">
                {JSON.stringify(customTool.data, null, 2)}
              </pre>
            </div>
          )}
          
          {customTool.error && (
            <div className="text-red-500 text-sm">Error: {customTool.error.message}</div>
          )}
        </div>
      </Card>

      {/* Direct Client Usage */}
      <Card className="p-4">
        <h2 className="text-lg font-semibold mb-3">Direct Client Usage</h2>
        <p className="text-sm text-gray-600 mb-2">
          Check the console for results when using the client directly
        </p>
        <Button onClick={handleDirectClientExample}>
          Fetch Data Directly (Check Console)
        </Button>
      </Card>
    </div>
  );
}