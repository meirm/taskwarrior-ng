# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-09-02-project-selector-ui/spec.md

> Created: 2025-09-02
> Version: 1.0.0

## Technical Requirements

### Component Architecture
- **Component Name**: ProjectSelector
- **Location**: `apps/frontend/src/components/ProjectSelector.tsx`
- **Type**: React functional component with TypeScript
- **State Management**: Use Zustand store for project list caching
- **Data Fetching**: TanStack Query for project list with optimistic updates

### UI/UX Specifications
- **Base Component**: Use existing Combobox pattern from UI library (shadcn/ui or similar)
- **Search**: Client-side filtering with debounce (200ms)
- **Visual Indicators**:
  - Existing projects: Normal text with optional task count badge
  - New project creation: "Create '[input]'" option with plus icon
  - Hierarchical projects: Indented display for sub-projects
- **Keyboard Navigation**: Full keyboard support (arrow keys, enter, escape)
- **Responsive**: Mobile-friendly with touch support

### Integration Requirements

#### Task Creation Form
- **Field Position**: Below description, above priority/due date fields
- **Default State**: Empty with placeholder "Select or create project"
- **Validation**: Optional field, no validation required
- **State Updates**: Update form state on selection/creation

#### Task Edit Form  
- **Current Value**: Pre-populate with existing task project
- **Clear Option**: Include "No Project" or clear button
- **Change Tracking**: Mark form as dirty on project change
- **Optimistic Updates**: Update UI immediately, sync with backend

### API Integration
- **Get Projects**: Use existing `getProjects()` from API client
- **Task Operations**: 
  - Create: Include `project` in task creation payload
  - Update: Include `project` in task modification payload
- **Cache Invalidation**: Invalidate project list when new project created

### Performance Criteria
- **Initial Load**: Project list cached for session duration
- **Search Response**: <50ms for client-side filtering
- **Creation Feedback**: Immediate UI update with optimistic rendering
- **Network Requests**: Debounced to prevent excessive API calls

## Approach

### Implementation Strategy
1. **Phase 1**: Create base ProjectSelector component with search and selection
2. **Phase 2**: Integrate with task creation form
3. **Phase 3**: Add project creation functionality
4. **Phase 4**: Integrate with task editing form
5. **Phase 5**: Performance optimization and caching

### Component Structure
```typescript
interface ProjectSelectorProps {
  value?: string;
  onValueChange: (project: string | null) => void;
  placeholder?: string;
  className?: string;
}
```

### State Management Pattern
- Use TanStack Query for server state (project list)
- Local component state for search input and selection
- Zustand store for cross-component project caching
- Form libraries (React Hook Form) for form integration

## External Dependencies

**@tanstack/react-query** - Already in use for data fetching

**react-select** or **@radix-ui/react-select** - Advanced select component with built-in search
**Justification:** Need a robust, accessible select component with search capabilities. Both options provide excellent accessibility, keyboard navigation, and customization options. React-select is more feature-rich while Radix UI is lighter and more composable.

**lodash.debounce** - Debounce search input
**Justification:** Prevent excessive re-renders during typing. Already likely present in the codebase.