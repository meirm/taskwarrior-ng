import React from 'react';
import { useTaskStore } from '@/stores/taskStore';
import Layout from '@/components/Layout';
import TaskList from '@/components/TaskList';

const TasksPage: React.FC = () => {
  const { loadTasks, loadMetadata } = useTaskStore();

  React.useEffect(() => {
    loadTasks();
    loadMetadata();
  }, [loadTasks, loadMetadata]);

  return (
    <Layout currentPage="tasks">
      <TaskList />
    </Layout>
  );
};

export default TasksPage;