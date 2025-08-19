"""
Pydantic models for MCP parameter validation and TaskWarrior data handling
"""
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator

# Individual task operation models
class AddTaskParams(BaseModel):
    description: str = Field(..., description="Task description")
    project: Optional[str] = Field(None, description="Project name")
    priority: Optional[str] = Field(None, description="Priority: H (High), M (Medium), L (Low)")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    due: Optional[str] = Field(None, description="Due date in ISO format (UTC), e.g., '2025-08-22T18:00:00Z'")

class ListTasksParams(BaseModel):
    status: str = Field("pending", description="Task status filter: pending, completed, deleted")
    project: Optional[str] = Field(None, description="Filter by project name")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: Optional[int] = Field(None, description="Maximum number of tasks to return")

class TaskIdParam(BaseModel):
    task_id: Optional[int] = Field(None, description="Task ID")
    uuid: Optional[str] = Field(None, description="Task UUID")
    
    @model_validator(mode='after')
    def validate_identifier(self):
        """Ensure at least one identifier is provided"""
        if not self.task_id and not self.uuid:
            raise ValueError("Either task_id or uuid must be provided")
        return self

class ModifyTaskParams(BaseModel):
    task_id: int = Field(..., description="Task ID to modify")
    description: Optional[str] = Field(None, description="New task description")
    project: Optional[str] = Field(None, description="New project name")
    priority: Optional[str] = Field(None, description="New priority (H/M/L)")
    tags: Optional[List[str]] = Field(None, description="New list of tags")
    due: Optional[str] = Field(None, description="New due date in ISO format (UTC), e.g., '2025-08-22T18:00:00Z'")

class RestoreTaskParams(BaseModel):
    task_id: Optional[int] = Field(None, description="ID of the deleted task to restore (may not exist for deleted tasks)")
    uuid: Optional[str] = Field(None, description="UUID of the deleted task to restore")
    status: Optional[str] = Field("pending", description="Status to set for restored task (default: pending)")
    
    @model_validator(mode='after')
    def validate_identifier(self):
        """Ensure at least one identifier is provided"""
        if not self.task_id and not self.uuid:
            raise ValueError("Either task_id or uuid must be provided")
        return self

# Batch operation models
class BatchTaskIdsParams(BaseModel):
    task_ids: List[int] = Field(..., description="List of task IDs to operate on")
    task_uuids: Optional[Dict[int, str]] = Field(None, description="Optional mapping of task IDs to UUIDs for better reliability")

