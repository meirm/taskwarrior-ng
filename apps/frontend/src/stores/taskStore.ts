// Task state management with Zustand
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Task, TaskStatus, TaskSummary } from '@/types/task';
import { taskWarriorAPI } from '@/services/api';

interface TaskState {
  // Data
  tasks: Task[];
  projects: string[];
  tags: string[];
  summary: TaskSummary | null;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedTasks: Set<number>;
  currentFilter: {
    status: TaskStatus | 'all';
    project: string | 'all';
    priority: 'H' | 'M' | 'L' | 'none' | 'all';
    search: string;
  };
  
  // Form State
  isTaskFormOpen: boolean;
  editingTask: Task | null;
  
  // Actions
  loadTasks: () => Promise<void>;
  loadMetadata: () => Promise<void>;
  addTask: (description: string, options?: {
    project?: string;
    priority?: 'H' | 'M' | 'L';
    tags?: string[];
    due?: string;
  }) => Promise<void>;
  updateTask: (taskId: number, updates: Partial<Task>) => Promise<void>;
  completeTask: (taskId: number) => Promise<void>;
  uncompleteTask: (taskId: number) => Promise<void>;
  deleteTask: (taskId: number) => Promise<void>;
  startTask: (taskId: number) => Promise<void>;
  stopTask: (taskId: number) => Promise<void>;
  
  // Batch operations
  batchComplete: (taskIds: number[]) => Promise<void>;
  batchUncomplete: (taskIds: number[]) => Promise<void>;
  batchDelete: (taskIds: number[]) => Promise<void>;
  batchStart: (taskIds: number[]) => Promise<void>;
  batchStop: (taskIds: number[]) => Promise<void>;
  
  // Selection
  toggleTaskSelection: (taskId: number) => void;
  selectAllTasks: (taskIds?: number[]) => void;
  clearSelection: () => void;
  
  // Filtering
  setFilter: (filter: Partial<TaskState['currentFilter']>) => void;
  
  // Form Management
  openTaskForm: (task?: Task) => void;
  closeTaskForm: () => void;
  
