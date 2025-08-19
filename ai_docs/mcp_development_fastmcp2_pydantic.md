# MCP Development with FastMCP 2.0 and Pydantic (2025 Guide)

**Comprehensive guide for building Model Context Protocol servers using FastMCP 2.0 and Pydantic in 2025**

## Overview

FastMCP 2.0 is the actively maintained framework for building MCP servers that was incorporated into the official MCP Python SDK. This guide provides best practices for using FastMCP with Pydantic for robust parameter validation and structured data handling.

## FastMCP 2.0 Key Features (2025)

### Core Features
- **Structured Content Support** (6/18/2025 MCP spec update)
- **Automatic Schema Generation** from type hints and Pydantic models
- **Type Coercion** with automatic conversion when possible
- **Comprehensive Type Support** - all Pydantic-supported types
- **Built-in Validation** with detailed error reporting

### Architecture Benefits
- **Modular Design**: Support for dynamic module loading
- **Production Ready**: Comprehensive error handling and logging
- **Event Loop Management**: Handles asyncio conflicts automatically
- **Performance Optimized**: Efficient tool registration and execution

## Basic Server Setup

```python
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Optional

# Create MCP server instance
mcp = FastMCP("Your Server Name")

# Server initialization and startup
if __name__ == "__main__":
    # Use FastMCP's built-in event loop handling (avoids asyncio conflicts)
    mcp.run(transport="stdio")
```

## Pydantic Model Best Practices

### 1. Parameter Models with Field Descriptions

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class AddTaskParams(BaseModel):
    """Parameters for adding a new task"""
    description: str = Field(..., description="Task description")
    project: Optional[str] = Field(None, description="Project name")
    priority: Optional[str] = Field(None, description="Priority: H (High), M (Medium), L (Low)")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    due: Optional[str] = Field(None, description="Due date in ISO format (UTC)")

class TaskIdParam(BaseModel):
    """Parameter for operations requiring a task ID"""
    task_id: int = Field(..., description="Task ID")
```

### 2. Advanced Field Constraints

```python
from typing import Annotated
from pydantic import BaseModel, Field

class ValidationExample(BaseModel):
    # Range constraints
    count: int = Field(ge=0, le=100, description="Count between 0-100")
    ratio: float = Field(gt=0, lt=1.0, description="Ratio between 0-1")
    
    # String constraints
    user_id: str = Field(
        pattern=r"^[A-Z]{2}\d{4}$",
        description="User ID in format XX0000"
    )
    comment: str = Field(
        min_length=3, 
        max_length=500, 
        description="Comment text"
    )
    
    # Multiple constraints
    factor: int = Field(multiple_of=5, ge=10, description="Factor (multiple of 5, min 10)")
```

### 3. Complex Nested Models

```python
class BatchFilterParams(BaseModel):
    """Complex filtering parameters for batch operations"""
    status: Optional[str] = Field(None, description="Filter by status")
    project: Optional[str] = Field(None, description="Filter by project name")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (ANY match)")
    priority: Optional[str] = Field(None, description="Filter by priority")
    description_contains: Optional[str] = Field(None, description="Filter by description text")
    due_before: Optional[str] = Field(None, description="Filter by due date before")
    due_after: Optional[str] = Field(None, description="Filter by due date after")
    limit: Optional[int] = Field(None, description="Maximum results")

class BatchModifyParams(BaseModel):
    """Parameters for batch modification operations"""
    # Either specific IDs or filter criteria
    task_ids: Optional[List[int]] = Field(None, description="Specific task IDs")
    filters: Optional[BatchFilterParams] = Field(None, description="Filter criteria")
    
    # Modification fields
    project: Optional[str] = Field(None, description="Set project for all tasks")
    priority: Optional[str] = Field(None, description="Set priority for all tasks")
    add_tags: Optional[List[str]] = Field(None, description="Tags to add")
    remove_tags: Optional[List[str]] = Field(None, description="Tags to remove")
```

## Tool Registration Patterns

### 1. Modular Tool Registration (Recommended)

```python
# In module file (e.g., tools/basic_operations.py)
from fastmcp import FastMCP
from typing import Dict, Any

# Global variable for MCP instance injection
mcp: FastMCP = None

