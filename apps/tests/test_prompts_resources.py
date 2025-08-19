#!/usr/bin/env python3
"""
Test Prompts and Resources for Taskwarrior MCP Server

This script demonstrates the prompts and resources functionality
of the Taskwarrior MCP server.
"""

import asyncio
import json
import sys
from typing import Dict, Any

class TaskwarriorPromptResourceTest:
    """Test client for Taskwarrior MCP prompts and resources"""
    
    def __init__(self):
        pass
    
    async def test_prompts(self):
        """Test all available prompts"""
        print("\n=== Testing: Prompts ===")
        
        # Import the server module
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server', 'src'))
        from taskwarrior_mcp_server import tw_mcp
        
        # Test daily planning prompt
        print("\n--- Daily Planning Prompt ---")
        try:
            daily_report = await tw_mcp.get_daily_report()
            print("Daily report preview:")
            print(daily_report[:500] + "..." if len(daily_report) > 500 else daily_report)
        except Exception as e:
            print(f"Error: {e}")
        
        # Test weekly summary
        print("\n--- Weekly Summary ---")
        try:
            weekly_summary = await tw_mcp.get_weekly_summary()
            print("Weekly summary preview:")
            print(weekly_summary[:500] + "..." if len(weekly_summary) > 500 else weekly_summary)
        except Exception as e:
            print(f"Error: {e}")
    
    async def test_resources(self):
        """Test all available resources"""
        print("\n=== Testing: Resources ===")
        
        # Import the server module
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server', 'src'))
        from taskwarrior_mcp_server import tw_mcp
        
        resources = [
            ("taskwarrior://daily-report", "Daily Report"),
            ("taskwarrior://weekly-summary", "Weekly Summary"),
            ("taskwarrior://task-summary", "Task Summary"),
            ("taskwarrior://pending-tasks", "Pending Tasks"),
            ("taskwarrior://overdue-tasks", "Overdue Tasks"),
            ("taskwarrior://projects", "Projects"),
            ("taskwarrior://tags", "Tags")
        ]
        
        for uri, name in resources:
            print(f"\n--- {name} ---")
            try:
                if uri == "taskwarrior://daily-report":
                    content = await tw_mcp.get_daily_report()
                elif uri == "taskwarrior://weekly-summary":
                    content = await tw_mcp.get_weekly_summary()
                elif uri == "taskwarrior://task-summary":
                    summary = await tw_mcp.get_summary()
                    content = json.dumps(summary, indent=2)
                elif uri == "taskwarrior://pending-tasks":
                    tasks = await tw_mcp.list_tasks(status="pending", limit=5)
                    content = json.dumps(tasks, indent=2)
                elif uri == "taskwarrior://overdue-tasks":
                    # Get overdue tasks by filtering
                    from datetime import datetime
                    pending_tasks = await tw_mcp.list_tasks(status="pending", limit=100)
                    if pending_tasks.get("success") and pending_tasks.get("tasks"):
                        now = datetime.now()
                        overdue_tasks = [
                            task for task in pending_tasks["tasks"] 
                            if task.get("due") and datetime.fromisoformat(task["due"].replace('Z', '+00:00')) < now
                        ]
                        result = {
                            "success": True,
                            "tasks": overdue_tasks,
                            "count": len(overdue_tasks),
                            "message": f"Found {len(overdue_tasks)} overdue tasks"
                        }
                    else:
                        result = {"success": False, "tasks": [], "count": 0, "message": "Failed to get overdue tasks"}
                    content = json.dumps(result, indent=2)
                elif uri == "taskwarrior://projects":
                    projects = await tw_mcp.get_projects()
                    content = json.dumps(projects, indent=2)
                elif uri == "taskwarrior://tags":
                    tags = await tw_mcp.get_tags()
                    content = json.dumps(tags, indent=2)
                else:
                    content = f"Unknown resource: {uri}"
                
                # Show preview of content
                if len(content) > 500:
                    print(f"Preview (first 500 chars):\n{content[:500]}...")
                    print(f"\nTotal length: {len(content)} characters")
                else:
                    print(f"Content:\n{content}")
                    
            except Exception as e:
                print(f"Error accessing {name}: {e}")
    
    async def test_project_report(self):
        """Test project-specific reporting"""
        print("\n=== Testing: Project Reports ===")
        
        # Import the server module
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server', 'src'))
        from taskwarrior_mcp_server import tw_mcp
        
        # Get list of projects first
        projects_data = await tw_mcp.get_projects()
        if projects_data.get("success") and projects_data.get("projects"):
            # Test with the first project
            project_name = projects_data["projects"][0]
            print(f"\n--- Project Report: {project_name} ---")
            
            try:
                project_report = await tw_mcp.get_project_report(project_name)
                print("Project report preview:")
                print(project_report[:500] + "..." if len(project_report) > 500 else project_report)
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("No projects found to generate reports for.")
    
    async def test_prompt_scenarios(self):
        """Test different prompt scenarios"""
        print("\n=== Testing: Prompt Scenarios ===")
        
        # Import the server module
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server', 'src'))
        from taskwarrior_mcp_server import tw_mcp
        
        scenarios = [
            {
                "name": "Daily Planning with Focus",
                "description": "Test daily planning prompt with a focus area",
                "focus_area": "work"
            },
            {
                "name": "Task Review Weekly",
                "description": "Test task review for weekly period",
                "time_period": "weekly"
            },
            {
                "name": "General Productivity Analysis",
                "description": "Test overall productivity analysis",
                "project": None
            }
        ]
        
        for scenario in scenarios:
            print(f"\n--- {scenario['name']} ---")
            print(f"Description: {scenario['description']}")
            
            try:
                if scenario['name'].startswith("Daily Planning"):
                    # Test daily planning logic
                    daily_report = await tw_mcp.get_daily_report()
                    print(f"Would generate daily planning prompt with focus on '{scenario['focus_area']}'")
                    print(f"Daily report available: {len(daily_report)} characters")
                    
                elif scenario['name'].startswith("Task Review"):
                    # Test task review logic
                    if scenario['time_period'] == 'weekly':
                        weekly_summary = await tw_mcp.get_weekly_summary()
                        print(f"Would generate weekly task review prompt")
                        print(f"Weekly summary available: {len(weekly_summary)} characters")
                    
                elif scenario['name'].startswith("General Productivity"):
                    # Test productivity analysis logic
                    summary = await tw_mcp.get_summary()
                    daily_report = await tw_mcp.get_daily_report()
                    print(f"Would generate general productivity analysis prompt")
                    print(f"Summary and reports available for analysis")
                    
            except Exception as e:
                print(f"Error in scenario: {e}")
    
    async def run_all_tests(self):
        """Run all test functions"""
        print("Starting Taskwarrior MCP Prompts and Resources Tests")
        print("===================================================")
        
        try:
            await self.test_resources()
            await self.test_prompts()
            await self.test_project_report()
            await self.test_prompt_scenarios()
            
            print("\n=== All Prompt and Resource Tests Completed ===")
            
        except Exception as e:
            print(f"\nTest failed with error: {e}")
            sys.exit(1)

async def main():
    """Main function to run tests"""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python test_prompts_resources.py")
        print("Tests the Taskwarrior MCP server prompts and resources functionality")
        print("\nMake sure you have:")
        print("1. Taskwarrior installed and configured")
        print("2. tasklib Python library installed")
        print("3. The taskwarrior_mcp_server.py file in the same directory")
        return
    
    # Check if tasklib is available
    try:
        import tasklib
        print("✓ tasklib is available")
    except ImportError:
        print("✗ tasklib is not available. Please install it: pip install tasklib")
        sys.exit(1)
    
    # Run the tests
    test_client = TaskwarriorPromptResourceTest()
    await test_client.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
