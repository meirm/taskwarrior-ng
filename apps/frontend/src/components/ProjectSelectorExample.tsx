import React, { useState } from 'react';
import ProjectSelector from './ProjectSelector';

/**
 * Example component demonstrating ProjectSelector usage
 * This can be used for testing and as a reference for integration
 */
const ProjectSelectorExample: React.FC = () => {
  const [selectedProject, setSelectedProject] = useState<string | undefined>();
  
  // Example projects with hierarchical structure
  const exampleProjects = [
    'Personal',
    'Work',
    'Work.Frontend',
    'Work.Frontend.Components',
    'Work.Frontend.Pages',
    'Work.Backend',
    'Work.Backend.API',
    'Work.Backend.Database',
    'Home',
    'Home.Renovation',
    'Home.Garden',
    'Learning',
    'Learning.React',
    'Learning.TypeScript',
    'Learning.Python',
  ];

  return (
    <div className="p-8 max-w-md mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-secondary-800">
        ProjectSelector Component Example
      </h2>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium text-secondary-700 mb-2">
            Basic Usage
          </h3>
          <ProjectSelector
            value={selectedProject}
            onChange={setSelectedProject}
            projects={exampleProjects}
            label="Project"
            helperText="Select an existing project or create a new one"
          />
          <p className="mt-2 text-sm text-secondary-600">
            Selected: {selectedProject || 'None'}
          </p>
        </div>

        <div>
          <h3 className="text-lg font-medium text-secondary-700 mb-2">
            Required Field
          </h3>
          <ProjectSelector
            value={undefined}
            onChange={() => {}}
            projects={exampleProjects}
            label="Required Project"
            required
            helperText="This field is required"
          />
        </div>

        <div>
          <h3 className="text-lg font-medium text-secondary-700 mb-2">
            With Error State
          </h3>
          <ProjectSelector
            value={undefined}
            onChange={() => {}}
            projects={exampleProjects}
            label="Project with Error"
            error="Please select a project"
          />
        </div>

        <div>
          <h3 className="text-lg font-medium text-secondary-700 mb-2">
            Disabled State
          </h3>
          <ProjectSelector
            value="Work.Frontend"
            onChange={() => {}}
            projects={exampleProjects}
            label="Disabled Project"
            disabled
            helperText="This field is disabled"
          />
        </div>

        <div>
          <h3 className="text-lg font-medium text-secondary-700 mb-2">
            Empty Projects List
          </h3>
          <ProjectSelector
            value={undefined}
            onChange={() => {}}
            projects={[]}
            label="No Projects Available"
            placeholder="Type to create your first project"
            helperText="Start typing to create a new project"
          />
        </div>
      </div>

      <div className="mt-8 p-4 bg-secondary-50 rounded-lg">
        <h3 className="text-sm font-medium text-secondary-700 mb-2">
          Features Demonstrated:
        </h3>
        <ul className="text-sm text-secondary-600 space-y-1">
          <li>✓ Search existing projects</li>
          <li>✓ Create new projects by typing</li>
          <li>✓ Hierarchical project display (dot notation)</li>
          <li>✓ Keyboard navigation (↑↓ Enter Esc)</li>
          <li>✓ Clear selection with X button</li>
          <li>✓ Visual indicators for new projects (+ icon)</li>
          <li>✓ Selected item check mark</li>
          <li>✓ Debounced search (200ms)</li>
          <li>✓ Accessibility support (ARIA labels)</li>
          <li>✓ Required, disabled, and error states</li>
        </ul>
      </div>
    </div>
  );
};

export default ProjectSelectorExample;