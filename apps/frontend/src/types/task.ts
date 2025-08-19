// TaskWarrior task types matching the MCP server TaskModel
export type TaskStatus = 'pending' | 'completed' | 'deleted' | 'waiting';
export type TaskPriority = 'H' | 'M' | 'L' | null;

export interface Task {
  id?: number;
  uuid?: string;
  description: string;
  status: TaskStatus;
  project?: string;
  priority?: TaskPriority;
  tags: string[];
  urgency: number;
  entry?: string;
  modified?: string;
  due?: string;
  start?: string;
  end?: string;
  wait?: string;
  until?: string;
  annotations: TaskAnnotation[];
  depends: string[];
  recur?: string;
}

export interface TaskAnnotation {
  entry?: string;
  description: string;
}

export interface CreateTaskRequest {
  description: string;
  project?: string;
  priority?: TaskPriority;
  tags?: string[];
  due?: string;
}

export interface ModifyTaskRequest {
  task_id: number;
  description?: string;
  project?: string;
  priority?: TaskPriority;
  tags?: string[];
  due?: string;
}

export interface ListTasksRequest {
  status?: TaskStatus;
  project?: string;
  tags?: string[];
  limit?: number;
}

export interface BatchFilterParams {
  status?: TaskStatus;
  project?: string;
  tags?: string[];
  priority?: TaskPriority;
  description_contains?: string;
  due_before?: string;
  due_after?: string;
  limit?: number;
}

export interface BatchModifyParams {
  task_ids?: number[];
  filters?: BatchFilterParams;
  project?: string;
  priority?: TaskPriority;
  add_tags?: string[];
  remove_tags?: string[];
  due?: string;
}

export interface TaskSummary {
  status: {
    pending: number;
    completed: number;
    deleted: number;
    total: number;
  };
  priority: {
    H: number;
    M: number;
    L: number;
    None: number;
  };
  overdue: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface TaskListResponse extends ApiResponse {
  tasks: Task[];
  count: number;
}

export interface ProjectsResponse extends ApiResponse {
  projects: string[];
  count: number;
}

export interface TagsResponse extends ApiResponse {
  tags: string[];
  count: number;
}

export interface SummaryResponse extends ApiResponse {
  summary: TaskSummary;
}