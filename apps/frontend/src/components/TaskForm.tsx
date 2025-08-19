import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Plus } from 'lucide-react';
import type { Task, TaskPriority } from '@/types/task';
import { formatDateForInput } from '@/utils/date';
import { useTaskStore } from '@/stores/taskStore';
import Button from './ui/Button';
import Input from './ui/Input';
import Select from './ui/Select';
import Modal from './ui/Modal';

const taskSchema = z.object({
  description: z.string().min(1, 'Description is required').max(500, 'Description too long'),
  project: z.string().optional(),
  priority: z.union([z.literal(''), z.literal('H'), z.literal('M'), z.literal('L'), z.null()]).optional(),
  tags: z.string().optional(),
  due: z.string().optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  task?: Task;
  isOpen: boolean;
  onClose: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ task, isOpen, onClose }) => {
  const { addTask, updateTask, projects, tags, isLoading } = useTaskStore();
  const isEditing = !!task;

  console.log('TaskForm rendered with task:', task);
  console.log('TaskForm defaultValues:', {
    description: task?.description || '',
    project: task?.project || '',
    priority: task?.priority === null ? '' : (task?.priority || ''),
    tags: Array.isArray(task?.tags) ? task.tags.join(', ') : '',
    due: task?.due ? formatDateForInput(task.due) : '',
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      description: '',
      project: '',
      priority: '',
      tags: '',
      due: '',
    },
  });

  const [tagInput, setTagInput] = React.useState('');
  const [selectedTags, setSelectedTags] = React.useState<string[]>(
    Array.isArray(task?.tags) ? task.tags : []
  );

  // Reset form when task changes or modal opens
  React.useEffect(() => {
    if (isOpen) {
      if (task) {
        const formData = {
          description: task.description || '',
          project: task.project || '',
          priority: task.priority === null ? '' : (task.priority || ''),
          tags: Array.isArray(task.tags) ? task.tags.join(', ') : '',
          due: task.due ? formatDateForInput(task.due) : '',
        };
        console.log('TaskForm useEffect: Resetting for edit with formData:', formData);
        
        // Use setValue for each field instead of reset
        setValue('description', formData.description);
        setValue('project', formData.project);
        setValue('priority', formData.priority);
        setValue('tags', formData.tags);
        setValue('due', formData.due);
        
        setSelectedTags(Array.isArray(task.tags) ? task.tags : []);
      } else {
        console.log('TaskForm useEffect: Resetting for new task');
        setValue('description', '');
        setValue('project', '');
        setValue('priority', '');
        setValue('tags', '');
        setValue('due', '');
        setSelectedTags([]);
      }
      setTagInput('');
    }
  }, [task, isOpen, setValue]);

  const addTag = () => {
    if (tagInput.trim() && !selectedTags.includes(tagInput.trim())) {
      const newTags = [...selectedTags, tagInput.trim()];
      setSelectedTags(newTags);
      setValue('tags', newTags.join(', '));
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    const newTags = selectedTags.filter(tag => tag !== tagToRemove);
    setSelectedTags(newTags);
    setValue('tags', newTags.join(', '));
  };

  const handleClose = () => {
    onClose();
  };

  const onSubmit = async (data: TaskFormData) => {
    try {
      const taskData = {
        description: data.description,
        project: data.project || undefined,
        priority: (!data.priority || data.priority === '') ? undefined : data.priority as TaskPriority,
        tags: selectedTags,
        due: data.due ? new Date(data.due).toISOString() : undefined,
      };

      if (isEditing && task) {
        await updateTask(task.id!, taskData);
      } else {
        await addTask(taskData.description, {
          project: taskData.project,
          priority: taskData.priority,
          tags: taskData.tags,
          due: taskData.due,
        });
      }

      handleClose();
    } catch (error) {
      console.error('Failed to save task:', error);
    }
  };

  const quickAddTag = (tag: string) => {
    if (!selectedTags.includes(tag)) {
      const newTags = [...selectedTags, tag];
      setSelectedTags(newTags);
      setValue('tags', newTags.join(', '));
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={isEditing ? 'Edit Task' : 'Add New Task'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Description */}
        <Input
          label="Description *"
          {...register('description')}
          error={errors.description?.message}
          placeholder="What needs to be done?"
          autoFocus
        />

        {/* Project and Priority row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Select
            label="Project"
            {...register('project')}
            error={errors.project?.message}
          >
            <option value="">No Project</option>
            {projects.map((project) => (
              <option key={project} value={project}>
                {project}
              </option>
            ))}
          </Select>

          <Select
            label="Priority"
            {...register('priority')}
            error={errors.priority?.message}
          >
            <option value="">No Priority</option>
            <option value="H">High</option>
            <option value="M">Medium</option>
            <option value="L">Low</option>
          </Select>
        </div>

        {/* Due date */}
        <Input
          type="datetime-local"
          label="Due Date"
          {...register('due')}
          error={errors.due?.message}
        />

        {/* Tags */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-secondary-700">
            Tags
          </label>
          
          {/* Selected tags */}
          {selectedTags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {selectedTags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => removeTag(tag)}
                    className="ml-1.5 inline-flex items-center justify-center w-3 h-3 rounded-full text-primary-400 hover:bg-primary-200 hover:text-primary-500 focus:outline-none focus:bg-primary-200 focus:text-primary-500"
                  >
                    <X className="w-2 h-2" />
                  </button>
                </span>
              ))}
            </div>
          )}

          {/* Tag input */}
          <div className="flex space-x-2">
            <Input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              placeholder="Add a tag..."
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addTag();
                }
              }}
            />
            <Button
              type="button"
              variant="outline"
              onClick={addTag}
              disabled={!tagInput.trim()}
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>

          {/* Quick add tags */}
          {tags.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-secondary-500">Quick add:</p>
              <div className="flex flex-wrap gap-1">
                {tags
                  .filter(tag => !selectedTags.includes(tag))
                  .slice(0, 10)
                  .map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => quickAddTag(tag)}
                      className="inline-flex items-center px-2 py-1 rounded text-xs text-secondary-600 bg-secondary-100 hover:bg-secondary-200 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    >
                      {tag}
                    </button>
                  ))}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            loading={isLoading}
            disabled={isLoading}
          >
            {isEditing ? 'Update Task' : 'Create Task'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default TaskForm;