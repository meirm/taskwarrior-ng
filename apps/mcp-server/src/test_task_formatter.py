#!/usr/bin/env python3
"""
Test and demonstrate the task formatter prompt
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from taskwarrior_mcp_server import tw, safe_get_task_field
from tasklib import Task

def create_sample_tasks():
    """Create some sample tasks to demonstrate the formatter context"""
    print("📝 Creating sample tasks for context...")
    
    sample_tasks = [
        "Update user profile page with new avatar upload feature",
        "Fix database connection timeout issue in production",
        "Write API documentation for the new payment endpoints"
    ]
    
    created_ids = []
    for i, desc in enumerate(sample_tasks):
        task = Task(tw, description=desc)
        task['project'] = f"Project{i+1}"
        task['priority'] = ['H', 'M', 'L'][i]
        task.save()
        created_ids.append(task['id'])
        print(f"   ✅ Created task {task['id']}: {desc[:40]}...")
    
    return created_ids

def demonstrate_task_formatter():
    """Demonstrate how the task formatter prompt works"""
    print("\n🔧 Demonstrating Task Formatter Prompt...")
    
    # Import and simulate the prompt function
    from taskwarrior_mcp_server import task_formatter
    
    # This would normally be called by Claude Desktop
    prompt_text = "This is what the task_formatter prompt would return:"
    
    print(f"\n📋 Task Formatter Prompt Output:")
    print("=" * 60)
    print(prompt_text)
    print("=" * 60)
    
    # Show examples of how different task descriptions would be improved
    examples = [
        {
            "original": "fix login bug",
            "improved": """## Fix User Login Authentication Bug

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
- [ ] Session management is secure"""
        },
        {
            "original": "update docs",
            "improved": """## Update API Documentation

Update the API documentation to reflect the latest changes in the authentication endpoints.

**Details:**
- Add documentation for new OAuth 2.0 flow
- Update parameter descriptions for user endpoints
- Include new error codes and responses
- Add code examples in multiple languages

**Acceptance Criteria:**
- [ ] All new endpoints are documented
- [ ] Code examples are tested and working
- [ ] Documentation is reviewed by team lead
- [ ] Changes are deployed to documentation site"""
        },
        {
            "original": "performance improvements",
            "improved": """## Optimize Application Performance

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
- Reduced bounce rate by 20%"""
        }
    ]
    
    print(f"\n📚 Example Transformations:")
    print("=" * 60)
    
    for i, example in enumerate(examples, 1):
        print(f"\n**Example {i}:**")
        print(f"❌ Original: \"{example['original']}\"")
        print(f"\n✅ Improved:")
        print(example['improved'])
        print("\n" + "-" * 40)
    
    return True

def show_context_example():
    """Show how the prompt uses existing tasks for context"""
    print(f"\n📊 Context Generation Example:")
    print("=" * 40)
    
    # Get some actual pending tasks
    pending = tw.tasks.pending()
    recent_tasks = []
    
    for task in sorted(pending, key=lambda t: safe_get_task_field(t, 'entry') or "", reverse=True)[:3]:
        task_desc = safe_get_task_field(task, 'description')
        task_project = safe_get_task_field(task, 'project')
        if task_desc:
            recent_tasks.append({
                'description': task_desc[:80] + '...' if len(task_desc) > 80 else task_desc,
                'project': task_project or 'No project'
            })
    
    if recent_tasks:
        print("Recent tasks for context:")
        for i, task in enumerate(recent_tasks, 1):
            print(f"{i}. {task['description']} (Project: {task['project']})")
    else:
        print("No recent tasks found for context")
    
    return True

def cleanup_sample_tasks(task_ids):
    """Clean up the sample tasks"""
    print(f"\n🧹 Cleaning up sample tasks...")
    
    for task_id in task_ids:
        try:
            task = tw.tasks.get(id=task_id)
            task.delete()
            print(f"   🗑️  Deleted task {task_id}")
        except Exception as e:
            print(f"   ⚠️  Could not delete task {task_id}: {e}")

def main():
    """Main demonstration function"""
    print("🎯 Task Formatter Prompt Demonstration")
    print("=" * 50)
    
    # Create sample tasks for context
    sample_ids = create_sample_tasks()
    
    try:
        # Demonstrate the formatter
        demonstrate_task_formatter()
        
        # Show context generation
        show_context_example()
        
        print(f"\n🎉 Task Formatter Features:")
        print("✅ Smart markdown formatting with ## titles")
        print("✅ Structured sections: Details, Acceptance Criteria") 
        print("✅ Context from recent tasks")
        print("✅ Clear examples and guidelines")
        print("✅ Actionable task descriptions")
        
        print(f"\n📋 Usage in Claude Desktop:")
        print("1. Use the 'Task Formatter' prompt")
        print("2. Describe your task briefly") 
        print("3. Claude will rewrite it with proper structure")
        print("4. Copy the formatted version to create task")
        
        return True
        
    finally:
        # Clean up sample tasks
        cleanup_sample_tasks(sample_ids)

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n{'🎊 Demonstration completed successfully!' if success else '❌ Demonstration failed!'}")
    except Exception as e:
        print(f"\n💥 Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)