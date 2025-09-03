import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import TasksPage from '@/pages/TasksPage';
import DashboardPage from '@/pages/DashboardPage';
import ReportsPage from '@/pages/ReportsPage';
import SettingsPage from '@/pages/SettingsPage';
import TrashPageWithLayout from '@/pages/TrashPageWithLayout';
import { AboutPage } from '@/pages/AboutPage';
import ProjectSelectorTestPage from '@/pages/ProjectSelectorTestPage';
import Layout from '@/components/Layout';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/trash" element={<TrashPageWithLayout />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/about" element={
            <Layout>
              <AboutPage />
            </Layout>
          } />
          <Route path="/test-project-selector" element={<ProjectSelectorTestPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;