def init_tools(mcp_instance: FastMCP):
    """Initialize tools with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register all tools with the MCP instance
    mcp.tool()(add_task)
    mcp.tool()(list_tasks)
    mcp.tool()(get_task)
    mcp.tool()(complete_task)
    # ... register all functions

# Tool functions (no decorators at definition time)
async def add_task(params: AddTaskParams) -> Dict[str, Any]:
    """Add a new task"""
    try:
        # Implementation here
        return {
            'success': True,
            'task': result_data,
            'message': 'Task created successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

### 2. Dynamic Module Loading

```python
# In main server file
import importlib
from pathlib import Path

def load_module_tools(module_path: str, mcp_instance: FastMCP):
    """Dynamically load tools from a module"""
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'init_tools'):
            module.init_tools(mcp_instance)
            logger.info(f"Loaded tools from {module_path}")
        else:
            logger.warning(f"Module {module_path} has no init_tools function")
    except Exception as e:
        logger.error(f"Error loading tools from {module_path}: {e}")

def initialize_server():
    """Initialize server with all modules"""
    tool_modules = [
        "tools.basic_operations",
        "tools.metadata_operations", 
        "tools.batch_operations"
    ]
    
    for module_name in tool_modules:
        load_module_tools(module_name, mcp)
```

## Response Format Standards

### 1. Structured Response Pattern

```python
# Success response
{
    'success': True,
    'data': result_object,  # The actual result
    'message': 'Operation completed successfully',
    'metadata': {  # Optional additional info
        'count': 5,
        'execution_time': '0.125s'
    }
}

# Error response
{
    'success': False,
    'error': 'Detailed error message',
    'error_code': 'VALIDATION_ERROR',  # Optional error categorization
    'details': {  # Optional additional context
        'field': 'task_id',
        'value': 'invalid_id'
    }
}
```

### 2. Structured Content Support (2025)

FastMCP 2.0 automatically creates structured outputs for object-like results:

```python
from pydantic import BaseModel

class TaskResult(BaseModel):
    """Structured task result"""
    id: int
    description: str
    status: str
    project: Optional[str]
    tags: List[str]

@mcp.tool()
async def get_task(params: TaskIdParam) -> TaskResult:
    """Get task - returns structured content automatically"""
    # FastMCP automatically creates structured JSON alongside text content
    return TaskResult(
        id=params.task_id,
        description="Sample task",
        status="pending",
        project=None,
        tags=["example"]
    )
```

## Resource and Prompt Patterns

### 1. Resource Registration

```python
# In resources module
def init_resources(mcp_instance: FastMCP):
    """Initialize resources with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register resources with URIs
    mcp.resource("taskwarrior://daily-report")(daily_report)
    mcp.resource("taskwarrior://weekly-summary")(weekly_summary)
    mcp.resource("taskwarrior://live-tasks")(live_tasks)

async def daily_report() -> str:
    """Generate daily task report in Markdown format"""
    # Return formatted markdown content
    return report_content
```

### 2. Prompt Registration

```python
# In prompts module
def init_prompts(mcp_instance: FastMCP):
    """Initialize prompts with MCP instance"""
    global mcp
    mcp = mcp_instance
    
    # Register prompts with names
    mcp.prompt("daily-planning")(daily_planning_prompt)
    mcp.prompt("task-prioritization")(task_prioritization_prompt)

async def daily_planning_prompt() -> str:
    """Generate context-aware planning prompt"""
    # Analyze current task state and generate helpful prompt
    return context_aware_prompt
