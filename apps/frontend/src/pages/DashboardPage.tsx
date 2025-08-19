import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart3, 
  Calendar, 
  Clock, 
  TrendingUp, 
  Target,
  CheckCircle,
  AlertCircle,
  Activity
} from 'lucide-react';
import { useTaskStore } from '@/stores/taskStore';
import { formatRelativeDate, isDateOverdue } from '@/utils/date';
import { sortTasks } from '@/utils/task';
import Layout from '@/components/Layout';
import TaskCard from '@/components/TaskCard';
import Badge from '@/components/ui/Badge';
import type { Task } from '@/types/task';

const DashboardPage: React.FC = () => {
  const { tasks, summary, loadTasks, loadMetadata, completeTask, deleteTask, startTask, stopTask, setFilter, openTaskForm } = useTaskStore();
  const navigate = useNavigate();

  React.useEffect(() => {
    loadTasks();
    loadMetadata();
  }, [loadTasks, loadMetadata]);

  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const overdueTasks = pendingTasks.filter(t => t.due && isDateOverdue(t.due));
  const dueSoonTasks = pendingTasks.filter(t => {
    if (!t.due) return false;
    const due = new Date(t.due);
    const now = new Date();
    const diffDays = (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays > 0 && diffDays <= 3;
  });
  const recentTasks = sortTasks(pendingTasks, 'modified').slice(0, 5);
  const highUrgencyTasks = sortTasks(pendingTasks, 'urgency').slice(0, 3);

  const handleCardClick = (filterType: 'all' | 'pending' | 'completed' | 'overdue') => {
    if (filterType === 'overdue') {
      // For overdue, we'll need to navigate to tasks and apply a custom filter
      setFilter({ status: 'pending' });
    } else if (filterType === 'all') {
      setFilter({ status: 'all' });
    } else {
      setFilter({ status: filterType });
    }
    navigate('/tasks');
  };

  const handlePriorityClick = (priority: 'H' | 'M' | 'L' | 'none') => {
    // Navigate to tasks page with pending status and priority filter
    setFilter({ 
      status: 'pending',
      priority: priority 
    });
    navigate('/tasks');
  };

  const handleEditTask = (task: Task) => {
    console.log('Dashboard handleEditTask called with:', task);
    openTaskForm(task);
  };

  const stats = [
    {
      title: 'Total Tasks',
      value: summary?.status.total || 0,
      icon: Target,
      color: 'bg-primary-500',
      textColor: 'text-primary-600',
      onClick: () => handleCardClick('all'),
    },
    {
      title: 'Pending',
      value: summary?.status.pending || 0,
      icon: Clock,
      color: 'bg-warning-500',
      textColor: 'text-warning-600',
      onClick: () => handleCardClick('pending'),
    },
    {
      title: 'Completed',
      value: summary?.status.completed || 0,
      icon: CheckCircle,
      color: 'bg-success-500',
      textColor: 'text-success-600',
      onClick: () => handleCardClick('completed'),
    },
    {
      title: 'Overdue',
      value: overdueTasks.length,
      icon: AlertCircle,
      color: 'bg-error-500',
      textColor: 'text-error-600',
      onClick: () => handleCardClick('overdue'),
    },
  ];

  const completionRate = summary ? 
    Math.round((summary.status.completed / summary.status.total) * 100) : 0;

  return (
    <Layout currentPage="dashboard">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Dashboard</h1>
          <p className="text-secondary-600 mt-1">
            Overview of your task management progress
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <div 
              key={stat.title} 
              className="bg-white p-6 rounded-lg border shadow-sm cursor-pointer hover:shadow-md transition-shadow"
              onClick={stat.onClick}
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">{stat.title}</p>
                  <p className={`text-2xl font-bold ${stat.textColor}`}>{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Progress Overview */}
        {summary && (
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-secondary-900">
                Progress Overview
              </h2>
              <Badge variant="primary" size="md">
                {completionRate}% Complete
              </Badge>
            </div>
            <div className="space-y-4">
              <div className="w-full bg-secondary-200 rounded-full h-3">
                <div 
                  className="bg-primary-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${completionRate}%` }}
                />
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                  <p className="font-medium text-secondary-900">{summary.status.completed}</p>
                  <p className="text-secondary-500">Completed</p>
                </div>
                <div className="text-center">
                  <p className="font-medium text-secondary-900">{summary.status.pending}</p>
                  <p className="text-secondary-500">Pending</p>
                </div>
                <div className="text-center">
                  <p className="font-medium text-secondary-900">{summary.status.total}</p>
                  <p className="text-secondary-500">Total</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* High Priority Tasks */}
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-secondary-900 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-error-500" />
                High Urgency Tasks
              </h2>
              <Badge variant="secondary" size="sm">
                {highUrgencyTasks.length}
              </Badge>
            </div>
            <div className="space-y-3">
              {highUrgencyTasks.length > 0 ? (
                highUrgencyTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onComplete={completeTask}
                    onDelete={deleteTask}
                    onStart={startTask}
                    onStop={stopTask}
                    onEdit={handleEditTask}
                  />
                ))
              ) : (
                <p className="text-secondary-500 text-center py-4">
                  No high urgency tasks
                </p>
              )}
            </div>
          </div>

          {/* Overdue & Due Soon */}
          <div className="space-y-6">
            {/* Overdue Tasks */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-secondary-900 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2 text-error-500" />
                  Overdue Tasks
                </h2>
                <Badge variant="error" size="sm">
                  {overdueTasks.length}
                </Badge>
              </div>
              <div className="space-y-2">
                {overdueTasks.length > 0 ? (
                  overdueTasks.slice(0, 3).map((task) => (
                    <div 
                      key={task.id} 
                      className="flex items-center justify-between p-3 bg-error-50 rounded-md cursor-pointer hover:bg-error-100 transition-colors"
                      onClick={() => handleEditTask(task)}
                    >
                      <div>
                        <p className="font-medium text-secondary-900 text-sm hover:text-primary-600 transition-colors">
                          {task.description.length > 40 
                            ? `${task.description.substring(0, 40)}...` 
                            : task.description
                          }
                        </p>
                        <p className="text-xs text-error-600">
                          Due {formatRelativeDate(task.due)}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-secondary-500 text-center py-4">
                    No overdue tasks 🎉
                  </p>
                )}
              </div>
            </div>

            {/* Due Soon */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-secondary-900 flex items-center">
                  <Calendar className="w-5 h-5 mr-2 text-warning-500" />
                  Due Soon
                </h2>
                <Badge variant="warning" size="sm">
                  {dueSoonTasks.length}
                </Badge>
              </div>
              <div className="space-y-2">
                {dueSoonTasks.length > 0 ? (
                  dueSoonTasks.slice(0, 3).map((task) => (
                    <div 
                      key={task.id} 
                      className="flex items-center justify-between p-3 bg-warning-50 rounded-md cursor-pointer hover:bg-warning-100 transition-colors"
                      onClick={() => handleEditTask(task)}
                    >
                      <div>
                        <p className="font-medium text-secondary-900 text-sm hover:text-primary-600 transition-colors">
                          {task.description.length > 40 
                            ? `${task.description.substring(0, 40)}...` 
                            : task.description
                          }
                        </p>
                        <p className="text-xs text-warning-600">
                          Due {formatRelativeDate(task.due)}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-secondary-500 text-center py-4">
                    No tasks due soon
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Priority Distribution */}
        {summary && (
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h2 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Priority Distribution
            </h2>
            <div className="grid grid-cols-4 gap-4">
              <div 
                className="text-center p-4 bg-error-50 rounded-lg cursor-pointer hover:bg-error-100 transition-colors"
                onClick={() => handlePriorityClick('H')}
              >
                <div className="text-2xl font-bold text-error-600">{summary.priority.H}</div>
                <div className="text-sm text-error-700">High Priority</div>
              </div>
              <div 
                className="text-center p-4 bg-warning-50 rounded-lg cursor-pointer hover:bg-warning-100 transition-colors"
                onClick={() => handlePriorityClick('M')}
              >
                <div className="text-2xl font-bold text-warning-600">{summary.priority.M}</div>
                <div className="text-sm text-warning-700">Medium Priority</div>
              </div>
              <div 
                className="text-center p-4 bg-primary-50 rounded-lg cursor-pointer hover:bg-primary-100 transition-colors"
                onClick={() => handlePriorityClick('L')}
              >
                <div className="text-2xl font-bold text-primary-600">{summary.priority.L}</div>
                <div className="text-sm text-primary-700">Low Priority</div>
              </div>
              <div 
                className="text-center p-4 bg-secondary-50 rounded-lg cursor-pointer hover:bg-secondary-100 transition-colors"
                onClick={() => handlePriorityClick('none')}
              >
                <div className="text-2xl font-bold text-secondary-600">{summary.priority.None}</div>
                <div className="text-sm text-secondary-700">No Priority</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default DashboardPage;