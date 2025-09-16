#!/usr/bin/env python3
"""
Modular Taskwarrior MCP Server
A Model Context Protocol server that provides AI assistants with access to Taskwarrior functionality.
"""
import asyncio
import importlib
import logging
import sys
from pathlib import Path

from fastmcp import FastMCP

# Add the utils directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))
from utils.fastmcp_wrapper import make_mcp_json_compatible

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taskwarrior-mcp.server")

# Create MCP server instance with JSON compatibility
mcp_base = FastMCP("Taskwarrior MCP Server")
mcp = make_mcp_json_compatible(mcp_base)

def load_module_tools(module_path: str, mcp_instance: FastMCP):
    """Dynamically load tools from a module"""
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'init_tools'):
            module.init_tools(mcp_instance)
            logger.info(f"Loaded tools from {module_path}")
        else:
            logger.warning(f"Module {module_path} has no init_tools function")
    except ImportError as e:
        logger.error(f"Failed to import {module_path}: {e}")
    except Exception as e:
        logger.error(f"Error loading tools from {module_path}: {e}")

def load_module_resources(module_path: str, mcp_instance: FastMCP):
    """Dynamically load resources from a module"""
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'init_resources'):
            module.init_resources(mcp_instance)
            logger.info(f"Loaded resources from {module_path}")
        else:
            logger.warning(f"Module {module_path} has no init_resources function")
    except ImportError as e:
        logger.error(f"Failed to import {module_path}: {e}")
    except Exception as e:
        logger.error(f"Error loading resources from {module_path}: {e}")

def load_module_prompts(module_path: str, mcp_instance: FastMCP):
    """Dynamically load prompts from a module"""
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'init_prompts'):
            module.init_prompts(mcp_instance)
            logger.info(f"Loaded prompts from {module_path}")
        else:
            logger.warning(f"Module {module_path} has no init_prompts function")
    except ImportError as e:
        logger.error(f"Failed to import {module_path}: {e}")
    except Exception as e:
        logger.error(f"Error loading prompts from {module_path}: {e}")

def initialize_server():
    """Initialize the MCP server with all modules"""
    logger.info("Initializing Taskwarrior MCP Server...")
    
    # Load tool modules
    logger.info("Loading tool modules...")
    tool_modules = [
        "tools.basic_operations",
        "tools.metadata_operations", 
        "tools.batch_operations"
    ]
    
    for module_name in tool_modules:
        load_module_tools(module_name, mcp)
    
    # Load resource modules
    logger.info("Loading resource modules...")
    resource_modules = [
        "resources.reports"
    ]
    
    for module_name in resource_modules:
        load_module_resources(module_name, mcp)
    
    # Load prompt modules
    logger.info("Loading prompt modules...")
    prompt_modules = [
        "prompts.planning"
    ]
    
    for module_name in prompt_modules:
        load_module_prompts(module_name, mcp)
    
    logger.info("Server initialization complete")

async def main():
    """Main server entry point"""
    # Add the src directory to Python path for relative imports
    src_path = Path(__file__).parent
    sys.path.insert(0, str(src_path))
    
    try:
        # Initialize server with all modules
        initialize_server()
        
        # Start the server
        logger.info("Starting Taskwarrior MCP Server...")
        await mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

def run_server():
    """Run the server with proper event loop handling"""
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we get here, we're already in an event loop
            logger.info("Running in existing event loop")
            # Use create_task instead of run
            task = asyncio.create_task(main())
            return task
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            logger.info("No existing event loop, creating new one")
            asyncio.run(main())
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Add the src directory to Python path for imports
    src_path = Path(__file__).parent
    sys.path.insert(0, str(src_path))
    
    # Initialize server with all modules
    initialize_server()
    
    # Use FastMCP's run method directly which handles asyncio better
    mcp.run(transport="stdio")