/**
 * MCPO Client for TaskWarrior-NG
 * 
 * This client provides a typed interface to interact with MCPO (Model Context Protocol to OpenAPI)
 * server, allowing the frontend to invoke MCP tools directly through a REST API.
 */

import apiConfig from '@/config/api.config';
import type {
  Task,
  CreateTaskRequest,
  ModifyTaskRequest,
  ListTasksRequest,
  BatchFilterParams,
  BatchModifyParams,
  ApiResponse,
} from '@/types/task';

/**
 * MCPO Tool Request structure
 */
export interface MCPOToolRequest<T = any> {
  tool: string;
  arguments?: T;
}

/**
 * MCPO Tool Response structure
 */
export interface MCPOToolResponse<T = any> {
  success: boolean;
  result?: T;
  error?: string;
  content?: Array<{
    type: string;
    text?: string;
    data?: any;
  }>;
}

/**
 * MCPO Server Information
 */
export interface MCPOServerInfo {
  name: string;
  version: string;
  protocol_version: string;
  capabilities: {
    tools?: boolean;
    prompts?: boolean;
    resources?: boolean;
  };
}

/**
 * MCPO Tool Definition
 */
export interface MCPOTool {
  name: string;
  description?: string;
  inputSchema?: {
    type: string;
    properties?: Record<string, any>;
    required?: string[];
  };
}

/**
 * MCPO Client Configuration
 */
export interface MCPOClientConfig {
  baseURL?: string;
  apiKey?: string;
  timeout?: number;
  headers?: Record<string, string>;
}

/**
 * MCPO Client Class
 * 
 * Provides methods to interact with an MCPO server that wraps MCP servers
 * and exposes their functionality through a REST API.
 */
export class MCPOClient {
  private baseURL: string;
  private apiKey?: string;
  private timeout: number;
  private headers: Record<string, string>;

  constructor(config: MCPOClientConfig = {}) {
    // Use centralized API configuration
    this.baseURL = config.baseURL || apiConfig.apiUrl;
    this.apiKey = config.apiKey || apiConfig.apiKey;
    this.timeout = config.timeout || 30000;
    this.headers = {
      ...apiConfig.headers,
      ...config.headers,
    };
  }

