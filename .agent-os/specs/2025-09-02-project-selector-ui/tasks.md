# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-09-02-project-selector-ui/spec.md

> Created: 2025-09-02
> Status: Ready for Implementation

## Tasks

- [ ] 1. Create ProjectSelector Component
  - [ ] 1.1 Write tests for ProjectSelector component behavior
  - [ ] 1.2 Create base ProjectSelector.tsx component with TypeScript interfaces
  - [ ] 1.3 Implement searchable dropdown with existing project list
  - [ ] 1.4 Add "Create new project" option with visual indicators
  - [ ] 1.5 Implement keyboard navigation and accessibility features
  - [ ] 1.6 Add autocomplete and debounced search functionality
  - [ ] 1.7 Support hierarchical project display (dot notation)
  - [ ] 1.8 Verify all component tests pass

- [ ] 2. Integrate API and State Management
  - [ ] 2.1 Write tests for API integration and state updates
  - [ ] 2.2 Create Zustand store slice for project list caching
  - [ ] 2.3 Implement TanStack Query hooks for fetching projects
  - [ ] 2.4 Add optimistic updates for project creation
  - [ ] 2.5 Set up cache invalidation on project changes
  - [ ] 2.6 Verify all integration tests pass

- [ ] 3. Integrate into Task Creation Form
  - [ ] 3.1 Write tests for task creation with project selection
  - [ ] 3.2 Import and add ProjectSelector to NewTaskForm component
  - [ ] 3.3 Wire up form state management for project field
  - [ ] 3.4 Update task creation API calls to include project
  - [ ] 3.5 Add form validation and error handling
  - [ ] 3.6 Test end-to-end task creation with projects
  - [ ] 3.7 Verify all task creation tests pass

- [ ] 4. Integrate into Task Edit Form
  - [ ] 4.1 Write tests for task editing with project changes
  - [ ] 4.2 Add ProjectSelector to TaskEditForm component
  - [ ] 4.3 Pre-populate selector with current task project
  - [ ] 4.4 Implement project removal (clear/no project option)
  - [ ] 4.5 Update task modification API calls for project changes
  - [ ] 4.6 Add change tracking and dirty state management
  - [ ] 4.7 Test end-to-end task editing with project changes
  - [ ] 4.8 Verify all task edit tests pass

- [ ] 5. Polish and Final Testing
  - [ ] 5.1 Write end-to-end integration tests for complete workflow
  - [ ] 5.2 Test mobile responsiveness and touch interactions
  - [ ] 5.3 Verify accessibility with screen readers
  - [ ] 5.4 Add loading states and error boundaries
  - [ ] 5.5 Optimize performance and bundle size
  - [ ] 5.6 Update documentation and component stories
  - [ ] 5.7 Conduct manual testing of all user flows
  - [ ] 5.8 Verify all tests pass and feature is production-ready