  // Utilities
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useTaskStore = create<TaskState>()(
  devtools(
    (set, get) => ({
      // Initial state
      tasks: [],
      projects: [],
      tags: [],
      summary: null,
      isLoading: false,
      error: null,
      selectedTasks: new Set(),
      currentFilter: {
        status: 'all' as const,
        project: 'all',
        priority: 'all',
        search: '',
      },
      isTaskFormOpen: false,
      editingTask: null,

      // Load tasks from API
      loadTasks: async () => {
        set({ isLoading: true, error: null });
        try {
          const { currentFilter } = get();
          const response = await taskWarriorAPI.listTasks({
            status: currentFilter.status === 'all' ? undefined : currentFilter.status,
            project: currentFilter.project === 'all' ? undefined : currentFilter.project,
          });

          if (response.success) {
            let tasks = response.tasks;
            
            // For tasks without valid IDs (like completed tasks), use UUID-based IDs
            tasks = tasks.map(task => {
              if (!task.id || task.id === 0) {
                // Generate a unique identifier based on UUID for tasks without IDs
                // This is common for completed tasks in TaskWarrior
                if (task.uuid) {
                  // Use a hash of the UUID to create a numeric-like ID
                  // This ensures consistency across reloads
                  const hashCode = task.uuid.split('').reduce((acc, char) => {
                    return Math.abs((acc * 31 + char.charCodeAt(0)) | 0);
                  }, 0);
                  return { ...task, id: hashCode };
                }
              }
              return task;
            });
            
            // Check for duplicate or missing IDs in development
            if (process.env.NODE_ENV === 'development') {
              const idCounts = new Map<any, number>();
              tasks.forEach((task, index) => {
                const key = task.id ?? 'undefined';
                idCounts.set(key, (idCounts.get(key) || 0) + 1);
                if (!task.id) {
                  console.warn(`Task at index ${index} has no ID, UUID:`, task.uuid);
                }
              });
              
              idCounts.forEach((count, id) => {
                if (count > 1 && id !== 'undefined') {
                  console.error(`Duplicate task ID found: ${id} appears ${count} times`);
                }
              });
            }
            
            // Filter by priority on client side
            if (currentFilter.priority !== 'all') {
              if (currentFilter.priority === 'none') {
                tasks = tasks.filter(t => !t.priority || t.priority === null);
              } else {
                tasks = tasks.filter(t => t.priority === currentFilter.priority);
              }
            }
            
            // Filter by search term if present
            if (currentFilter.search) {
              const searchLower = currentFilter.search.toLowerCase();
              tasks = tasks.filter(t => 
                t.description.toLowerCase().includes(searchLower) ||
                t.project?.toLowerCase().includes(searchLower) ||
                t.tags.some(tag => tag.toLowerCase().includes(searchLower))
              );
            }
            
            set({ tasks, isLoading: false });
          } else {
            set({ error: response.error || 'Failed to load tasks', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      // Load metadata (projects, tags, summary)
      loadMetadata: async () => {
        try {
          const [projectsRes, tagsRes, summaryRes] = await Promise.all([
            taskWarriorAPI.getProjects(),
            taskWarriorAPI.getTags(),
            taskWarriorAPI.getSummary(),
          ]);

          set({
            projects: projectsRes.success ? projectsRes.projects : [],
            tags: tagsRes.success ? tagsRes.tags : [],
            summary: summaryRes.success ? summaryRes.summary : null,
          });
        } catch (error) {
          console.error('Failed to load metadata:', error);
        }
      },

      // Add new task
      addTask: async (description, options = {}) => {
        set({ isLoading: true, error: null });
        try {
          const response = await taskWarriorAPI.addTask({
            description,
            ...options,
          });

          if (response.success) {
            // Reload tasks to get updated list
            await get().loadTasks();
            await get().loadMetadata();
          } else {
            set({ error: response.error || 'Failed to add task', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      // Update existing task
      updateTask: async (taskId, updates) => {
        set({ isLoading: true, error: null });
        try {
          const response = await taskWarriorAPI.modifyTask({
            task_id: taskId,
            ...updates,
          });

          if (response.success) {
            await get().loadTasks();
            await get().loadMetadata();
          } else {
            set({ error: response.error || 'Failed to update task', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      // Complete task
      completeTask: async (taskId) => {
        set({ isLoading: true, error: null });
        try {
          const response = await taskWarriorAPI.completeTask(taskId);
          if (response.success) {
            await get().loadTasks();
            await get().loadMetadata();
          } else {
            set({ error: response.error || 'Failed to complete task', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      // Uncomplete task
      uncompleteTask: async (taskId) => {
        set({ isLoading: true, error: null });
        try {
          // Find the task to get its UUID
          const task = get().tasks.find(t => t.id === taskId);
          const uuid = task?.uuid;
          
          const response = await taskWarriorAPI.uncompleteTask(taskId, uuid);
          if (response.success) {
            await get().loadTasks();
            await get().loadMetadata();
          } else {
            set({ error: response.error || 'Failed to uncomplete task', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      // Delete task
      deleteTask: async (taskId) => {
        set({ isLoading: true, error: null });
        try {
          const response = await taskWarriorAPI.deleteTask(taskId);
          if (response.success) {
            await get().loadTasks();
            await get().loadMetadata();
          } else {
            set({ error: response.error || 'Failed to delete task', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      // Start task (time tracking)
      startTask: async (taskId) => {
        try {
          const response = await taskWarriorAPI.startTask(taskId);
          if (response.success) {
            await get().loadTasks();
          } else {
            set({ error: response.error || 'Failed to start task' });
          }
        } catch (error) {
          set({ error: (error as Error).message });
        }
      },

      // Stop task (time tracking)
      stopTask: async (taskId) => {
        try {
          const response = await taskWarriorAPI.stopTask(taskId);
          if (response.success) {
            await get().loadTasks();
          } else {
            set({ error: response.error || 'Failed to stop task' });
          }
        } catch (error) {
          set({ error: (error as Error).message });
        }
      },

      // Batch operations
      batchComplete: async (taskIds) => {
        set({ isLoading: true, error: null });
        try {
          const response = await taskWarriorAPI.batchCompleteByIds(taskIds);
          if (response.success) {
            await get().loadTasks();
            await get().loadMetadata();
            set({ selectedTasks: new Set() });
          } else {
            set({ error: response.error || 'Failed to complete tasks', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      batchUncomplete: async (taskIds) => {
        set({ isLoading: true, error: null });
        try {
          // Build a map of task IDs to UUIDs for better reliability
          const taskUuids: Record<number, string> = {};
          const tasks = get().tasks;
          taskIds.forEach(id => {
            const task = tasks.find(t => t.id === id);
            if (task?.uuid) {
              taskUuids[id] = task.uuid;
            }
          });
          
          const response = await taskWarriorAPI.batchUncompleteByIds(taskIds, taskUuids);
          if (response.success) {
            await get().loadTasks();
            await get().loadMetadata();
            set({ selectedTasks: new Set() });
          } else {
            set({ error: response.error || 'Failed to uncomplete tasks', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      batchDelete: async (taskIds) => {
        set({ isLoading: true, error: null });
        try {
          const response = await taskWarriorAPI.batchDeleteByIds(taskIds);
          if (response.success) {
            await get().loadTasks();
            await get().loadMetadata();
            set({ selectedTasks: new Set() });
          } else {
            set({ error: response.error || 'Failed to delete tasks', isLoading: false });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
        }
      },

      batchStart: async (taskIds) => {
        try {
          const response = await taskWarriorAPI.batchStartByIds(taskIds);
          if (response.success) {
            await get().loadTasks();
          } else {
            set({ error: response.error || 'Failed to start tasks' });
          }
        } catch (error) {
          set({ error: (error as Error).message });
        }
      },

      batchStop: async (taskIds) => {
        try {
          const response = await taskWarriorAPI.batchStopByIds(taskIds);
          if (response.success) {
            await get().loadTasks();
          } else {
            set({ error: response.error || 'Failed to stop tasks' });
          }
        } catch (error) {
          set({ error: (error as Error).message });
        }
      },

      // Selection management
      toggleTaskSelection: (taskId) => {
        if (!taskId) return;
        
        set((state) => {
          const newSelection = new Set(state.selectedTasks);
          if (newSelection.has(taskId)) {
            newSelection.delete(taskId);
          } else {
            newSelection.add(taskId);
          }
          return { selectedTasks: newSelection };
        });
      },

      selectAllTasks: (taskIds) => {
        set((state) => {
          // If specific taskIds are provided, use those (for filtered selections)
          if (taskIds) {
            return { selectedTasks: new Set(taskIds.filter(Boolean)) };
          }
          // Otherwise select all tasks
          return { selectedTasks: new Set(state.tasks.map(t => t.id!).filter(Boolean)) };
        });
      },

      clearSelection: () => {
        set({ selectedTasks: new Set() });
      },

      // Filter management
      setFilter: (filter) => {
        set((state) => ({
          currentFilter: { ...state.currentFilter, ...filter },
        }));
        // Automatically reload tasks when filter changes
        setTimeout(() => get().loadTasks(), 0);
      },

      // Form Management
      openTaskForm: (task) => {
        console.log('Store: Opening task form with task:', task);
        if (task) {
          console.log('Store: Task details:', {
            id: task.id,
            description: task.description,
            project: task.project,
            priority: task.priority,
            tags: task.tags,
            due: task.due,
          });
        }
        set({ isTaskFormOpen: true, editingTask: task || null });
      },
      
      closeTaskForm: () => {
        set({ isTaskFormOpen: false, editingTask: null });
      },

      // Utilities
      setError: (error) => set({ error }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    { name: 'task-store' }
  )
);