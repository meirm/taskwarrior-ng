import React from 'react';
import Layout from '@/components/Layout';
import { Settings, User, Bell, Shield, Palette, Database } from 'lucide-react';
import Button from '@/components/ui/Button';

const SettingsPage: React.FC = () => {
  const settingsSections = [
    {
      title: 'Profile',
      icon: User,
      description: 'Manage your personal information and preferences',
    },
    {
      title: 'Notifications',
      icon: Bell,
      description: 'Configure how and when you receive notifications',
    },
    {
      title: 'Appearance',
      icon: Palette,
      description: 'Customize the look and feel of the application',
    },
    {
      title: 'Security',
      icon: Shield,
      description: 'Manage your security settings and privacy',
    },
    {
      title: 'Data & Storage',
      icon: Database,
      description: 'Control your data and storage preferences',
    },
  ];

  return (
    <Layout currentPage="settings">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Settings</h1>
          <p className="text-secondary-600 mt-1">
            Manage your application preferences and configuration
          </p>
        </div>

        {/* Settings Sections */}
        <div className="space-y-4">
          {settingsSections.map((section) => (
            <div key={section.title} className="bg-white rounded-lg border shadow-sm p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-primary-50 rounded-lg">
                    <section.icon className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-secondary-900">
                      {section.title}
                    </h3>
                    <p className="text-sm text-secondary-600 mt-1">
                      {section.description}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Coming Soon Notice */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <div className="flex">
            <Settings className="w-5 h-5 text-primary-600 mr-3 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-primary-900">
                Settings functionality coming soon
              </h4>
              <p className="text-sm text-primary-700 mt-1">
                We're working on bringing you full control over your TaskWarrior experience. 
                Settings will allow you to customize themes, notifications, shortcuts, and more.
              </p>
            </div>
          </div>
        </div>

        {/* Version Info */}
        <div className="text-center text-sm text-secondary-500 pt-8">
          <p>TaskWarrior Frontend v1.0.0</p>
          <p className="mt-1">Built with React, TypeScript, and Tailwind CSS</p>
        </div>
      </div>
    </Layout>
  );
};

export default SettingsPage;