# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides AI assistants with access to Taskwarrior functionality through the tasklib Python library. The server exposes task management operations, smart prompts, and formatted resources for natural language interaction with Taskwarrior.

## Key Commands

### Running the Server
```bash
# Main server execution
python taskwarrior_mcp_server.py

# Run test suite
python test_final_comprehensive.py  # Comprehensive modular test
python test_modular_server.py       # Basic functionality test

# Install dependencies
pip install -r requirements.txt
# or
pip install tasklib mcp pydantic
```

### Development Commands
```bash
# Check Taskwarrior installation
task --version

# Run automated installation
./install.sh

# Test specific functionality
python test_final_comprehensive.py  # Comprehensive test of all modular components
python test_modular_server.py       # Basic modular server functionality
```

## Architecture & Code Structure

### Modular Architecture

The server uses a **modular architecture** with dynamic loading for maintainability and extensibility:

**Main Server** (`taskwarrior_mcp_server.py`)
- FastMCP-based server with dynamic module loading
- Orchestrates initialization of all components
- Handles MCP protocol communication via stdio

**Modular Components**:
- `tools/` - **19 MCP Tools** for task operations
  - `basic_operations.py` - Core CRUD operations (add, list, get, complete, modify, delete, start, stop, purge)
  - `metadata_operations.py` - Metadata queries (get projects, tags, summary)
  - `batch_operations.py` - Batch processing (bulk complete, delete, modify, start/stop)
- `resources/` - **3 MCP Resources** for formatted data
  - `reports.py` - Daily reports, weekly summaries, live task data
- `prompts/` - **3 MCP Prompts** for AI assistance
  - `planning.py` - Daily planning, task prioritization, task formatting prompts
- `utils/` - **Shared Utilities**
  - `taskwarrior.py` - TaskWarrior connection and task conversion utilities
  - `models.py` - Pydantic parameter validation models
  - `filters.py` - Task filtering utilities for batch operations

### Key Design Patterns

1. **Modular Loading**: Components are dynamically loaded and initialized at runtime
2. **Dependency Injection**: MCP instance is injected into each module during initialization
3. **Tool Registration**: Each operation is registered as an MCP tool with structured parameters
4. **Error Handling**: All operations return structured responses with `success` indicators and error messages
5. **Data Transformation**: Task objects are safely converted to dictionaries using `safe_get_task_field()`
6. **UTC Timezone Handling**: All dates are stored in UTC and converted for display
7. **Resource Formatting**: Resources available in both Markdown (reports) and JSON (data)
8. **Prompt System**: Context-aware prompts analyze current task data

### MCP Protocol Implementation

The server implements:
- **19 Tools**: Complete task management operations including batch processing and maintenance
- **3 Smart Prompts**: Intelligent task planning and analysis
- **3 Resources**: Formatted reports and live task data

Tools use Pydantic models for parameter validation and return structured JSON responses. Resources are identified by URIs (e.g., `taskwarrior://daily-report`) and return formatted content.

### Testing Structure

- `test_final_comprehensive.py`: Comprehensive test of all modular components
- `test_modular_server.py`: Basic modular server functionality test
- Multiple specialized test files for specific features
- All tests can run without requiring actual MCP client connections

## Important Implementation Details

### Date Handling
- Dates are expected in ISO format (e.g., "2024-12-31T23:59:59")
- Server handles timezone conversion automatically
- Task dates are serialized to ISO format in responses

### Task Filtering
- List operations support filtering by status (pending/completed/deleted), project, and tags
- Filters can be combined for complex queries

### Error Recovery
- Server includes comprehensive try/catch blocks for all operations
- Failed operations return structured error messages without crashing
- Taskwarrior connection is validated on initialization

### Integration Points
- Server runs as a standalone Python process
- Communicates via stdio with MCP protocol
- Requires Taskwarrior to be installed and accessible via PATH
- Uses default Taskwarrior configuration unless custom data_location is specified

## Dependencies

- Python 3.8+ (required)
- tasklib>=2.5.1 (Taskwarrior Python interface)
- mcp>=1.0.0 (Model Context Protocol library)
- pydantic>=2.0.0 (Data validation)
- Taskwarrior (must be installed separately)