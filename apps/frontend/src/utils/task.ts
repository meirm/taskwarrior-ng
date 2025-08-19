// Task utility functions
import type { Task, TaskPriority, TaskStatus } from '@/types/task';

export function getUrgencyColor(urgency: number): string {
  if (urgency >= 15) return 'text-error-600';
  if (urgency >= 10) return 'text-warning-600';
  if (urgency >= 5) return 'text-primary-600';
  return 'text-secondary-500';
}

export function getPriorityColor(priority?: TaskPriority): string {
  switch (priority) {
    case 'H':
      return 'text-error-600 bg-error-50 border-error-200';
    case 'M':
      return 'text-warning-600 bg-warning-50 border-warning-200';
    case 'L':
      return 'text-primary-600 bg-primary-50 border-primary-200';
    default:
      return 'text-secondary-500 bg-secondary-50 border-secondary-200';
  }
}

export function getPriorityLabel(priority?: TaskPriority): string {
  switch (priority) {
    case 'H':
      return 'High';
    case 'M':
      return 'Medium';
    case 'L':
      return 'Low';
    default:
      return 'None';
  }
}

export function getStatusColor(status: TaskStatus): string {
  switch (status) {
    case 'pending':
      return 'text-primary-600 bg-primary-50';
    case 'completed':
      return 'text-success-600 bg-success-50';
    case 'deleted':
      return 'text-error-600 bg-error-50';
    case 'waiting':
      return 'text-warning-600 bg-warning-50';
    default:
      return 'text-secondary-600 bg-secondary-50';
  }
}

export function getStatusLabel(status: TaskStatus): string {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'completed':
      return 'Completed';
    case 'deleted':
      return 'Deleted';
    case 'waiting':
      return 'Waiting';
    default:
      return status;
  }
}

export function sortTasks(tasks: Task[], sortBy: 'urgency' | 'due' | 'created' | 'modified' = 'urgency'): Task[] {
  return [...tasks].sort((a, b) => {
    switch (sortBy) {
      case 'urgency':
        return b.urgency - a.urgency;
      case 'due':
        if (!a.due && !b.due) return 0;
        if (!a.due) return 1;
        if (!b.due) return -1;
        return new Date(a.due).getTime() - new Date(b.due).getTime();
      case 'created':
        if (!a.entry && !b.entry) return 0;
        if (!a.entry) return 1;
        if (!b.entry) return -1;
        return new Date(b.entry).getTime() - new Date(a.entry).getTime();
      case 'modified':
        if (!a.modified && !b.modified) return 0;
        if (!a.modified) return 1;
        if (!b.modified) return -1;
        return new Date(b.modified).getTime() - new Date(a.modified).getTime();
      default:
        return 0;
    }
  });
}

export function filterTasks(tasks: Task[], filters: {
  search?: string;
  project?: string;
  priority?: TaskPriority | 'none' | null;
  tags?: string[];
}): Task[] {
  return tasks.filter(task => {
    // Search filter
    if (filters.search) {
      const search = filters.search.toLowerCase();
      const matchesDescription = task.description.toLowerCase().includes(search);
      const matchesProject = task.project?.toLowerCase().includes(search);
      const matchesTags = task.tags.some(tag => tag.toLowerCase().includes(search));
      if (!matchesDescription && !matchesProject && !matchesTags) {
        return false;
      }
    }

    // Project filter
    if (filters.project && filters.project !== 'all') {
      if (task.project !== filters.project) {
        return false;
      }
    }

    // Priority filter
    if (filters.priority && filters.priority !== 'all') {
      if (filters.priority === 'none') {
        if (task.priority) return false;
      } else {
        if (task.priority !== filters.priority) return false;
      }
    }

    // Tags filter
    if (filters.tags && filters.tags.length > 0) {
      const hasAnyTag = filters.tags.some(tag => task.tags.includes(tag));
      if (!hasAnyTag) return false;
    }

    return true;
  });
}

export function groupTasksByProject(tasks: Task[]): Record<string, Task[]> {
  return tasks.reduce((groups, task) => {
    const project = task.project || 'No Project';
    if (!groups[project]) {
      groups[project] = [];
    }
    groups[project].push(task);
    return groups;
  }, {} as Record<string, Task[]>);
}

export function getTaskProgress(tasks: Task[]): {
  total: number;
  completed: number;
  pending: number;
  percentage: number;
} {
  const total = tasks.length;
  const completed = tasks.filter(t => t.status === 'completed').length;
  const pending = tasks.filter(t => t.status === 'pending').length;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  return { total, completed, pending, percentage };
}

export function truncateDescription(description: string, maxLength: number = 50): string {
  if (description.length <= maxLength) return description;
  return description.substring(0, maxLength) + '...';
}