  /**
   * Make a request to the MCPO server
   */
  private async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.headers,
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`MCPO request failed: ${response.status} ${errorText}`);
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error(`MCPO request timeout after ${this.timeout}ms`);
        }
        throw error;
      }
      throw new Error('Unknown error occurred');
    }
  }

  /**
   * Invoke an MCP tool through MCPO
   */
  async invokeTool<TArgs = any, TResult = any>(
    toolName: string,
    args?: TArgs
  ): Promise<MCPOToolResponse<TResult>> {
    // MCPO expects parameters in a 'params' field for direct tool endpoints
    const endpoint = `/${toolName}`;
    return this.request<MCPOToolResponse<TResult>>(endpoint, {
      method: 'POST',
      body: JSON.stringify({
        params: args,
      }),
    });
  }

  /**
   * Get server information
   */
  async getServerInfo(): Promise<MCPOServerInfo> {
    return this.request<MCPOServerInfo>('/server/info');
  }

  /**
   * List available tools
   */
  async listTools(): Promise<MCPOTool[]> {
    const response = await this.request<{ tools: MCPOTool[] }>('/tools');
    return response.tools || [];
  }

  /**
   * Health check
   * Note: MCPO may not have a dedicated health endpoint, 
   * so we use the OpenAPI spec endpoint as a health check
   */
  async health(): Promise<{ status: string; timestamp: string }> {
    try {
      // Try to fetch the OpenAPI spec as a health check
      await this.request('/openapi.json');
      return {
        status: 'healthy',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // ============================================
  // TaskWarrior-specific convenience methods
  // ============================================

  /**
   * Add a new task
   */
  async addTask(params: CreateTaskRequest): Promise<ApiResponse<{ task: Task; message: string }>> {
    const response = await this.invokeTool<CreateTaskRequest, any>('add_task', params);
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          task: response.task,
          message: response.message || 'Task created successfully',
        },
      };
    }
    
    throw new Error(response.error || 'Failed to add task');
  }

  /**
   * List tasks with optional filters
   */
  async listTasks(params: ListTasksRequest = {}): Promise<{ success: boolean; tasks: Task[]; count: number }> {
    const response = await this.invokeTool<ListTasksRequest, any>('list_tasks', params);
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        tasks: response.tasks || [],
        count: response.count || 0,
      };
    }
    
    return { success: false, tasks: [], count: 0 };
  }

  /**
   * Get a specific task
   */
  async getTask(taskId: number | string): Promise<ApiResponse<{ task: Task }>> {
    const response = await this.invokeTool<{ task_id: number | string }, any>('get_task', {
      task_id: taskId,
    });
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          task: response.task,
        },
      };
    }
    
    throw new Error(response.error || 'Failed to get task');
  }

  /**
   * Modify a task
   */
  async modifyTask(params: ModifyTaskRequest): Promise<ApiResponse<{ task: Task; message: string }>> {
    const response = await this.invokeTool<ModifyTaskRequest, any>('modify_task', params);
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          task: response.task,
          message: response.message || 'Task modified successfully',
        },
      };
    }
    
    throw new Error(response.error || 'Failed to modify task');
  }

  /**
   * Complete a task
   */
  async completeTask(taskId: number | string): Promise<ApiResponse<{ message: string }>> {
    const response = await this.invokeTool<{ task_id: number | string }, any>('complete_task', {
      task_id: taskId,
    });
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          message: response.message || 'Task completed successfully',
        },
      };
    }
    
    throw new Error(response.error || 'Failed to complete task');
  }

  /**
   * Uncomplete a task
   */
  async uncompleteTask(taskId: number | string, uuid?: string): Promise<ApiResponse<{ message: string; task: Task }>> {
    const params = uuid ? { uuid } : { task_id: taskId };
    const response = await this.invokeTool<any, any>('uncomplete_task', params);
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          message: response.message || 'Task uncompleted successfully',
          task: response.task,
        },
      };
    }
    
    throw new Error(response.error || 'Failed to uncomplete task');
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId: number | string): Promise<ApiResponse<{ message: string }>> {
    const response = await this.invokeTool<{ task_id: number | string }, any>('delete_task', {
      task_id: taskId,
    });
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          message: response.message || 'Task deleted successfully',
        },
      };
    }
    
    throw new Error(response.error || 'Failed to delete task');
  }

  /**
   * Start a task
   */
  async startTask(taskId: number | string): Promise<ApiResponse<{ message: string; task: Task }>> {
    const response = await this.invokeTool<{ task_id: number | string }, any>('start_task', {
      task_id: taskId,
    });
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          message: response.message || 'Task started successfully',
          task: response.task,
        },
      };
    }
    
    throw new Error(response.error || 'Failed to start task');
  }

  /**
   * Stop a task
   */
  async stopTask(taskId: number | string): Promise<ApiResponse<{ message: string; task: Task }>> {
    const response = await this.invokeTool<{ task_id: number | string }, any>('stop_task', {
      task_id: taskId,
    });
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          message: response.message || 'Task stopped successfully',
          task: response.task,
        },
      };
    }
    
    throw new Error(response.error || 'Failed to stop task');
  }

  /**
   * Batch complete tasks
   */
  async batchCompleteTasks(taskIds: (number | string)[]): Promise<ApiResponse<any>> {
    const response = await this.invokeTool<{ task_ids: (number | string)[] }, any>('batch_complete_tasks', {
      task_ids: taskIds,
    });
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: response,
      };
    }
    
    throw new Error(response.error || 'Failed to batch complete tasks');
  }

  /**
   * Batch complete tasks by filter
   */
  async batchCompleteByFilter(filters: BatchFilterParams): Promise<ApiResponse<any>> {
    const response = await this.invokeTool<BatchFilterParams, any>('batch_complete_by_filter', filters);
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: response,
      };
    }
    
    throw new Error(response.error || 'Failed to batch complete tasks by filter');
  }

  /**
   * Get projects
   */
  async getProjects(): Promise<ApiResponse<{ projects: Array<{ name: string; count: number }> }>> {
    const response = await this.invokeTool<undefined, any>('get_projects');
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          projects: response.projects || [],
        },
      };
    }
    
    throw new Error(response.error || 'Failed to get projects');
  }

  /**
   * Get tags
   */
  async getTags(): Promise<ApiResponse<{ tags: Array<{ name: string; count: number }> }>> {
    const response = await this.invokeTool<undefined, any>('get_tags');
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          tags: response.tags || [],
        },
      };
    }
    
    throw new Error(response.error || 'Failed to get tags');
  }

  /**
   * Get summary
   */
  async getSummary(): Promise<ApiResponse<any>> {
    const response = await this.invokeTool<undefined, any>('get_summary');
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: response,
      };
    }
    
    throw new Error(response.error || 'Failed to get summary');
  }

  /**
   * Purge deleted tasks
   */
  async purgeTasks(): Promise<ApiResponse<{ message: string; purged_count: number }>> {
    const response = await this.invokeTool<undefined, any>('purge_tasks');
    
    // MCPO returns the result directly
    if (response.success) {
      return {
        success: response.success,
        data: {
          message: response.message || 'Tasks purged successfully',
          purged_count: response.purged_count || 0,
        },
      };
    }
    
    throw new Error(response.error || 'Failed to purge tasks');
  }
}

// Export a singleton instance for convenience
export const mcpoClient = new MCPOClient();

// Export default
export default MCPOClient;