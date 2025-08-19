#!/usr/bin/env python3
"""
Script to remove @mcp.tool(), @mcp.resource(), and @mcp.prompt() decorators
"""
import re
from pathlib import Path

def fix_file(file_path: Path):
    """Remove MCP decorators from a file"""
    print(f"Fixing {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove @mcp.tool() decorators
    content = re.sub(r'@mcp\.tool\(\)\n', '', content)
    
    # Remove @mcp.resource() decorators
    content = re.sub(r'@mcp\.resource\([^)]+\)\n', '', content)
    
    # Remove @mcp.prompt() decorators
    content = re.sub(r'@mcp\.prompt\([^)]+\)\n', '', content)
    
    with open(file_path, 'w') as f:
        f.write(content)

def main():
    """Fix all Python files in the project"""
    src_dir = Path(__file__).parent
    
    # Fix all Python files in tools, resources, and prompts directories
    for pattern in ['tools/*.py', 'resources/*.py', 'prompts/*.py']:
        for file_path in src_dir.glob(pattern):
            if file_path.name != '__init__.py':
                fix_file(file_path)
    
    print("All decorators removed!")

if __name__ == "__main__":
    main()