import React from 'react';
import Layout from '@/components/Layout';
import ProjectSelectorExample from '@/components/ProjectSelectorExample';

/**
 * Test page for the ProjectSelector component
 */
const ProjectSelectorTestPage: React.FC = () => {
  return (
    <Layout>
      <div className="min-h-screen bg-secondary-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-8">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-secondary-900 mb-2">
                ProjectSelector Component Test
              </h1>
              <p className="text-secondary-600">
                Test the ProjectSelector component functionality before integrating into task forms.
              </p>
            </div>
            
            <ProjectSelectorExample />
            
            <div className="mt-12 p-6 bg-blue-50 border border-blue-200 rounded-lg">
              <h2 className="text-lg font-semibold text-blue-900 mb-4">
                Testing Instructions
              </h2>
              <div className="space-y-4 text-sm text-blue-800">
                <div>
                  <h3 className="font-medium mb-2">Basic Functionality:</h3>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Click on the first selector to open the dropdown</li>
                    <li>Type to search existing projects (try "Work" or "Learn")</li>
                    <li>Type a new project name to see the "Create" option</li>
                    <li>Use arrow keys to navigate options</li>
                    <li>Press Enter to select or Escape to close</li>
                    <li>Click the X button to clear selection</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-medium mb-2">Advanced Features:</h3>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Notice hierarchical projects are indented (Work.Frontend, Work.Backend)</li>
                    <li>Search is debounced (200ms delay) for performance</li>
                    <li>Selected projects show a check mark</li>
                    <li>New project options show a plus icon</li>
                    <li>Dropdown closes when clicking outside</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-medium mb-2">States to Test:</h3>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Required field validation (asterisk indicator)</li>
                    <li>Error state display (red border and message)</li>
                    <li>Disabled state (grayed out, not interactive)</li>
                    <li>Empty project list (only allows creation)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ProjectSelectorTestPage;