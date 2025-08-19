import React from 'react';
import Layout from '@/components/Layout';
import { BarChart3, TrendingUp, Calendar, Clock } from 'lucide-react';

const ReportsPage: React.FC = () => {
  return (
    <Layout currentPage="reports">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Reports</h1>
          <p className="text-secondary-600 mt-1">
            Analytics and insights about your task management
          </p>
        </div>

        {/* Coming Soon Message */}
        <div className="bg-white rounded-lg border shadow-sm p-12 text-center">
          <BarChart3 className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-secondary-900 mb-2">
            Reports Coming Soon
          </h2>
          <p className="text-secondary-600 max-w-md mx-auto">
            We're working on bringing you detailed analytics, productivity insights, 
            and beautiful visualizations of your task management data.
          </p>
          
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
            <div className="p-4 bg-secondary-50 rounded-lg">
              <TrendingUp className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <h3 className="font-medium text-secondary-900">Productivity Trends</h3>
              <p className="text-sm text-secondary-600 mt-1">
                Track your completion rates over time
              </p>
            </div>
            <div className="p-4 bg-secondary-50 rounded-lg">
              <Calendar className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <h3 className="font-medium text-secondary-900">Time Analysis</h3>
              <p className="text-sm text-secondary-600 mt-1">
                See when you're most productive
              </p>
            </div>
            <div className="p-4 bg-secondary-50 rounded-lg">
              <Clock className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <h3 className="font-medium text-secondary-900">Task Duration</h3>
              <p className="text-sm text-secondary-600 mt-1">
                Analyze how long tasks take to complete
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ReportsPage;