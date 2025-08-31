---
description: Prioritize and organize tasks for optimal execution strategies
globs:
alwaysApply: false
version: 1.0
encoding: UTF-8
---

# Task Prioritization Rules

## Overview

Analyze and reorganize tasks from an existing tasks.md file based on specified prioritization criteria, enabling parallel execution, dependency management, and strategic task ordering.

<pre_flight_check>
  EXECUTE: @.agent-os/instructions/meta/pre-flight.md
</pre_flight_check>

<process_flow>

<step number="1" subagent="context-fetcher" name="load_tasks">

### Step 1: Load Existing Tasks

Use the context-fetcher subagent to read the current tasks.md file from the active spec folder and parse the task structure.

<task_loading>
  <source>@.agent-os/specs/*/tasks.md</source>
  <parse>
    - major_tasks: numbered items (1, 2, 3...)
    - subtasks: decimal notation (1.1, 1.2...)
    - dependencies: implicit from ordering
    - status: checkbox state ([ ] or [x])
  </parse>
</task_loading>

</step>

<step number="2" name="prioritization_criteria">

### Step 2: Determine Prioritization Criteria

Ask the user which prioritization strategy to apply or accept user-specified criteria.

<prioritization_strategies>

<strategy name="parallel_execution">
  <description>Organize tasks for maximum parallel execution by multiple agents</description>
  <criteria>
    - Identify independent task groups with no shared dependencies
    - Separate by component boundaries (stores, UI components, filters)
    - Isolate by file boundaries to prevent merge conflicts
    - Group by domain (data layer, presentation layer, business logic)
  </criteria>
  <output>Task groups that can be worked on simultaneously</output>
</strategy>

<strategy name="complexity_based">
  <description>Order tasks from simplest to most complex or vice versa</description>
  <criteria>
    - Simple: Single file changes, minimal dependencies
    - Moderate: Multi-file changes within single component
    - Complex: Cross-component changes, architectural modifications
  </criteria>
  <complexity_indicators>
    - subtask_count: More subtasks = higher complexity
    - file_count: More files touched = higher complexity
    - integration_points: More integrations = higher complexity
    - testing_requirements: More test types = higher complexity
  </complexity_indicators>
</strategy>

<strategy name="importance_based">
  <description>Prioritize by business value and user impact</description>
  <criteria>
    - Critical: Core functionality, blocking issues, user-facing bugs
    - High: Major features, performance improvements
    - Medium: Enhancements, minor features
    - Low: Nice-to-have, technical debt, documentation
  </criteria>
  <importance_indicators>
    - user_impact: Direct user benefit
    - business_value: Revenue or efficiency impact
    - risk_mitigation: Security or stability improvement
    - technical_debt: Long-term maintainability
  </importance_indicators>
</strategy>

<strategy name="dependency_based">
  <description>Order tasks based on technical dependencies</description>
  <criteria>
    - Foundation: Data models, stores, core utilities
    - Integration: API connections, service layers
    - Business Logic: Core functionality, algorithms
    - Presentation: UI components, views
    - Polish: Styling, animations, optimizations
  </criteria>
  <dependency_rules>
    - stores_before_components: Data layer must exist first
    - tests_before_implementation: TDD approach
    - core_before_features: Base functionality before enhancements
    - backend_before_frontend: API before UI consumption
  </dependency_rules>
</strategy>

<strategy name="deadline_based">
  <description>Organize by time constraints and deadlines</description>
  <criteria>
    - Immediate: Must be done today
    - Short-term: Within current sprint (1-2 weeks)
    - Medium-term: Current release cycle (2-4 weeks)
    - Long-term: Future releases (>4 weeks)
  </criteria>
  <deadline_factors>
    - external_dependencies: Waiting on other teams
    - release_schedule: Production deployment dates
    - compliance_requirements: Regulatory deadlines
    - customer_commitments: Promised delivery dates
  </deadline_factors>
</strategy>

<strategy name="hybrid">
  <description>Combine multiple prioritization strategies</description>
  <approach>
    - Apply primary strategy first
    - Use secondary strategy for tie-breaking
    - Consider tertiary factors for fine-tuning
  </approach>
  <example>
    primary: dependency_based
    secondary: complexity_based
    tertiary: importance_based
  </example>
</strategy>

</prioritization_strategies>

<user_prompt>
  Which prioritization strategy would you like to apply?
  
  1. **Parallel Execution** - Organize for multiple agents working simultaneously
  2. **Complexity-Based** - Order by task complexity (simple→complex or complex→simple)
  3. **Importance-Based** - Prioritize by business value and user impact
  4. **Dependency-Based** - Order by technical dependencies
  5. **Deadline-Based** - Organize by time constraints
  6. **Hybrid** - Combine multiple strategies
  7. **Custom** - Specify your own criteria
  
  Please specify your choice and any additional parameters.
</user_prompt>

</step>

<step number="3" name="task_analysis">

### Step 3: Analyze Task Relationships

Perform deep analysis of task relationships and dependencies based on the selected strategy.

<analysis_dimensions>

<dimension name="file_boundaries">
  <identify>
    - Which files each task modifies
    - Potential merge conflicts
    - Shared dependencies
  </identify>
  <classify>
    - Isolated: Single file or component
    - Overlapping: Shared files with other tasks
    - Dependent: Requires output from other tasks
  </classify>
</dimension>

<dimension name="component_boundaries">
  <identify>
    - Component ownership per task
    - Cross-component dependencies
    - Integration points
  </identify>
  <classify>
    - Self-contained: Within single component
    - Cross-cutting: Affects multiple components
    - Infrastructure: Affects system-wide functionality
  </classify>
</dimension>

<dimension name="technical_dependencies">
  <identify>
    - Required inputs from other tasks
    - Shared resources or services
    - Order constraints
  </identify>
  <dependency_graph>
    - Build directed acyclic graph (DAG)
    - Identify critical path
    - Find parallelization opportunities
  </dependency_graph>
</dimension>

<dimension name="testing_requirements">
  <identify>
    - Unit test dependencies
    - Integration test requirements
    - E2E test coordination
  </identify>
  <test_strategy>
    - Isolated: Can test independently
    - Integrated: Requires other components
    - System: Needs full system testing
  </test_strategy>
</dimension>

</analysis_dimensions>

</step>

<step number="4" subagent="file-creator" name="generate_prioritized_tasks">

### Step 4: Generate Prioritized Task Structure

Use the file-creator subagent to create prioritized-tasks.md in the spec folder with the reorganized task structure.

<file_template>
  <header>
    # Prioritized Tasks
    
    > Original: @.agent-os/specs/[SPEC_NAME]/tasks.md
    > Strategy: [SELECTED_STRATEGY]
    > Generated: [CURRENT_DATE]
  </header>
</file_template>

<parallel_execution_template>
  ## Parallel Execution Groups
  
  ### Group A: Independent Store Operations
  **Agent Assignment**: Agent 1
  **Files**: stores/geodata.js, stores/singletable.js
  **Dependencies**: None
  
  - [ ] 1. Unified Geolocation Store Implementation
    - [ ] 1.1 Write comprehensive unit tests
    - [ ] 1.2 Implement unifiedResults state structure
    [...]
  
  ### Group B: UI Component Updates
  **Agent Assignment**: Agent 2
  **Files**: components/shared/table/DataTable.vue
  **Dependencies**: None (can use mocked store)
  
  - [ ] 3. DataTable Component Enhancement
    - [ ] 3.1 Write comprehensive tests
    - [ ] 3.2 Add query source column support
    [...]
  
  ### Group C: Filter System
  **Agent Assignment**: Agent 3
  **Files**: components/form/*, components/shared/filters/*
  **Dependencies**: None
  
  - [ ] 5. Filter System and Navigation Updates
    - [ ] 5.1 Write comprehensive tests
    - [ ] 5.2 Extend existing filter components
    [...]
  
  ### Integration Phase (Sequential)
  **Dependencies**: Groups A, B, C must complete first
  
  - [ ] 2. GeolocationTabPanel Enhancement (integrates A + B + C)
  - [ ] 4. GeolocationCardPanel Integration (integrates A + B)
</parallel_execution_template>

<dependency_based_template>
  ## Dependency-Ordered Tasks
  
  ### Phase 1: Foundation Layer
  **No Dependencies - Can Start Immediately**
  
  - [ ] 1. Unified Geolocation Store Implementation
    - Core data layer required by all other components
    - Estimated: 2-3 days
  
  ### Phase 2: Core Components
  **Depends on**: Phase 1 completion
  
  - [ ] 3. DataTable Component Enhancement
    - Requires unified data structure from Phase 1
    - Can run parallel with other Phase 2 tasks
  
  - [ ] 5. Filter System Updates
    - Requires unified filter structure from Phase 1
    - Can run parallel with other Phase 2 tasks
  
  ### Phase 3: Integration Layer
  **Depends on**: Phase 1 and Phase 2 completion
  
  - [ ] 2. GeolocationTabPanel Enhancement
    - Integrates store, table, and filters
    - Requires all foundational components
  
  - [ ] 4. GeolocationCardPanel Integration
    - Integrates store and display components
    - Can run parallel with Task 2
</dependency_based_template>

<complexity_scoring>
  ## Complexity Scores
  
  | Task | Subtasks | Files | Integrations | Complexity | Priority |
  |------|----------|-------|--------------|------------|----------|
  | 5. Filter System | 8 | 5+ | High | 8/10 | Do First/Last |
  | 1. Store Implementation | 8 | 2 | Medium | 7/10 | Do Second |
  | 2. TabPanel Enhancement | 8 | 1 | Very High | 9/10 | Do Last/First |
  | 3. DataTable Enhancement | 8 | 1 | Low | 5/10 | Do Early |
  | 4. CardPanel Integration | 8 | 1 | Medium | 6/10 | Do Middle |
</complexity_scoring>

<importance_matrix>
  ## Importance/Impact Matrix
  
  | Task | User Impact | Business Value | Risk Mitigation | Total Score | Priority |
  |------|------------|----------------|-----------------|-------------|----------|
  | 1. Store | Critical | High | High | 10/10 | P0 - Immediate |
  | 2. TabPanel | Critical | High | Medium | 9/10 | P0 - Immediate |
  | 3. DataTable | High | Medium | Low | 6/10 | P1 - High |
  | 4. CardPanel | Medium | Medium | Low | 5/10 | P2 - Medium |
  | 5. Filter | High | High | Medium | 8/10 | P1 - High |
</importance_matrix>

</step>

<step number="5" name="execution_recommendations">

### Step 5: Generate Execution Recommendations

Provide specific recommendations for executing the prioritized tasks based on the selected strategy.

<recommendations>

<parallel_execution_recommendations>
  ## Parallel Execution Recommendations
  
  ### Team Structure
  - **Minimum Agents**: 3 for optimal parallelization
  - **Maximum Agents**: 5 (diminishing returns beyond this)
  - **Ideal Configuration**: 3 agents + 1 integration coordinator
  
  ### Workflow
  1. Assign each agent to an independent group
  2. Use feature branches for each group
  3. Daily sync for integration planning
  4. Integration coordinator manages merges
  
  ### Conflict Avoidance
  - Each group works on separate file sets
  - Shared interfaces defined upfront
  - Mock dependencies for independent testing
  - Integration tests run after group completion
</parallel_execution_recommendations>

<sequential_recommendations>
  ## Sequential Execution Recommendations
  
  ### Critical Path
  1. Complete foundation tasks first (blocks everything)
  2. Parallelize independent tasks in each phase
  3. Integration tasks only after dependencies met
  4. Testing and validation at phase boundaries
  
  ### Risk Mitigation
  - Test each phase thoroughly before proceeding
  - Maintain rollback points at phase boundaries
  - Document integration contracts between phases
  - Keep integration surface area minimal
</sequential_recommendations>

<hybrid_recommendations>
  ## Hybrid Execution Recommendations
  
  ### Optimal Strategy
  1. Start with foundation layer (sequential)
  2. Parallelize middle layer components
  3. Converge for integration phase
  4. Final validation and polish (sequential)
  
  ### Resource Allocation
  - 1 agent on critical path tasks
  - 2-3 agents on parallelizable work
  - All agents converge for integration
  - Dedicated QA for continuous testing
</hybrid_recommendations>

</recommendations>

</step>

<step number="6" name="update_tracking">

### Step 6: Create Execution Tracking

Generate a tracking document for monitoring progress across the prioritized tasks.

<tracking_template>
  ## Execution Tracking
  
  ### Parallel Groups Status
  | Group | Agent | Status | Progress | Blockers | ETA |
  |-------|-------|--------|----------|----------|-----|
  | A | Agent-1 | In Progress | 3/8 | None | 2 days |
  | B | Agent-2 | In Progress | 2/8 | Waiting on API mock | 3 days |
  | C | Agent-3 | Not Started | 0/8 | None | 4 days |
  
  ### Dependencies Resolved
  - [x] Store data structure defined
  - [x] Component interfaces agreed
  - [ ] Filter API contract finalized
  - [ ] Integration test plan approved
  
  ### Integration Readiness
  - [ ] Group A complete and tested
  - [ ] Group B complete and tested
  - [ ] Group C complete and tested
  - [ ] Integration environment prepared
  - [ ] Merge strategy defined
</tracking_template>

</step>

</process_flow>

<output_files>
  <file name="prioritized-tasks.md">
    Reorganized task list based on selected strategy
  </file>
  <file name="execution-plan.md" optional="true">
    Detailed execution plan with timelines and assignments
  </file>
  <file name="dependency-graph.md" optional="true">
    Visual representation of task dependencies
  </file>
  <file name="tracking.md" optional="true">
    Progress tracking template for execution
  </file>
</output_files>

<post_flight_check>
  EXECUTE: @.agent-os/instructions/meta/post-flight.md
</post_flight_check>