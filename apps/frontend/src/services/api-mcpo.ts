/**
 * TaskWarrior API client using MCPO
 * 
 * This is an alternative implementation of the API service that uses the MCPO client
 * instead of direct HTTP requests. It maintains the same interface as the original
 * api.ts file for easy swapping.
 */

import { MCPOClient } from './mcpo-client';
import apiConfig from '@/config/api.config';
import type {
  Task,
  CreateTaskRequest,
  ModifyTaskRequest,
  ListTasksRequest,
  BatchFilterParams,
  BatchModifyParams,
  TaskListResponse,
  ProjectsResponse,
  TagsResponse,
  SummaryResponse,
  ApiResponse,
} from '@/types/task';

class TaskWarriorMCPOAPI {
  private client: MCPOClient;

  constructor() {
    // Initialize MCPO client with centralized API configuration
    this.client = new MCPOClient({
      baseURL: apiConfig.apiUrl,
      apiKey: apiConfig.apiKey,
    });
  }

  // Basic CRUD Operations
  async addTask(params: CreateTaskRequest): Promise<ApiResponse<{ task: Task; message: string }>> {
    return this.client.addTask(params);
  }

  async listTasks(params: ListTasksRequest = {}): Promise<TaskListResponse> {
    const result = await this.client.listTasks(params);
    return {
      success: result.success,
      tasks: result.tasks,
      count: result.count,
    };
  }

  async getTask(taskId: number): Promise<ApiResponse<{ task: Task }>> {
    return this.client.getTask(taskId);
  }

  async modifyTask(params: ModifyTaskRequest): Promise<ApiResponse<{ task: Task; message: string }>> {
    return this.client.modifyTask(params);
  }

  async completeTask(taskId: number): Promise<ApiResponse<{ message: string }>> {
    return this.client.completeTask(taskId);
  }

  async uncompleteTask(taskId: number, uuid?: string): Promise<ApiResponse<{ message: string; task: Task }>> {
    return this.client.uncompleteTask(taskId, uuid);
  }

  async deleteTask(taskId: number): Promise<ApiResponse<{ message: string }>> {
    return this.client.deleteTask(taskId);
  }

  async startTask(taskId: number): Promise<ApiResponse<{ message: string; task: Task }>> {
    return this.client.startTask(taskId);
  }

  async stopTask(taskId: number): Promise<ApiResponse<{ message: string; task: Task }>> {
    return this.client.stopTask(taskId);
  }

  // Batch Operations
  async batchCompleteTasks(taskIds: number[]): Promise<ApiResponse<any>> {
    return this.client.batchCompleteTasks(taskIds);
  }

  async batchUncompleteTask(taskIds: number[]): Promise<ApiResponse<any>> {
    // Use batch_uncomplete_tasks tool
    const response = await this.client.invokeTool<{ task_ids: number[] }, any>('batch_uncomplete_tasks', {
      task_ids: taskIds,
    });
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to batch uncomplete tasks');
  }

  async batchCompleteByFilter(filters: BatchFilterParams): Promise<ApiResponse<any>> {
    return this.client.batchCompleteByFilter(filters);
  }

  async batchUncompleteByFilter(filters: BatchFilterParams): Promise<ApiResponse<any>> {
    const response = await this.client.invokeTool<BatchFilterParams, any>('batch_uncomplete_by_filter', filters);
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to batch uncomplete by filter');
  }

  async batchDeleteTasks(taskIds: number[]): Promise<ApiResponse<any>> {
    const response = await this.client.invokeTool<{ task_ids: number[] }, any>('batch_delete_tasks', {
      task_ids: taskIds,
    });
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to batch delete tasks');
  }

  async batchDeleteByFilter(filters: BatchFilterParams): Promise<ApiResponse<any>> {
    const response = await this.client.invokeTool<BatchFilterParams, any>('batch_delete_by_filter', filters);
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to batch delete by filter');
  }

  async batchStartTasks(taskIds: number[]): Promise<ApiResponse<any>> {
    const response = await this.client.invokeTool<{ task_ids: number[] }, any>('batch_start_tasks', {
      task_ids: taskIds,
    });
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to batch start tasks');
  }

  async batchStopTasks(taskIds: number[]): Promise<ApiResponse<any>> {
    const response = await this.client.invokeTool<{ task_ids: number[] }, any>('batch_stop_tasks', {
      task_ids: taskIds,
    });
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to batch stop tasks');
  }

  async batchModifyTasks(params: BatchModifyParams): Promise<ApiResponse<any>> {
    const response = await this.client.invokeTool<BatchModifyParams, any>('batch_modify_tasks', params);
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to batch modify tasks');
  }

  // Metadata Operations
  async getProjects(): Promise<ProjectsResponse> {
    const result = await this.client.getProjects();
    return {
      success: result.success,
      projects: result.data?.projects || [],
    };
  }

  async getTags(): Promise<TagsResponse> {
    const result = await this.client.getTags();
    return {
      success: result.success,
      tags: result.data?.tags || [],
    };
  }

  async getSummary(): Promise<SummaryResponse> {
    const result = await this.client.getSummary();
    return {
      success: result.success,
      summary: result.data || {},
    };
  }

  // Maintenance Operations
  async purgeTasks(): Promise<ApiResponse<{ message: string; purged_count: number }>> {
    return this.client.purgeTasks();
  }

  // Restore Task Operation (for trash recovery)
  async restoreTask(taskId: number | string, uuid?: string): Promise<ApiResponse<{ message: string; task: Task }>> {
    const params = uuid ? { uuid } : { task_id: taskId };
    const response = await this.client.invokeTool<any, any>('restore_task', params);
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: {
          message: result.message || 'Task restored successfully',
          task: result.task,
        },
      };
    }
    
    throw new Error(response.error || 'Failed to restore task');
  }

  // Restore Multiple Tasks
  async restoreTasks(taskIds: (number | string)[]): Promise<ApiResponse<any>> {
    const response = await this.client.invokeTool<{ task_ids: (number | string)[] }, any>('batch_restore_tasks', {
      task_ids: taskIds,
    });
    
    if (response.success && response.content?.[0]?.text) {
      const result = JSON.parse(response.content[0].text);
      return {
        success: result.success,
        data: result,
      };
    }
    
    throw new Error(response.error || 'Failed to restore tasks');
  }
}

// Export singleton instance
export const taskWarriorMCPOAPI = new TaskWarriorMCPOAPI();

// Export class
export default TaskWarriorMCPOAPI;