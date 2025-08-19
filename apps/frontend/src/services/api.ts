// TaskWarrior API client for MCP server communication via bridge
import apiConfig, { apiRequest, invokeMCPOTool } from '@/config/api.config';
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

class TaskWarriorAPI {
  // Use the centralized API configuration
  private get baseURL(): string {
    return apiConfig.apiUrl;
  }

  private get apiKey(): string | undefined {
    return apiConfig.apiKey;
  }

  private async request<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Use the centralized apiRequest function
    return apiRequest<T>(endpoint, options);
  }

  // Helper method for MCPO tool invocation
  private async invokeTool<T = any>(toolName: string, params?: any): Promise<T> {
    // Use the centralized invokeMCPOTool function
    return invokeMCPOTool<T>(toolName, params);
  }

  // Basic CRUD Operations
  async addTask(params: CreateTaskRequest): Promise<ApiResponse<{ task: Task; message: string }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('add_task', params);
      return {
        success: result.success,
        data: {
          task: result.task,
          message: result.message,
        },
      };
    }
    return this.request('/tasks', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async listTasks(params: ListTasksRequest = {}): Promise<TaskListResponse> {
    if (this.apiKey) {
      return this.invokeTool('list_tasks', params);
    }
    const searchParams = new URLSearchParams();
    if (params.status) searchParams.set('status', params.status);
    if (params.project) searchParams.set('project', params.project);
    if (params.tags?.length) searchParams.set('tags', params.tags.join(','));
    if (params.limit) searchParams.set('limit', params.limit.toString());

    const query = searchParams.toString();
    return this.request(`/tasks${query ? `?${query}` : ''}`);
  }

  async getTask(taskId: number): Promise<ApiResponse<{ task: Task }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('get_task', { task_id: taskId });
      return {
        success: result.success,
        data: {
          task: result.task,
        },
      };
    }
    return this.request(`/tasks/${taskId}`);
  }

  async modifyTask(params: ModifyTaskRequest): Promise<ApiResponse<{ task: Task; message: string }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('modify_task', params);
      return {
        success: result.success,
        data: {
          task: result.task,
          message: result.message,
        },
      };
    }
    const { task_id, ...updateData } = params;
    return this.request(`/tasks/${task_id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async completeTask(taskId: number): Promise<ApiResponse<{ message: string }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('complete_task', { task_id: taskId });
      return {
        success: result.success,
        data: {
          message: result.message,
        },
      };
    }
    return this.request(`/tasks/${taskId}/complete`, {
      method: 'POST',
    });
  }

  async uncompleteTask(taskId: number, uuid?: string): Promise<ApiResponse<{ message: string; task: Task }>> {
    if (this.apiKey) {
      const params = uuid ? { uuid } : { task_id: taskId };
      const result = await this.invokeTool<any>('uncomplete_task', params);
      return {
        success: result.success,
        data: {
          message: result.message,
          task: result.task,
        },
      };
    }
    // If we have a UUID, use it as it's more reliable for completed tasks
    const endpoint = uuid ? `/tasks/${uuid}/uncomplete` : `/tasks/${taskId}/uncomplete`;
    return this.request(endpoint, {
      method: 'POST',
      body: uuid ? JSON.stringify({ uuid }) : undefined,
    });
  }

  async deleteTask(taskId: number): Promise<ApiResponse<{ message: string }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('delete_task', { task_id: taskId });
      return {
        success: result.success,
        data: {
          message: result.message,
        },
      };
    }
    return this.request(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async startTask(taskId: number): Promise<ApiResponse<{ message: string; task: Task }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('start_task', { task_id: taskId });
      return {
        success: result.success,
        data: {
          message: result.message,
          task: result.task,
        },
      };
    }
    return this.request(`/tasks/${taskId}/start`, {
      method: 'POST',
    });
  }

  async stopTask(taskId: number): Promise<ApiResponse<{ message: string; task: Task }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('stop_task', { task_id: taskId });
      return {
        success: result.success,
        data: {
          message: result.message,
          task: result.task,
        },
      };
    }
    return this.request(`/tasks/${taskId}/stop`, {
      method: 'POST',
    });
  }

  // Batch Operations
  async batchCompleteByIds(taskIds: number[]): Promise<ApiResponse<{ completed_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/complete', {
      method: 'POST',
      body: JSON.stringify({ task_ids: taskIds }),
    });
  }

  async batchCompleteByFilter(filters: BatchFilterParams): Promise<ApiResponse<{ completed_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/complete-filter', {
      method: 'POST',
      body: JSON.stringify(filters),
    });
  }

  async batchUncompleteByIds(taskIds: number[], taskUuids?: Record<number, string>): Promise<ApiResponse<{ uncompleted_count: number; results: any[]; errors: string[] }>> {
    // If we have UUIDs, include them in the request
    const body: any = { task_ids: taskIds };
    if (taskUuids) {
      body.task_uuids = taskUuids;
    }
    return this.request('/tasks/batch/uncomplete', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async batchUncompleteByFilter(filters: BatchFilterParams): Promise<ApiResponse<{ uncompleted_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/uncomplete-filter', {
      method: 'POST',
      body: JSON.stringify(filters),
    });
  }

  async batchDeleteByIds(taskIds: number[]): Promise<ApiResponse<{ deleted_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/delete', {
      method: 'POST',
      body: JSON.stringify({ task_ids: taskIds }),
    });
  }

  async batchDeleteByFilter(filters: BatchFilterParams): Promise<ApiResponse<{ deleted_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/delete-filter', {
      method: 'POST',
      body: JSON.stringify(filters),
    });
  }

  async batchStartByIds(taskIds: number[]): Promise<ApiResponse<{ started_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/start', {
      method: 'POST',
      body: JSON.stringify({ task_ids: taskIds }),
    });
  }

  async batchStopByIds(taskIds: number[]): Promise<ApiResponse<{ stopped_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/stop', {
      method: 'POST',
      body: JSON.stringify({ task_ids: taskIds }),
    });
  }

  async batchModifyTasks(params: BatchModifyParams): Promise<ApiResponse<{ modified_count: number; results: any[]; errors: string[] }>> {
    return this.request('/tasks/batch/modify', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Metadata Operations
  async getProjects(): Promise<ProjectsResponse> {
    // Check if we're using MCPO (has API key)
    if (this.apiKey) {
      return this.invokeTool('get_projects');
    }
    return this.request('/projects');
  }

  async getTags(): Promise<TagsResponse> {
    // Check if we're using MCPO (has API key)
    if (this.apiKey) {
      return this.invokeTool('get_tags');
    }
    return this.request('/tags');
  }

  async getSummary(): Promise<SummaryResponse> {
    // Check if we're using MCPO (has API key)
    if (this.apiKey) {
      return this.invokeTool('get_summary');
    }
    return this.request('/summary');
  }

  // Task Restoration
  async restoreTask(taskIdOrUuid: number | string, status?: string): Promise<ApiResponse<{ task: Task; message: string }>> {
    return this.request(`/tasks/${taskIdOrUuid}/restore`, {
      method: 'POST',
      body: JSON.stringify({ status: status || 'pending' }),
    });
  }

  // Database Maintenance
  async purgeDeletedTasks(): Promise<ApiResponse<{ purged_count: number; message: string; details?: string }>> {
    if (this.apiKey) {
      const result = await this.invokeTool<any>('purge_tasks');
      return {
        success: result.success,
        data: {
          purged_count: result.purged_count || 0,
          message: result.message,
          details: result.details,
        },
      };
    }
    return this.request('/tasks/purge', {
      method: 'POST',
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; service: string; version: string }> {
    const baseUrl = this.baseURL.replace('/api', '');
    const response = await fetch(`${baseUrl}/health`);
    return response.json();
  }

  // Get current API URL (useful for debugging)
  getApiUrl(): string {
    return this.baseURL;
  }
}

// Export singleton instance
export const taskWarriorAPI = new TaskWarriorAPI();