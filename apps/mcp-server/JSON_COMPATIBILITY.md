# JSON Compatibility for MCP Server

## Overview

The TaskWarrior MCP server now includes automatic JSON to Pydantic model conversion, enabling compatibility with MCP clients (like Claude) that send JSON instead of Pydantic model instances.

## How It Works

### 1. FastMCP Wrapper (`utils/fastmcp_wrapper.py`)

The wrapper intercepts all tool registrations and adds automatic JSON to Pydantic conversion:

```python
from fastmcp import FastMCP
from utils.fastmcp_wrapper import make_mcp_json_compatible

# Create server with JSON compatibility
mcp_base = FastMCP("Taskwarrior MCP Server")
mcp = make_mcp_json_compatible(mcp_base)
```

### 2. Automatic Conversion

When a tool function is called, the wrapper:

1. **Detects JSON input**: Checks if the input is a dictionary instead of a Pydantic model
2. **Handles MCP protocol**: Extracts parameters from `{"arguments": {...}}` format
3. **Converts to Pydantic**: Creates the appropriate Pydantic model from the JSON
4. **Filters extra fields**: Removes any fields not defined in the model
5. **Validates data**: Ensures the data meets Pydantic validation rules

### 3. Supported Input Formats

The server now accepts multiple input formats:

#### Direct JSON
```json
{
  "description": "Task description",
  "project": "ProjectName",
  "priority": "H"
}
```

#### MCP Protocol Wrapper
```json
{
  "arguments": {
    "description": "Task description",
    "project": "ProjectName",
    "priority": "H"
  }
}
```

#### Pydantic Models (Original)
```python
AddTaskParams(
    description="Task description",
    project="ProjectName",
    priority="H"
)
```

## Benefits

1. **Claude Compatibility**: Claude MCP client can now use the server without modifications
2. **Backward Compatible**: Existing Pydantic-based tools still work
3. **Automatic Validation**: JSON inputs are validated through Pydantic models
4. **Error Handling**: Invalid fields are filtered out automatically
5. **Logging**: Conversion process is logged for debugging

## Testing

Two test scripts are provided:

1. **`test_wrapper_decorator.py`**: Tests the wrapper decorator directly
2. **`test_json_compatibility.py`**: Tests end-to-end JSON handling

Run tests with:
```bash
cd apps/mcp-server
source venv/bin/activate
python src/test_wrapper_decorator.py
```

## Supported Tools

All MCP tools automatically support JSON input:

- `add_task` - Add new tasks
- `list_tasks` - List tasks with filters
- `get_task` - Get task details
- `complete_task` - Mark tasks as complete
- `modify_task` - Modify existing tasks
- `delete_task` - Delete tasks
- `batch_*` - All batch operations
- And all other registered tools

## Error Handling

If JSON conversion fails, the wrapper:

1. Logs the error with details
2. Attempts to filter extra fields and retry
3. Provides clear error messages for debugging
4. Falls back to original error if conversion is impossible

## Usage with Claude

When Claude connects as an MCP client, it can now send standard JSON:

```json
{
  "tool": "add_task",
  "arguments": {
    "description": "Review pull request",
    "project": "Development",
    "priority": "H",
    "tags": ["code-review", "urgent"]
  }
}
```

The server automatically converts this to the expected Pydantic model and processes the request.

## Implementation Details

The wrapper:
- Uses Python's `inspect` module to analyze function signatures
- Leverages `get_type_hints()` to identify Pydantic model parameters
- Applies the `convert_json_to_pydantic` decorator to all tool functions
- Maintains full compatibility with FastMCP's existing functionality

## Troubleshooting

### Conversion Errors
Check logs for messages like:
- `"Converting JSON to {ModelName}"`
- `"Failed to convert JSON to {ModelName}: {error}"`
- `"Successfully converted with filtered fields"`

### Common Issues
1. **Extra fields**: Automatically filtered out
2. **Missing required fields**: Will raise validation error
3. **Type mismatches**: Pydantic validation will catch these
4. **MCP wrapper format**: Automatically detected and handled