class BatchFilterParams(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status: pending, completed, deleted")
    project: Optional[str] = Field(None, description="Filter by project name")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (tasks with ANY of these tags)")
    priority: Optional[str] = Field(None, description="Filter by priority: H, M, L")
    description_contains: Optional[str] = Field(None, description="Filter by description containing text")
    due_before: Optional[str] = Field(None, description="Filter by due date before this date (ISO format)")
    due_after: Optional[str] = Field(None, description="Filter by due date after this date (ISO format)")
    limit: Optional[int] = Field(None, description="Maximum number of tasks to operate on")

class BatchModifyParams(BaseModel):
    # Either provide specific task IDs or filter criteria
    task_ids: Optional[List[int]] = Field(None, description="Specific task IDs to modify")
    filters: Optional[BatchFilterParams] = Field(None, description="Filter criteria to select tasks")
    # Fields to update
    project: Optional[str] = Field(None, description="Set project for all selected tasks")
    priority: Optional[str] = Field(None, description="Set priority for all selected tasks")
    add_tags: Optional[List[str]] = Field(None, description="Tags to add to all selected tasks")
    remove_tags: Optional[List[str]] = Field(None, description="Tags to remove from all selected tasks")
    due: Optional[str] = Field(None, description="Set due date for all selected tasks")

# ============================================================================
# TaskWarrior Data Models - Eliminates all safe_get workaround code
# ============================================================================

class TaskAnnotation(BaseModel):
    """Represents a task annotation"""
    entry: Optional[datetime] = Field(None, description="Annotation creation timestamp")
    description: str = Field(..., description="Annotation text")

class TaskModel(BaseModel):
    """
    Comprehensive Pydantic model for TaskWarrior tasks.
    
    This replaces all the safe_get_task_field() workaround code with clean,
    type-safe field access and automatic validation/serialization.
    """
    # Core fields (always present)
    id: Optional[int] = Field(None, description="Task ID")
    uuid: Optional[str] = Field(None, description="Task UUID")
    description: str = Field("", description="Task description")
    status: str = Field("pending", description="Task status")
    
    # Optional organizational fields
    project: Optional[str] = Field(None, description="Project name")
    priority: Optional[str] = Field(None, description="Priority (H/M/L)")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    
    # Numeric fields
    urgency: float = Field(0.0, description="Calculated urgency score")
    
    # Timestamp fields (automatically handled as UTC)
    entry: Optional[datetime] = Field(None, description="Task creation timestamp")
    modified: Optional[datetime] = Field(None, description="Last modification timestamp")
    due: Optional[datetime] = Field(None, description="Due date/time")
    start: Optional[datetime] = Field(None, description="Task start timestamp")
    end: Optional[datetime] = Field(None, description="Task completion timestamp")
    wait: Optional[datetime] = Field(None, description="Wait until timestamp")
    until: Optional[datetime] = Field(None, description="Expiry timestamp")
    
    # Complex fields
    annotations: List[TaskAnnotation] = Field(default_factory=list, description="Task annotations")
    depends: List[str] = Field(default_factory=list, description="Task dependencies (UUIDs)")
    recur: Optional[str] = Field(None, description="Recurrence pattern")
    
    class Config:
        # Enable datetime serialization to ISO format
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z' if v else None
        }
        # Allow field population by name or alias
        populate_by_name = True
        # Validate on assignment
        validate_assignment = True

    @field_validator('tags', mode='before')
    @classmethod
    def convert_tags(cls, v):
        """Convert TaskWarrior tags to list"""
        if v is None:
            return []
        if isinstance(v, (set, tuple)):
            return list(v)
        return v if isinstance(v, list) else []

    @field_validator('depends', mode='before') 
    @classmethod
    def convert_depends(cls, v):
        """Convert TaskWarrior depends to list"""
        if v is None:
            return []
        if isinstance(v, (set, tuple)):
            return list(v)
        return v if isinstance(v, list) else []

    @field_validator('annotations', mode='before')
    @classmethod
    def convert_annotations(cls, v):
        """Convert TaskWarrior annotations to TaskAnnotation objects"""
        if not v:
            return []
        
        result = []
        for ann in v:
            if isinstance(ann, dict):
                result.append(TaskAnnotation(**ann))
            elif hasattr(ann, 'entry') and hasattr(ann, 'description'):
                result.append(TaskAnnotation(
                    entry=ann.entry,
                    description=ann.description
                ))
        return result

    def to_utc_dict(self) -> Dict[str, Any]:
        """
        Export to dictionary with UTC timestamps.
        
        This replaces the entire task_to_dict() function with all its
        safe_get() calls and manual datetime handling.
        """
        def format_datetime(dt: Optional[datetime]) -> Optional[str]:
            if dt is None:
                return None
            # Ensure UTC timezone
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            utc_dt = dt.astimezone(datetime.now().astimezone().tzinfo)
            return utc_dt.isoformat().replace('+00:00', 'Z')
        
        data = self.model_dump()
        
        # Convert datetime fields to UTC ISO strings
        datetime_fields = ['entry', 'modified', 'due', 'start', 'end', 'wait', 'until']
        for field in datetime_fields:
            if data.get(field):
                data[field] = format_datetime(data[field])
        
        # Convert annotation timestamps
        if data.get('annotations'):
            for ann in data['annotations']:
                if ann.get('entry'):
                    ann['entry'] = format_datetime(ann['entry'])
        
        return data

    @classmethod
    def from_taskwarrior_task(cls, task) -> 'TaskModel':
        """
        Create TaskModel from TaskWarrior Task object.
        
        This replaces ALL the safe_get_task_field() workaround code
        with a single, clean conversion function.
        """
        def safe_get(field: str, default=None):
            """Internal helper - will be eliminated once we fully migrate"""
            try:
                value = task[field]
                # Special handling for ID field - ensure it's valid
                if field == 'id' and (value is None or value == 0):
                    # For tasks without valid IDs, we'll use None and handle it in the frontend
                    return None
                return value
            except (KeyError, AttributeError):
                return default
        
        # Get the task ID and ensure it's valid
        task_id = safe_get('id')
        
        # Direct field mapping - no more safe_get calls scattered everywhere!
        return cls(
            id=task_id,
            uuid=safe_get('uuid'),
            description=safe_get('description', ''),
            status=safe_get('status', 'pending'),
            project=safe_get('project'),
            priority=safe_get('priority'),
            tags=safe_get('tags', []),
            urgency=safe_get('urgency', 0.0),
            entry=safe_get('entry'),
            modified=safe_get('modified'),
            due=safe_get('due'),
            start=safe_get('start'),
            end=safe_get('end'),
            wait=safe_get('wait'),
            until=safe_get('until'),
            annotations=safe_get('annotations', []),
            depends=safe_get('depends', []),
            recur=safe_get('recur')
        )