import React from 'react';
import { clsx } from 'clsx';
import { 
  Clock, 
  Calendar, 
  Play, 
  Square, 
  CheckSquare, 
  Trash2, 
  Edit3,
  Flag,
  Tag as TagIcon,
  Folder
} from 'lucide-react';
import type { Task } from '@/types/task';
import { formatRelativeDate, isDateOverdue } from '@/utils/date';
import { getPriorityColor, getUrgencyColor, truncateDescription } from '@/utils/task';
import Badge from './ui/Badge';
import Button from './ui/Button';

interface TaskCardProps {
  task: Task;
  isSelected?: boolean;
  onSelect?: (taskId: number) => void;
  onComplete?: (taskId: number) => void;
  onUncomplete?: (taskId: number) => void;
  onDelete?: (taskId: number) => void;
  onEdit?: (task: Task) => void;
  onStart?: (taskId: number) => void;
  onStop?: (taskId: number) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  isSelected = false,
  onSelect,
  onComplete,
  onUncomplete,
  onDelete,
  onEdit,
  onStart,
  onStop,
}) => {
  const isCompleted = task.status === 'completed';
  const isActive = task.start && !task.end;
  const isOverdue = task.due ? isDateOverdue(task.due) : false;

  return (
    <div
      className={clsx(
        'bg-white rounded-lg border shadow-sm transition-all hover:shadow-md',
        isSelected && 'ring-2 ring-primary-500 border-primary-300',
        isCompleted && 'opacity-75',
        isOverdue && 'border-error-300 bg-error-50'
      )}
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-start space-x-3 flex-1">
            {/* Selection checkbox */}
            <div className="mt-1">
              {task.id ? (
                <button
                  onClick={() => onSelect?.(task.id!)}
                  className="p-1 hover:bg-secondary-100 rounded"
                  aria-label={isSelected ? 'Deselect task' : 'Select task'}
                >
                  {isSelected ? (
                    <CheckSquare className="w-4 h-4 text-primary-600" />
                  ) : (
                    <Square className="w-4 h-4 text-secondary-400" />
                  )}
                </button>
              ) : (
                <div className="w-6 h-6" />
              )}
            </div>

            {/* Task content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-2">
                {/* Urgency indicator */}
                <div className="flex items-center">
                  <Flag className={clsx('w-4 h-4', getUrgencyColor(task.urgency))} />
                  <span className={clsx('text-xs font-mono', getUrgencyColor(task.urgency))}>
                    {task.urgency.toFixed(1)}
                  </span>
                </div>

                {/* Priority badge */}
                {task.priority && (
                  <Badge
                    variant={
                      task.priority === 'H' ? 'error' :
                      task.priority === 'M' ? 'warning' :
                      'primary'
                    }
                    size="sm"
                  >
                    {task.priority === 'H' ? 'High' : task.priority === 'M' ? 'Medium' : 'Low'}
                  </Badge>
                )}

                {/* Active indicator */}
                {isActive && (
                  <Badge variant="success" size="sm">
                    <Play className="w-3 h-3 mr-1" />
                    Active
                  </Badge>
                )}
              </div>

              {/* Description */}
              <h3
                className={clsx(
                  'text-sm font-medium text-secondary-900 mb-2 cursor-pointer hover:text-primary-600',
                  isCompleted && 'line-through text-secondary-500'
                )}
                onClick={() => onEdit?.(task)}
                title={task.description}
              >
                {truncateDescription(task.description, 80)}
              </h3>

              {/* Metadata */}
              <div className="flex items-center space-x-4 text-xs text-secondary-500">
                {/* Project */}
                {task.project && (
                  <div className="flex items-center">
                    <Folder className="w-3 h-3 mr-1" />
                    {task.project}
                  </div>
                )}

                {/* Due date */}
                {task.due && (
                  <div className={clsx(
                    'flex items-center',
                    isOverdue && 'text-error-600 font-medium'
                  )}>
                    <Calendar className="w-3 h-3 mr-1" />
                    {formatRelativeDate(task.due)}
                  </div>
                )}

                {/* Modified date */}
                {task.modified && (
                  <div className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatRelativeDate(task.modified)}
                  </div>
                )}
              </div>

              {/* Tags */}
              {task.tags.length > 0 && (
                <div className="flex items-center flex-wrap gap-1 mt-2">
                  <TagIcon className="w-3 h-3 text-secondary-400" />
                  {task.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" size="sm">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center space-x-1 ml-2">
            {!isCompleted && (
              <>
                {isActive ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onStop?.(task.id!)}
                    title="Stop working on this task"
                  >
                    <Square className="w-3 h-3" />
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onStart?.(task.id!)}
                    title="Start working on this task"
                  >
                    <Play className="w-3 h-3" />
                  </Button>
                )}

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onComplete?.(task.id!)}
                  title="Mark as completed"
                >
                  <CheckSquare className="w-3 h-3" />
                </Button>
              </>
            )}

            {isCompleted && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onUncomplete?.(task.id!)}
                title="Mark as pending"
                className="text-primary-600 hover:text-primary-700"
              >
                <Square className="w-3 h-3" />
              </Button>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit?.(task)}
              title="Edit task"
            >
              <Edit3 className="w-3 h-3" />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete?.(task.id!)}
              title="Delete task"
              className="text-error-600 hover:text-error-700 hover:bg-error-50"
            >
              <Trash2 className="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskCard;