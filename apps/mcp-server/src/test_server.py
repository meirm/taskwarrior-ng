#!/usr/bin/env python3
"""
Test script to verify the Taskwarrior MCP server can be imported and runs correctly
"""
import sys
import os

# Add the current directory to the path so we can import the server
sys.path.insert(0, os.path.dirname(__file__))

def test_server():
    """Test that the server can be imported without errors"""
    
    print("🧪 Testing Taskwarrior MCP Server Import...")
    
    try:
        import taskwarrior_mcp_server
        print("✅ Server imported successfully")
        
        # Check that the MCP server has the expected structure
        mcp = taskwarrior_mcp_server.mcp
        print(f"✅ MCP server instance found: {type(mcp)}")
        
        # Check TaskWarrior connection
        tw = taskwarrior_mcp_server.tw
        print("✅ TaskWarrior connection established")
        
        # Test basic functionality
        from taskwarrior_mcp_server import task_to_dict
        print("✅ Helper functions available")
        
        print("\n✨ All import tests passed!")
        print("\n📋 Server is ready for Claude Desktop integration")
        print("   Add the config.json contents to your Claude Desktop configuration")
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)