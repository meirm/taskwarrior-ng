# MCPO Wrapper for TaskWarrior MCP Server

This directory contains a simple wrapper script to run MCPO (Model Context Protocol to OpenAPI) which exposes the TaskWarrior MCP server as a REST API.

## What is MCPO?

MCPO is a proxy that converts MCP (Model Context Protocol) tools into OpenAPI-compliant REST endpoints. It allows the frontend to interact with the MCP server using standard HTTP/REST instead of the MCP protocol.

## Configuration

The wrapper uses two configuration methods:

1. **config.json** - Defines the MCP server to run (static configuration)
2. **Environment Variables** - Runtime configuration for ports, hosts, etc.

## Usage

### Quick Start

```bash
./start-mcpo.sh
```

This will start MCPO with default settings:
- Port: 8085
- Host: 0.0.0.0
- Path Prefix: /api/mcpo/
- API Key: taskwarrior-secret-key
- Config: ./config.json (defines TaskWarrior MCP server)

### Custom Configuration

You can override settings using environment variables:

```bash
MCPO_PORT=8080 \
MCPO_API_KEY="your-secret-key" \
MCPO_PATH_PREFIX="/api/" \
./start-mcpo.sh
```

### Available Environment Variables

- `MCPO_PORT` - The port MCPO will listen on (default: 8085)
- `MCPO_HOST` - The host interface to bind to (default: 0.0.0.0)
- `MCPO_PATH_PREFIX` - URL path prefix for all endpoints (default: /api/mcpo/)
- `MCPO_API_KEY` - API key for authentication (default: taskwarrior-secret-key)

## API Endpoints

Once running, MCPO provides:

- **API Base**: `http://localhost:8085/api/mcpo/taskwarrior/` - All MCP tools as REST endpoints
- **OpenAPI Docs**: `http://localhost:8085/docs` - Interactive API documentation
- **OpenAPI Spec**: `http://localhost:8085/openapi.json` - OpenAPI specification

Note: MCPO appends the server name "taskwarrior" to the path prefix, so endpoints are at `/api/mcpo/taskwarrior/[tool_name]`

## How It Works

1. MCPO starts and launches the TaskWarrior MCP server as a subprocess
2. It establishes communication with the MCP server via stdio
3. MCP tools are automatically exposed as REST endpoints
4. The frontend can call these endpoints using standard HTTP requests with Bearer token authentication

## Requirements

- Python 3.8+
- MCPO installed: `pip install mcpo`
- TaskWarrior MCP server dependencies installed

## Architecture

```
Frontend (React/TypeScript)
         ↓
    HTTP/REST with Bearer Auth
         ↓
MCPO (Port 8085)
         ↓
    MCP Protocol (stdio)
         ↓
TaskWarrior MCP Server
         ↓
TaskWarrior CLI
```

## Notes

- The `--path-prefix` flag must be placed BEFORE the `--` separator in the MCPO command
- MCPO version 0.0.9+ is required for path prefix support
- All requests require Bearer token authentication in the Authorization header
- CORS is configured to allow origins: localhost:3033, localhost:3000, localhost:5173
- The script uses `--hot-reload` for development convenience
- The config.json file defines which MCP server to run (TaskWarrior in this case)