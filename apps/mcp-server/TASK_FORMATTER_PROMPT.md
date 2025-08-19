# 📝 Task Formatter Prompt

## Overview

The **Task Formatter Prompt** helps AI agents rewrite task descriptions using structured markdown format with descriptive titles. This addresses TaskWarrior's limitation of having only a single description field by providing a standardized, readable structure.

## 🎯 Purpose

Since TaskWarrior stores everything in one description field, this prompt ensures tasks are:
- **Well-structured** with clear markdown formatting
- **Descriptive** with meaningful titles using `## heading`
- **Actionable** with specific details and acceptance criteria
- **Consistent** across all tasks in the system

## 🔧 How It Works

### 1. Prompt Activation
In Claude Desktop, use the **"Task Formatter"** prompt to help structure your task descriptions.

### 2. Smart Context Generation
The prompt automatically includes:
- Examples from your recent tasks for consistency
- Project context for better organization
- Current task patterns for maintaining style

### 3. Structured Format Guidelines
```markdown
## Descriptive Title

Brief summary of what needs to be done.

**Details:**
- Specific requirement 1
- Specific requirement 2
- Technical considerations
- Context and background

**Acceptance Criteria:**
- [ ] Measurable outcome 1
- [ ] Measurable outcome 2
- [ ] Quality standards
```

## 📚 Example Transformations

### ❌ Before: Simple Description
```
fix login bug
```

### ✅ After: Structured Markdown
```
## Fix User Login Authentication Bug

Resolve the authentication issue that prevents users from successfully logging into the application.

**Details:**
- Users cannot login with valid credentials
- Issue started after recent security update
- Affects both web and mobile interfaces
- Error message: "Invalid credentials" even with correct password

**Acceptance Criteria:**
- [ ] Users can login with correct credentials
- [ ] Error messages are accurate and helpful
- [ ] Login works on all platforms
- [ ] Session management is secure
```

### ❌ Before: Vague Task
```
performance improvements
```

### ✅ After: Detailed Structure
```
## Optimize Application Performance

Implement performance improvements to reduce page load times and improve user experience.

**Details:**
- Database queries are taking too long (>2 seconds)
- Image loading is slow on mobile devices
- JavaScript bundle size has grown to 3MB+
- Users report slow navigation between pages

**Technical Tasks:**
- [ ] Add database query indexing
- [ ] Implement image compression and lazy loading
- [ ] Split JavaScript bundle by routes
- [ ] Add performance monitoring
- [ ] Set up caching for static assets

**Success Metrics:**
- Page load time < 1 second
- Lighthouse performance score > 90
- Reduced bounce rate by 20%
```

## 🚀 Usage Workflow

### In Claude Desktop:

1. **Activate Prompt**: Select "Task Formatter" from available prompts
2. **Describe Task**: Provide a brief description of what you want to accomplish
3. **Get Structured Version**: Claude rewrites it with proper markdown structure
4. **Create Task**: Use the formatted description when creating the task
5. **Enjoy Benefits**: Better organized, more actionable tasks

### Example Conversation:
```
You: "I need to update the user dashboard with new analytics"

Claude (using Task Formatter): 
## Update User Dashboard Analytics

Add new analytics widgets to the user dashboard to provide better insights into user behavior and system usage.

**Details:**
- Add real-time user activity charts
- Include system performance metrics
- Implement data filtering by date range
- Ensure responsive design for mobile devices

**Acceptance Criteria:**
- [ ] Analytics widgets display real-time data
- [ ] Charts are interactive and responsive
- [ ] Data can be filtered by time periods
- [ ] Dashboard loads in under 2 seconds
- [ ] Mobile layout is user-friendly
```

## 💡 Benefits

### For Task Management:
- **Clarity**: Clear understanding of what needs to be done
- **Actionability**: Specific steps and criteria for completion
- **Consistency**: All tasks follow the same structured format
- **Searchability**: Better task discovery through descriptive titles

### For Team Collaboration:
- **Knowledge Transfer**: New team members understand tasks quickly
- **Progress Tracking**: Clear acceptance criteria for measuring completion
- **Context Preservation**: Important details and background information included
- **Quality Assurance**: Consistent format ensures nothing is overlooked

## 🎨 Customization

The prompt adapts to your existing tasks by:
- **Learning from Context**: Uses recent tasks to understand your preferred style
- **Project Awareness**: Considers current project patterns
- **Consistency Maintenance**: Ensures new tasks match existing format patterns

## 📊 Server Integration

- **Prompt Name**: `task_formatter`
- **Type**: Smart contextual prompt
- **Context**: Uses recent tasks for consistency
- **Output**: Structured markdown format instructions
- **Integration**: Works seamlessly with all task creation workflows

## 🔄 Updated Server Stats

- **Total Prompts**: 3 (was 2)
  - `daily_planning` - Help plan daily tasks
  - `task_prioritization` - Help prioritize tasks  
  - `task_formatter` - Format task descriptions ✨ **NEW**

This prompt transforms TaskWarrior's single-field limitation into a powerful structured task management system while maintaining full compatibility with the underlying TaskWarrior infrastructure.