import React, { useState, useEffect } from 'react';
import { Trash2, RefreshCw, AlertTriangle, Undo2, CheckSquare, Square, MinusSquare } from 'lucide-react';
import { taskWarriorMCPOAPI as taskWarriorAPI } from '@/services/api-mcpo';
import { Task } from '@/types/task';
import { formatTaskDate } from '@/utils/date';
import Button from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export function TrashPage() {
  const [deletedTasks, setDeletedTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPurgeDialog, setShowPurgeDialog] = useState(false);
  const [restoringTasks, setRestoringTasks] = useState<Set<string>>(new Set());
  const [purging, setPurging] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<Set<string>>(new Set());
  const [bulkRestoring, setBulkRestoring] = useState(false);
  const [lastSelectedIndex, setLastSelectedIndex] = useState<number | null>(null);

  useEffect(() => {
    loadDeletedTasks();
  }, []);

  // Add keyboard shortcut for select all (Ctrl/Cmd + A)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();
        toggleSelectAll();
      }
      // Escape to clear selection
      if (e.key === 'Escape' && selectedTasks.size > 0) {
        setSelectedTasks(new Set());
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [deletedTasks.length, selectedTasks.size]);

  const loadDeletedTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await taskWarriorAPI.listTasks({ status: 'deleted' });
      if (response.success && response.tasks) {
        setDeletedTasks(response.tasks);
        // Clear selections when reloading
        setSelectedTasks(new Set());
      } else {
        setDeletedTasks([]);
      }
    } catch (err) {
      setError('Failed to load deleted tasks');
      console.error('Error loading deleted tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleTaskSelection = (taskId: string, index: number, event?: React.MouseEvent) => {
    // Handle shift-click for range selection
    if (event?.shiftKey && lastSelectedIndex !== null) {
      const start = Math.min(lastSelectedIndex, index);
      const end = Math.max(lastSelectedIndex, index);
      const taskIdsInRange = deletedTasks
        .slice(start, end + 1)
        .map(task => task.uuid || task.id?.toString() || '');
      
      setSelectedTasks(prev => {
        const newSet = new Set(prev);
        taskIdsInRange.forEach(id => newSet.add(id));
        return newSet;
      });
    } else {
      // Normal toggle
      setSelectedTasks(prev => {
        const newSet = new Set(prev);
        if (newSet.has(taskId)) {
          newSet.delete(taskId);
        } else {
          newSet.add(taskId);
        }
        return newSet;
      });
      setLastSelectedIndex(index);
    }
  };

  const toggleSelectAll = () => {
    if (selectedTasks.size === deletedTasks.length) {
      // All selected, deselect all
      setSelectedTasks(new Set());
    } else {
      // Not all selected, select all
      const allTaskIds = deletedTasks.map(task => task.uuid || task.id?.toString() || '');
      setSelectedTasks(new Set(allTaskIds));
    }
  };

  const handleBulkRestore = async () => {
    if (selectedTasks.size === 0) return;
    
    try {
      setBulkRestoring(true);
      setError(null);
      
      const restorePromises = Array.from(selectedTasks).map(taskId => 
        taskWarriorAPI.restoreTask(taskId, 'pending')
      );
      
      const results = await Promise.allSettled(restorePromises);
      
      // Count successful restorations
      const successCount = results.filter(r => r.status === 'fulfilled' && 
        (r as PromiseFulfilledResult<any>).value.success).length;
      
      if (successCount > 0) {
        // Reload the task list
        await loadDeletedTasks();
        // Clear selection after successful restoration
        setSelectedTasks(new Set());
        console.log(`Successfully restored ${successCount} tasks`);
      }
      
      if (successCount < selectedTasks.size) {
        setError(`Restored ${successCount} of ${selectedTasks.size} tasks. Some tasks failed to restore.`);
        // Clear selection even on partial success
        setSelectedTasks(new Set());
      }
      
    } catch (err) {
      setError('Failed to restore selected tasks');
      console.error('Error restoring tasks:', err);
    } finally {
      setBulkRestoring(false);
    }
  };

  const handlePurgeSelected = async () => {
    // For now, we'll purge all since the API doesn't support selective purge
    // In the future, we could add selective purge support
    handlePurgeAll();
  };

  const handleRestore = async (task: Task) => {
    const taskId = task.uuid || task.id?.toString() || '';
    
    try {
      setRestoringTasks(prev => new Set(prev).add(taskId));
      const response = await taskWarriorAPI.restoreTask(taskId, 'pending');
      
      if (response.success) {
        // Reload the task list to ensure consistency with backend
        await loadDeletedTasks();
        
        // Clear selection if the restored task was selected
        setSelectedTasks(prev => {
          const newSet = new Set(prev);
          newSet.delete(taskId);
          return newSet;
        });
        
        // Show success message (could use a toast here)
        console.log('Task restored successfully');
      } else {
        setError('Failed to restore task');
      }
    } catch (err) {
      setError('Failed to restore task');
      console.error('Error restoring task:', err);
    } finally {
      setRestoringTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(taskId);
        return newSet;
      });
    }
  };

  const handlePurgeAll = async () => {
    try {
      setPurging(true);
      const response = await taskWarriorAPI.purgeDeletedTasks();
      
      if (response.success && response.data) {
        setDeletedTasks([]);
        setShowPurgeDialog(false);
        console.log(`Purged ${response.data.purged_count} tasks`);
        // You might also show the message: response.data.message
      } else {
        setError(response.data?.message || 'Failed to purge tasks');
      }
    } catch (err) {
      setError('Failed to purge tasks');
      console.error('Error purging tasks:', err);
    } finally {
      setPurging(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  // Compute selection state for checkbox
  const isAllSelected = deletedTasks.length > 0 && selectedTasks.size === deletedTasks.length;
  const isPartiallySelected = selectedTasks.size > 0 && selectedTasks.size < deletedTasks.length;

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Trash2 className="w-8 h-8 text-gray-600" />
            <h1 className="text-3xl font-bold text-gray-900">Trash</h1>
            <span className="text-sm text-gray-500 ml-2">
              {deletedTasks.length} deleted {deletedTasks.length === 1 ? 'task' : 'tasks'}
              {selectedTasks.size > 0 && ` (${selectedTasks.size} selected)`}
            </span>
          </div>
          <div className="flex gap-2">
            {selectedTasks.size > 0 && (
              <>
                <Button
                  variant="outline"
                  onClick={handleBulkRestore}
                  disabled={bulkRestoring}
                >
                  {bulkRestoring ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Undo2 className="w-4 h-4 mr-2" />
                  )}
                  Restore {selectedTasks.size} Selected
                </Button>
              </>
            )}
            <Button
              variant="outline"
              onClick={loadDeletedTasks}
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            {deletedTasks.length > 0 && (
              <Button
                variant="destructive"
                onClick={() => setShowPurgeDialog(true)}
                disabled={purging}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Purge All
              </Button>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {deletedTasks.length === 0 ? (
        <Card>
          <CardContent className="py-12 mt-2">
            <div className="text-center text-gray-500">
              <Trash2 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">The trash is empty</p>
              <p className="text-sm mt-2">Deleted tasks will appear here</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Select All Checkbox */}
          {deletedTasks.length > 0 && (
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <button
                onClick={toggleSelectAll}
                className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                {isAllSelected ? (
                  <CheckSquare className="w-5 h-5 text-primary-600" />
                ) : isPartiallySelected ? (
                  <MinusSquare className="w-5 h-5 text-primary-600" />
                ) : (
                  <Square className="w-5 h-5" />
                )}
                <span>Select All</span>
              </button>
              <div className="text-xs text-gray-500">
                <span className="font-medium">Tip:</span> Use Shift+Click to select a range, Ctrl/Cmd+A to select all, Esc to clear
              </div>
            </div>
          )}
          
          {/* Task Cards */}
          <div className="grid gap-4">
            {deletedTasks.map((task, index) => {
              const taskId = task.uuid || task.id?.toString() || '';
              const isRestoring = restoringTasks.has(taskId);
              const isSelected = selectedTasks.has(taskId);
              
              return (
                <Card 
                  key={task.uuid || task.id} 
                  className={`hover:shadow-md transition-all cursor-pointer ${isSelected ? 'ring-2 ring-primary-500 bg-primary-50' : ''}`}
                  onClick={(e) => {
                    // Allow clicking anywhere on the card to select (except buttons)
                    if ((e.target as HTMLElement).closest('button')) return;
                    toggleTaskSelection(taskId, index, e);
                  }}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleTaskSelection(taskId, index, e);
                        }}
                        className="mt-1 flex-shrink-0"
                      >
                        {isSelected ? (
                          <CheckSquare className="w-5 h-5 text-primary-600" />
                        ) : (
                          <Square className="w-5 h-5 text-gray-400 hover:text-gray-600" />
                        )}
                      </button>
                      <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-1">
                        {task.description}
                      </h3>
                      <div className="flex flex-wrap gap-2 text-sm text-gray-500">
                        {task.project && (
                          <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded">
                            {task.project}
                          </span>
                        )}
                        {task.tags && task.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-gray-100 text-gray-600 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {task.priority && (
                          <span className={`px-2 py-1 rounded ${
                            task.priority === 'H' ? 'bg-red-50 text-red-700' :
                            task.priority === 'M' ? 'bg-yellow-50 text-yellow-700' :
                            'bg-green-50 text-green-700'
                          }`}>
                            Priority: {task.priority}
                          </span>
                        )}
                      </div>
                      <div className="mt-2 text-xs text-gray-400">
                        {task.entry && (
                          <span>Created: {formatTaskDate(task.entry)}</span>
                        )}
                        {task.end && (
                          <span className="ml-4">Deleted: {formatTaskDate(task.end)}</span>
                        )}
                      </div>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRestore(task);
                        }}
                        disabled={isRestoring || isSelected}
                        className="ml-4 flex-shrink-0"
                        title={isSelected ? "Use 'Restore Selected' button to restore multiple tasks" : "Restore this task"}
                      >
                        {isRestoring ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Undo2 className="w-4 h-4" />
                        )}
                        <span className="ml-2">Restore</span>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      <AlertDialog open={showPurgeDialog} onOpenChange={setShowPurgeDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Permanently Delete All Tasks?
            </AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete {deletedTasks.length} task{deletedTasks.length === 1 ? '' : 's'} from the database.
              These tasks will be completely removed and cannot be recovered.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handlePurgeAll}
              disabled={purging}
              className="bg-red-600 hover:bg-red-700"
            >
              {purging ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Purging...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Purge All
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}