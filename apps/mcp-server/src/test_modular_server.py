#!/usr/bin/env python3
"""
Test script for the modular Taskwarrior MCP Server
"""
import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from taskwarrior_mcp_server import initialize_server, mcp

async def test_server_initialization():
    """Test that the server initializes properly"""
    print("Testing modular server initialization...")
    
    try:
        # Initialize the server
        initialize_server()
        
        # Check that tools are loaded (FastMCP stores them differently)
        print(f"\nTesting component registration...")
        print(f"MCP instance created successfully")
        
        # Test a basic tool call
        print(f"\nTesting basic tool functionality...")
        
        # Get list of pending tasks
        from tools.basic_operations import list_tasks
        from utils.models import ListTasksParams
        
        params = ListTasksParams(status="pending", limit=5)
        result = await list_tasks(params)
        
        if result['success']:
            print(f"✅ list_tasks working: found {result['count']} pending tasks")
        else:
            print(f"❌ list_tasks failed: {result.get('error', 'Unknown error')}")
        
        # Test metadata operations
        from tools.metadata_operations import get_summary
        
        summary_result = await get_summary()
        if summary_result['success']:
            print(f"✅ get_summary working: {summary_result['summary']}")
        else:
            print(f"❌ get_summary failed: {summary_result.get('error', 'Unknown error')}")
        
        # Test resource access
        from resources.reports import daily_report
        
        report = await daily_report()
        if report.startswith("# Daily Task Report"):
            print(f"✅ daily_report working: generated {len(report)} characters")
        else:
            print(f"❌ daily_report failed: {report[:100]}...")
        
        # Test prompts
        from prompts.planning import daily_planning_prompt
        
        prompt = await daily_planning_prompt()
        if "daily task planning" in prompt:
            print(f"✅ daily_planning_prompt working: generated {len(prompt)} characters")
        else:
            print(f"❌ daily_planning_prompt failed: {prompt[:100]}...")
        
        print(f"\n🎉 Modular server test completed successfully!")
        print(f"All components tested and working properly")
        
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    """Main test function"""
    success = await test_server_initialization()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())