"""
TaskWarrior utilities and connection management
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from tasklib import TaskWarrior, Task

# Configure logging
logger = logging.getLogger("taskwarrior-mcp.utils")

# Initialize TaskWarrior connection
try:
    tw = TaskWarrior()
    logger.info("Connected to Taskwarrior successfully")
except Exception as e:
    logger.error(f"Failed to connect to Taskwarrior: {e}")
    raise

# ============================================================================
# OPTIMIZED PYDANTIC-BASED APPROACH
# ============================================================================

def task_to_model(task: Task) -> 'TaskModel':
    """
    Convert TaskWarrior Task to Pydantic TaskModel.
    
    This replaces all safe_get_task_field() workaround code with a single
    clean conversion to a type-safe Pydantic model.
    """
    from .models import TaskModel
    return TaskModel.from_taskwarrior_task(task)

def task_to_dict(task: Task) -> Dict[str, Any]:
    """
    Convert TaskWarrior Task to dictionary (OPTIMIZED VERSION).
    
    Now uses Pydantic TaskModel internally, eliminating all the 
    manual safe_get() calls and datetime conversion logic.
    """
    task_model = task_to_model(task)
    return task_model.to_utc_dict()

def tasks_to_models(tasks: List[Task]) -> List['TaskModel']:
    """Convert list of TaskWarrior Tasks to list of TaskModels"""
    from .models import TaskModel
    return [TaskModel.from_taskwarrior_task(task) for task in tasks]

# ============================================================================
# MIGRATION COMPLETE - All workaround code has been replaced with TaskModel
# ============================================================================
# All safe_get_task_field() usage has been replaced with TaskModel approach
# The codebase now uses type-safe Pydantic models throughout