"""
FastMCP wrapper that automatically handles JSON to Pydantic conversion
This ensures compatibility between MCP clients sending JSON and server functions expecting Pydantic models.
"""
import functools
import inspect
import logging
from typing import Any, Callable, Dict, Union, get_type_hints, get_origin, get_args
from pydantic import BaseModel

logger = logging.getLogger("taskwarrior-mcp.wrapper")

def convert_json_to_pydantic(func: Callable) -> Callable:
    """
    Decorator that automatically converts JSON arguments to Pydantic models.

    This decorator inspects function signatures and converts dictionary arguments
    to the appropriate Pydantic model types when needed.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        param_names = list(sig.parameters.keys())

        # Process arguments
        new_args = list(args)

        # Handle the first positional argument (typically 'params' in MCP tools)
        if new_args and param_names:
            first_param_name = param_names[0]

            if first_param_name in type_hints:
                param_type = type_hints[first_param_name]
                first_arg = new_args[0]

                # Check if the parameter type includes a Pydantic model
                # Handle Union types (e.g., Union[PydanticModel, Dict, None])
                if get_origin(param_type) is Union:
                    # Get all types in the Union
                    union_types = get_args(param_type)
                    # Find the Pydantic model type if present
                    pydantic_type = None
                    for t in union_types:
                        if inspect.isclass(t) and issubclass(t, BaseModel):
                            pydantic_type = t
                            break

                    if pydantic_type and isinstance(first_arg, dict):
                        # Convert dict to Pydantic model
                        param_type = pydantic_type
                elif inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                    # Direct Pydantic model type
                    pass
                else:
                    # Not a Pydantic model, skip conversion
                    return await func(*new_args, **kwargs)

                # Convert if we have a dict and expect a Pydantic model
                if (inspect.isclass(param_type) and
                    issubclass(param_type, BaseModel) and
                    isinstance(first_arg, dict)):

                    try:
                        # Handle MCP protocol wrapper format
                        if 'arguments' in first_arg and isinstance(first_arg['arguments'], dict):
                            logger.debug(f"Extracting arguments from MCP wrapper")
                            first_arg = first_arg['arguments']

                        # Convert to Pydantic model
                        logger.debug(f"Converting JSON to {param_type.__name__}")
                        converted = param_type(**first_arg)
                        new_args[0] = converted

                    except Exception as e:
                        logger.error(f"Failed to convert JSON to {param_type.__name__}: {e}")
                        logger.debug(f"Input data: {first_arg}")

                        # Try with filtered fields (only those defined in the model)
                        try:
                            if hasattr(param_type, '__fields__'):
                                model_fields = param_type.__fields__.keys()
                                filtered_data = {k: v for k, v in first_arg.items() if k in model_fields}
                                logger.debug(f"Retrying with filtered fields: {list(filtered_data.keys())}")
                                converted = param_type(**filtered_data)
                                new_args[0] = converted
                                logger.info(f"Successfully converted with filtered fields")
                            else:
                                raise e
                        except Exception as e2:
                            logger.error(f"Failed even with filtered fields: {e2}")
                            raise

        # Call the original function with converted arguments
        return await func(*new_args, **kwargs)

    return wrapper

class JsonCompatibleFastMCP:
    """
    Wrapper around FastMCP that automatically adds JSON to Pydantic conversion
    to all registered tools.
    """

    def __init__(self, mcp_instance):
        """
        Initialize the wrapper with an existing FastMCP instance.

        Args:
            mcp_instance: The FastMCP instance to wrap
        """
        self.mcp = mcp_instance
        self._original_tool = mcp_instance.tool

        # Replace the tool decorator
        self._setup_json_compatible_tool()

    def _setup_json_compatible_tool(self):
        """Replace the tool decorator with our JSON-compatible version."""
        def json_compatible_tool(*tool_args, **tool_kwargs):
            """Tool decorator that adds JSON to Pydantic conversion."""
            def decorator(func: Callable) -> Callable:
                # First apply our conversion decorator
                converted_func = convert_json_to_pydantic(func)
                # Then apply the original tool decorator
                return self._original_tool(*tool_args, **tool_kwargs)(converted_func)
            return decorator

        # Replace the tool method
        self.mcp.tool = json_compatible_tool

    def __getattr__(self, name):
        """Proxy all other attributes to the wrapped MCP instance."""
        return getattr(self.mcp, name)

    def run(self, *args, **kwargs):
        """Proxy the run method to the wrapped MCP instance."""
        return self.mcp.run(*args, **kwargs)

def make_mcp_json_compatible(mcp_instance) -> Any:
    """
    Make a FastMCP instance compatible with JSON input from MCP clients.

    This function wraps the FastMCP instance to automatically convert JSON
    dictionaries to Pydantic models for all tool functions.

    Args:
        mcp_instance: The FastMCP instance to make JSON-compatible

    Returns:
        The wrapped MCP instance with JSON compatibility
    """
    logger.info("Enabling JSON compatibility for FastMCP server")
    wrapper = JsonCompatibleFastMCP(mcp_instance)

    # Return the wrapper's mcp instance which now has the modified tool decorator
    # but we need to return the wrapper itself to maintain the proxy
    return wrapper