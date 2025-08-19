import React from 'react';
import { useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import { 
  Home, 
  CheckSquare, 
  BarChart3, 
  Settings, 
  Menu,
  X,
  Search,
  Plus,
  Bell,
  Trash2
} from 'lucide-react';
import { useTaskStore } from '@/stores/taskStore';
import Button from './ui/Button';
import Badge from './ui/Badge';
import Input from './ui/Input';
import TaskForm from './TaskFormSimple';

interface LayoutProps {
  children: React.ReactNode;
  currentPage?: 'tasks' | 'dashboard' | 'reports' | 'settings' | 'trash';
}

const Layout: React.FC<LayoutProps> = ({ children, currentPage = 'tasks' }) => {
  const { summary, loadMetadata, openTaskForm, closeTaskForm, isTaskFormOpen, editingTask, setFilter } = useTaskStore();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isSearchOpen, setIsSearchOpen] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');

  React.useEffect(() => {
    loadMetadata();
  }, [loadMetadata]);

  const navigation = [
    { 
      name: 'Dashboard', 
      key: 'dashboard' as const, 
      icon: Home, 
      badge: null,
      path: '/dashboard'
    },
    { 
      name: 'Tasks', 
      key: 'tasks' as const, 
      icon: CheckSquare, 
      badge: summary?.status.pending || null,
      path: '/tasks'
    },
    {
      name: 'Trash',
      key: 'trash' as const,
      icon: Trash2,
      badge: summary?.status.deleted || null,
      path: '/trash'
    },
    { 
      name: 'Reports', 
      key: 'reports' as const, 
      icon: BarChart3, 
      badge: null,
      path: '/reports'
    },
    { 
      name: 'Settings', 
      key: 'settings' as const, 
      icon: Settings, 
      badge: null,
      path: '/settings'
    },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    setIsSidebarOpen(false); // Close mobile sidebar after navigation
  };

  const closeSidebar = () => setIsSidebarOpen(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      // Navigate to tasks page with search query
      navigate(`/tasks?search=${encodeURIComponent(searchTerm)}`);
      setIsSearchOpen(false);
      setSearchTerm('');
    }
  };

  const toggleSearch = () => {
    setIsSearchOpen(!isSearchOpen);
    if (!isSearchOpen) {
      setSearchTerm('');
    }
  };

  return (
    <div className="flex h-screen bg-secondary-50">
      {/* Mobile sidebar backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-secondary-600 bg-opacity-75 lg:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Sidebar header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-secondary-200">
          <div 
            className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => handleNavigation('/about')}
            title="About TaskWarrior MCP Edition"
          >
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <CheckSquare className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-lg font-bold text-secondary-900">TaskWarrior</h1>
          </div>
          <button
            onClick={closeSidebar}
            className="lg:hidden p-1 rounded-md text-secondary-500 hover:text-secondary-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick stats */}
        {summary && (
          <div className="p-6 border-b border-secondary-200">
            <div className="grid grid-cols-2 gap-4">
              <div 
                className="text-center cursor-pointer hover:bg-primary-50 rounded-lg p-2 transition-colors"
                onClick={() => {
                  useTaskStore.getState().setFilter({ status: 'pending' });
                  handleNavigation('/tasks');
                }}
              >
                <div className="text-2xl font-bold text-primary-600">
                  {summary.status.pending}
                </div>
                <div className="text-xs text-secondary-500">Pending</div>
              </div>
              <div 
                className="text-center cursor-pointer hover:bg-success-50 rounded-lg p-2 transition-colors"
                onClick={() => {
                  useTaskStore.getState().setFilter({ status: 'completed' });
                  handleNavigation('/tasks');
                }}
              >
                <div className="text-2xl font-bold text-success-600">
                  {summary.status.completed}
                </div>
                <div className="text-xs text-secondary-500">Completed</div>
              </div>
              <div 
                className="text-center cursor-pointer hover:bg-warning-50 rounded-lg p-2 transition-colors"
                onClick={() => {
                  useTaskStore.getState().setFilter({ status: 'pending' });
                  handleNavigation('/tasks');
                }}
              >
                <div className="text-2xl font-bold text-warning-600">
                  {summary.overdue}
                </div>
                <div className="text-xs text-secondary-500">Overdue</div>
              </div>
              <div 
                className="text-center cursor-pointer hover:bg-secondary-100 rounded-lg p-2 transition-colors"
                onClick={() => {
                  useTaskStore.getState().setFilter({ status: 'all' });
                  handleNavigation('/tasks');
                }}
              >
                <div className="text-2xl font-bold text-secondary-600">
                  {summary.status.total}
                </div>
                <div className="text-xs text-secondary-500">Total</div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => (
            <button
              key={item.key}
              onClick={() => handleNavigation(item.path)}
              className={clsx(
                'w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-colors',
                currentPage === item.key
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                  : 'text-secondary-700 hover:text-secondary-900 hover:bg-secondary-100'
              )}
            >
              <div className="flex items-center space-x-3">
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <Badge variant="primary" size="sm">
                  {item.badge}
                </Badge>
              )}
            </button>
          ))}
        </nav>

        {/* Bottom actions */}
        <div className="border-t border-secondary-200 p-4 space-y-2">
          <Button className="w-full justify-start" variant="ghost" size="sm">
            <Bell className="w-4 h-4 mr-3" />
            Notifications
          </Button>
          <div className="text-xs text-secondary-500 text-center pt-2">
            TaskWarrior Frontend v1.0.0
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-secondary-200">
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="lg:hidden p-2 rounded-md text-secondary-500 hover:text-secondary-700"
              >
                <Menu className="w-5 h-5" />
              </button>
            </div>

            <div className="flex items-center space-x-4">
              {/* Search Bar */}
              {isSearchOpen ? (
                <form onSubmit={handleSearch} className="flex items-center space-x-2">
                  <Input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search tasks..."
                    className="w-64"
                    autoFocus
                  />
                  <Button type="submit" size="sm" variant="ghost">
                    <Search className="w-4 h-4" />
                  </Button>
                  <button
                    type="button"
                    onClick={() => setIsSearchOpen(false)}
                    className="p-2 rounded-md text-secondary-500 hover:text-secondary-700"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </form>
              ) : (
                <>
                  <button 
                    onClick={toggleSearch}
                    className="p-2 rounded-md text-secondary-500 hover:text-secondary-700"
                    title="Search tasks"
                  >
                    <Search className="w-5 h-5" />
                  </button>
                  <Button size="sm" onClick={() => openTaskForm()}>
                    <Plus className="w-4 h-4 mr-2" />
                    Quick Add
                  </Button>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto px-6 py-8 max-w-7xl">
            {children}
          </div>
        </main>
      </div>

      {/* Global Task Form Modal */}
      <TaskForm
        task={editingTask || undefined}
        isOpen={isTaskFormOpen}
        onClose={closeTaskForm}
      />
    </div>
  );
};

export default Layout;