```

## Error Handling Best Practices

### 1. Comprehensive Try-Catch Blocks

```python
async def tool_function(params: ParamsModel) -> Dict[str, Any]:
    """Tool with comprehensive error handling"""
    try:
        # Validate business logic
        if not params.required_field:
            return {
                'success': False,
                'error': 'Required field missing',
                'error_code': 'VALIDATION_ERROR'
            }
        
        # Perform operation
        result = await perform_operation(params)
        
        return {
            'success': True,
            'data': result,
            'message': 'Operation completed successfully'
        }
        
    except ValidationError as e:
        logger.error(f"Validation error in {tool_function.__name__}: {e}")
        return {
            'success': False,
            'error': f'Validation failed: {str(e)}',
            'error_code': 'VALIDATION_ERROR'
        }
    except TimeoutError:
        logger.error(f"Timeout in {tool_function.__name__}")
        return {
            'success': False,
            'error': 'Operation timed out',
            'error_code': 'TIMEOUT_ERROR'
        }
    except Exception as e:
        logger.error(f"Unexpected error in {tool_function.__name__}: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }
```

### 2. Type Safety with Safe Field Access

```python
from tasklib import Task

def safe_get_task_field(task: Task, field: str):
    """Safely get a field from a Task object"""
    try:
        return task[field]
    except KeyError:
        return None

def task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert Task to dictionary with safe field access"""
    return {
        'id': safe_get_task_field(task, 'id'),
        'description': safe_get_task_field(task, 'description') or '',
        'status': safe_get_task_field(task, 'status') or 'pending',
        'project': safe_get_task_field(task, 'project'),
        # ... other fields with safe access
    }
```

## Testing Strategies

### 1. Comprehensive Module Testing

```python
import asyncio
from pathlib import Path

async def test_modular_server():
    """Test modular server initialization and functionality"""
    # Initialize server
    initialize_server()
    
    # Import modules after initialization
    from tools.basic_operations import add_task, list_tasks
    from utils.models import AddTaskParams, ListTasksParams
    
    # Test basic functionality
    add_result = await add_task(AddTaskParams(description="Test task"))
    assert add_result['success'], f"Add failed: {add_result.get('error')}"
    
    list_result = await list_tasks(ListTasksParams(status="pending"))
    assert list_result['success'], f"List failed: {list_result.get('error')}"
    
    print("✅ All tests passed!")
```

### 2. Integration Testing

```python
async def test_comprehensive_functionality():
    """Test all server components together"""
    test_results = {
        'tools': 0, 'resources': 0, 'prompts': 0,
        'passed': 0, 'failed': 0
    }
    
    # Test tools
    for tool_func in [add_task, list_tasks, complete_task]:
        try:
            result = await tool_func(test_params)
            if result.get('success'):
                test_results['tools'] += 1
                test_results['passed'] += 1
        except Exception as e:
            test_results['failed'] += 1
    
    # Test resources and prompts similarly
    # Report comprehensive results
    success_rate = test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100
    print(f"Success rate: {success_rate:.1f}%")
```

## Production Deployment Considerations

### 1. Event Loop Management

```python
# Correct approach for production (handles asyncio conflicts)
if __name__ == "__main__":
    # Add path for imports
    src_path = Path(__file__).parent
    sys.path.insert(0, str(src_path))
    
    # Initialize server with all modules
    initialize_server()
    
    # Use FastMCP's run method (handles event loop properly)
    mcp.run(transport="stdio")
```

### 2. Configuration Management

```python
# Configuration structure
{
    "server_info": {
        "name": "your-mcp-server",
        "version": "1.0.0",
        "mcp_version": "1.13.0",
        "fastmcp_version": "2.11.3"
    },
    "features": {
        "tools": 19,
        "resources": 3,
        "prompts": 3,
        "capabilities": [
            "data_validation",
            "structured_content",
            "batch_operations",
            "error_handling"
        ]
    }
}
```

## Performance Optimization

### 1. Efficient Data Handling

```python
# Use generators for large datasets
def filter_large_dataset(data, filters):
    """Generator-based filtering for memory efficiency"""
    for item in data:
        if matches_filters(item, filters):
            yield item

# Batch operations for efficiency
async def batch_operation(items: List[Any]) -> Dict[str, Any]:
    """Process items in batches for better performance"""
    results = []
    errors = []
    
    for item in items:
        try:
            result = await process_item(item)
            results.append(result)
        except Exception as e:
            errors.append(f"Item {item}: {str(e)}")
    
    return {
        'success': len(errors) == 0,
        'results': results,
        'errors': errors
    }
```

### 2. Caching and Memoization

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache expensive operations
@lru_cache(maxsize=128)
def expensive_calculation(param: str) -> str:
    """Cache expensive calculations"""
    # Expensive operation here
    return result

# Time-based caching for dynamic data
_cache = {}
_cache_timeout = {}

def get_with_cache(key: str, ttl_seconds: int = 300):
    """Get data with time-based cache"""
    now = datetime.now()
    
    if (key in _cache and 
        key in _cache_timeout and 
        _cache_timeout[key] > now):
        return _cache[key]
    
    # Fetch fresh data
    data = fetch_fresh_data(key)
    _cache[key] = data
    _cache_timeout[key] = now + timedelta(seconds=ttl_seconds)
    
    return data
```

## Summary

FastMCP 2.0 with Pydantic provides a robust, type-safe foundation for building MCP servers in 2025. Key benefits:

- **Type Safety**: Comprehensive validation with Pydantic models
- **Structured Content**: Automatic JSON schema generation and validation
- **Modular Architecture**: Dynamic loading and clean separation of concerns
- **Production Ready**: Built-in error handling, logging, and event loop management
- **Performance**: Efficient data handling and caching strategies

This combination enables building maintainable, scalable MCP servers that integrate seamlessly with modern AI systems and provide excellent developer experience.