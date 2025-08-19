import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { clsx } from 'clsx';
import { 
  CheckSquare, 
  Square, 
  Trash2, 
  Play, 
  SquareIcon,
  Filter,
  SortAsc,
  Search,
  Plus
} from 'lucide-react';
import type { Task, TaskStatus, TaskPriority } from '@/types/task';
import { useTaskStore } from '@/stores/taskStore';
import { sortTasks, filterTasks, getTaskProgress } from '@/utils/task';
import TaskCard from './TaskCard';
import Button from './ui/Button';
import Input from './ui/Input';
import Select from './ui/Select';
import Badge from './ui/Badge';

const TaskList: React.FC = () => {
  const [searchParams] = useSearchParams();
  const {
    tasks,
    projects,
    selectedTasks,
    currentFilter,
    isLoading,
    error,
    isTaskFormOpen,
    editingTask,
    toggleTaskSelection,
    selectAllTasks,
    clearSelection,
    setFilter,
    completeTask,
    uncompleteTask,
    deleteTask,
    startTask,
    stopTask,
    batchComplete,
    batchUncomplete,
    batchDelete,
    batchStart,
    batchStop,
    openTaskForm,
    closeTaskForm,
  } = useTaskStore();
  
  // Get search from URL params or use local state
  const urlSearch = searchParams.get('search');
  const [searchTerm, setSearchTerm] = React.useState(urlSearch || '');
  const [sortBy, setSortBy] = React.useState<'urgency' | 'due' | 'created' | 'modified'>('urgency');
  const [localFilters, setLocalFilters] = React.useState({
    tags: [] as string[],
  });

  // Update search term when URL params change
  React.useEffect(() => {
    if (urlSearch !== null) {
      setSearchTerm(urlSearch);
    }
  }, [urlSearch]);

  // Apply local filtering and sorting
  const filteredAndSortedTasks = React.useMemo(() => {
    let filtered = filterTasks(tasks, {
      search: searchTerm,
      project: currentFilter.project === 'all' ? undefined : currentFilter.project,
      priority: currentFilter.priority === 'all' ? undefined : currentFilter.priority === 'none' ? 'none' : currentFilter.priority as TaskPriority,
      tags: localFilters.tags.length > 0 ? localFilters.tags : undefined,
    });

    return sortTasks(filtered, sortBy);
  }, [tasks, searchTerm, currentFilter.project, currentFilter.priority, localFilters, sortBy]);

  const progress = getTaskProgress(filteredAndSortedTasks);
  const selectedTaskIds = Array.from(selectedTasks);
  const hasSelection = selectedTaskIds.length > 0;

  const handleEditTask = (task: Task) => {
    openTaskForm(task);
  };

  const handleBatchAction = async (action: 'complete' | 'uncomplete' | 'delete' | 'start' | 'stop') => {
    if (!hasSelection) return;

    try {
      switch (action) {
        case 'complete':
          await batchComplete(selectedTaskIds);
          break;
        case 'uncomplete':
          await batchUncomplete(selectedTaskIds);
          break;
        case 'delete':
          await batchDelete(selectedTaskIds);
          break;
        case 'start':
          await batchStart(selectedTaskIds);
          break;
        case 'stop':
          await batchStop(selectedTaskIds);
          break;
      }
    } catch (error) {
      console.error(`Failed to ${action} tasks:`, error);
    }
  };

  const allSelected = filteredAndSortedTasks.length > 0 && 
    filteredAndSortedTasks.every(task => task.id && selectedTasks.has(task.id));
    
  const handleSelectAll = () => {
    if (allSelected) {
      clearSelection();
    } else {
      // Pass the filtered task IDs to selectAllTasks
      const visibleTaskIds = filteredAndSortedTasks
        .map(task => task.id)
        .filter(id => id !== undefined && id !== null) as number[];
      selectAllTasks(visibleTaskIds);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Tasks</h1>
          <p className="text-sm text-secondary-600 mt-1">
            {progress.total} total · {progress.completed} completed · {progress.pending} pending
            {progress.total > 0 && (
              <span className="ml-2">
                <Badge variant="primary" size="sm">{progress.percentage}% complete</Badge>
              </span>
            )}
          </p>
        </div>
        <Button onClick={() => openTaskForm()}>
          <Plus className="w-4 h-4 mr-2" />
          Add Task
        </Button>
      </div>

      {/* Filters and Search */}
      <div className="bg-white p-4 rounded-lg border space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <Input
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>

          {/* Status Filter */}
          <Select
            value={currentFilter.status}
            onChange={(e) => setFilter({ status: e.target.value as TaskStatus | 'all' })}
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="waiting">Waiting</option>
            <option value="deleted">Deleted</option>
          </Select>

          {/* Sort */}
          <Select value={sortBy} onChange={(e) => setSortBy(e.target.value as typeof sortBy)}>
            <option value="urgency">Sort by Urgency</option>
            <option value="due">Sort by Due Date</option>
            <option value="created">Sort by Created</option>
            <option value="modified">Sort by Modified</option>
          </Select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Project Filter */}
          <Select
            value={currentFilter.project}
            onChange={(e) => setFilter({ project: e.target.value })}
          >
            <option value="all">All Projects</option>
            {projects.map((project) => (
              <option key={project} value={project}>
                {project}
              </option>
            ))}
          </Select>

          {/* Priority Filter */}
          <Select
            value={currentFilter.priority}
            onChange={(e) => setFilter({ 
              priority: e.target.value as 'H' | 'M' | 'L' | 'none' | 'all'
            })}
          >
            <option value="all">All Priorities</option>
            <option value="H">High Priority</option>
            <option value="M">Medium Priority</option>
            <option value="L">Low Priority</option>
            <option value="none">No Priority</option>
          </Select>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                setSearchTerm('');
                setFilter({ status: 'all', project: 'all', priority: 'all' });
                setLocalFilters({ tags: [] });
              }}
              className="text-sm text-secondary-500 hover:text-secondary-700"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Batch Actions */}
      {hasSelection && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-primary-900">
                {selectedTaskIds.length} task{selectedTaskIds.length !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={clearSelection}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Clear selection
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBatchAction('start')}
              >
                <Play className="w-4 h-4 mr-1" />
                Start
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBatchAction('stop')}
              >
                <SquareIcon className="w-4 h-4 mr-1" />
                Stop
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBatchAction('complete')}
              >
                <CheckSquare className="w-4 h-4 mr-1" />
                Complete
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBatchAction('uncomplete')}
                className="text-primary-600 hover:text-primary-700"
              >
                <Square className="w-4 h-4 mr-1" />
                Uncomplete
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleBatchAction('delete')}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Task List Header */}
      <div className="flex items-center justify-between py-2">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleSelectAll}
            className="flex items-center space-x-2 text-sm text-secondary-600 hover:text-secondary-900"
          >
            {allSelected ? (
              <CheckSquare className="w-4 h-4" />
            ) : (
              <Square className="w-4 h-4" />
            )}
            <span>Select All</span>
          </button>
        </div>
        <span className="text-sm text-secondary-500">
          {filteredAndSortedTasks.length} task{filteredAndSortedTasks.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-error-50 border border-error-200 rounded-lg p-4">
          <p className="text-error-700">{error}</p>
        </div>
      )}

      {/* Task List */}
      {!isLoading && !error && (
        <div className="space-y-3">
          {filteredAndSortedTasks.length > 0 ? (
            filteredAndSortedTasks.map((task, index) => {
              // Generate a unique key for each task
              // Prefer uuid, then id (if not 0), then fallback to index
              const taskKey = task.uuid || (task.id && task.id !== 0 ? `id-${task.id}` : `index-${index}`);
              
              return (
                <TaskCard
                  key={taskKey}
                  task={task}
                  isSelected={task.id ? selectedTasks.has(task.id) : false}
                  onSelect={toggleTaskSelection}
                  onComplete={completeTask}
                  onUncomplete={uncompleteTask}
                  onDelete={deleteTask}
                  onEdit={handleEditTask}
                  onStart={startTask}
                  onStop={stopTask}
                />
              );
            })
          ) : (
            <div className="text-center py-12">
              <div className="text-secondary-400 mb-4">
                <CheckSquare className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-secondary-900 mb-2">
                No tasks found
              </h3>
              <p className="text-secondary-500 mb-4">
                {tasks.length > 0 
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Get started by creating your first task.'
                }
              </p>
              {tasks.length === 0 && (
                <Button onClick={() => openTaskForm()}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Task
                </Button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Task Form Modal is now handled globally in Layout */}
    </div>
  );
};

export default TaskList;