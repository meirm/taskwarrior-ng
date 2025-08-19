# Pydantic Documentation - Python Data Validation Library

*Last Updated: January 2025*

## Overview

Pydantic is the most widely used Python data validation library, offering fast and extensible data validation using Python type hints. It provides runtime type checking, automatic data conversion, and detailed error reporting.

## Official Resources

- **Official Documentation**: [docs.pydantic.dev](https://docs.pydantic.dev/latest/)
- **GitHub Repository**: [github.com/pydantic/pydantic](https://github.com/pydantic/pydantic)
- **PyPI Package**: [pypi.org/project/pydantic](https://pypi.org/project/pydantic)

## Key Features (2025)

- **Python 3.9+ Support** (3.11+ recommended for best performance)
- **Rust-powered Core**: Core validation logic written in Rust for extreme performance
- **Type Safety**: Uses Python type hints for schema validation
- **JSON Schema Generation**: Automatic schema generation for API documentation
- **Extensive Ecosystem**: Wide adoption by major companies (FAANG+)
- **IDE Integration**: Full support for IDEs and static analysis tools

## Requirements

- Python 3.9 and above (Python 3.11+ recommended)
- Optional: `email-validator` for email validation
- Optional: `logfire` for validation monitoring and debugging

## Installation

```bash
# Basic installation
pip install pydantic

# With email validation
pip install 'pydantic[email]'

# Development version
pip install -U --pre pydantic
```

## Basic Usage

### Simple Model Definition

```python
from datetime import datetime
from pydantic import BaseModel, PositiveInt

class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None = None
    tastes: dict[str, PositiveInt]

# Usage
user_data = {
    'id': '123',  # Will be converted to int
    'signup_ts': '2025-01-01T12:00:00',  # Will be parsed to datetime
    'tastes': {'coffee': 5, 'tea': 3}
}

user = User(**user_data)
print(user.id)  # 123 (as int)
print(user.signup_ts)  # 2025-01-01 12:00:00 (as datetime)
```

### Model Properties

```python
# Access model data
print(user.model_dump())  # Dictionary representation
print(user.model_dump_json())  # JSON string
print(user.model_fields)  # Field information
print(user.model_json_schema())  # JSON schema
```

## Field Definitions and Constraints

### Using Field Function

```python
from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Product name")
    price: float = Field(gt=0, description="Product price must be positive")
    quantity: int = Field(default=0, ge=0, le=1000)
    description: Optional[str] = Field(None, max_length=500)
    tags: list[str] = Field(default_factory=list)
```

### Common Field Constraints

```python
class ValidationExample(BaseModel):
    # String constraints
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    
    # Numeric constraints
    age: int = Field(ge=0, le=120)  # >= 0 and <= 120
    score: float = Field(gt=0, lt=100)  # > 0 and < 100
    
    # Collection constraints
    tags: list[str] = Field(min_length=1, max_length=10)
    
    # Default values
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = Field(default=True)
```

## Validators

### Field Validators

```python
from pydantic import BaseModel, field_validator

class UserModel(BaseModel):
    name: str
    email: str
    age: int
    
    @field_validator('name')
    @classmethod
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('Name must contain a space')
        return v.title()
    
    @field_validator('email')
    @classmethod
    def email_validation(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('age')
    @classmethod
    def age_validation(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        if v > 120:
            raise ValueError('Age seems unrealistic')
        return v
```

### Model Validators

```python
from pydantic import BaseModel, model_validator

class UserRegistration(BaseModel):
    username: str
    password: str
    password_confirm: str
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self
```

### Before and Wrap Validators

```python
from pydantic import BaseModel, field_validator, ValidationInfo

class DataProcessor(BaseModel):
    value: str
    
    @field_validator('value', mode='before')
    @classmethod
    def convert_to_string(cls, v):
        # Convert any input to string before validation
        return str(v)
    
    @field_validator('value', mode='wrap')
    @classmethod
    def validate_and_clean(cls, v, handler, info: ValidationInfo):
        # Run before validation, call handler, then post-process
        try:
            result = handler(v)  # Run normal validation
            return result.strip().lower()  # Post-process result
        except ValueError:
            return 'default_value'
```

## Advanced Features

### Nested Models

```python
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str = 'US'

class User(BaseModel):
    name: str
    addresses: List[Address]

# Usage
user_data = {
    'name': 'John Doe',
    'addresses': [
        {'street': '123 Main St', 'city': 'New York'},
        {'street': '456 Oak Ave', 'city': 'Los Angeles'}
    ]
}
user = User(**user_data)
```

### Generic Models

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    success: bool
    data: T
    message: str = ""

# Usage
class User(BaseModel):
    name: str
    email: str

user_response = Response[User](
    success=True,
    data=User(name="John", email="john@example.com")
)
```

### Dynamic Model Creation

```python
from pydantic import create_model

# Create model dynamically
DynamicModel = create_model(
    'DynamicModel',
    name=(str, 'Default Name'),
    age=(int, Field(gt=0)),
    email=(str, ...)
)

instance = DynamicModel(age=25, email='test@example.com')
```

## Configuration

### Model Configuration

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(
        # Don't allow extra fields
        extra='forbid',
        # Validate field assignments
        validate_assignment=True,
        # Use enum values instead of names
        use_enum_values=True,
        # Strict mode - no type coercion
        strict=True,
        # Frozen - immutable after creation
        frozen=True
    )
    
    name: str
    age: int
```

### Flexible Configuration

```python
class FlexibleModel(BaseModel):
    model_config = ConfigDict(
        # Allow extra fields
        extra='allow',
        # Don't validate assignments (performance)
        validate_assignment=False,
        # Allow population by field name or alias
        populate_by_name=True
    )
    
    name: str = Field(alias='full_name')
    age: int
```

## Serialization and Deserialization

### Custom Serialization

```python
from pydantic import BaseModel, field_serializer

class User(BaseModel):
    name: str
    email: str
    created_at: datetime
    
    @field_serializer('email')
    def serialize_email(self, value):
        # Hide email domain for privacy
        username, domain = value.split('@')
        return f"{username}@***"
    
    @field_serializer('created_at')
    def serialize_datetime(self, value):
        return value.strftime('%Y-%m-%d %H:%M:%S')

# Usage
user = User(name="John", email="john@example.com", created_at=datetime.now())
print(user.model_dump())  # Uses custom serializers
```

### JSON Handling

```python
import json
from datetime import datetime
from pydantic import BaseModel

class Event(BaseModel):
    name: str
    timestamp: datetime
    participants: list[str]

# From JSON
json_data = '{"name": "Meeting", "timestamp": "2025-01-01T10:00:00", "participants": ["Alice", "Bob"]}'
event = Event.model_validate_json(json_data)

# To JSON
json_output = event.model_dump_json()
```

## Error Handling

### Validation Errors

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    age: int

try:
    User(name="John", age="not_a_number")
except ValidationError as e:
    print(e.json())  # Detailed error information
    
    # Iterate through errors
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

### Custom Error Messages

```python
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

class User(BaseModel):
    age: int = Field(description="User age")
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0:
            raise PydanticCustomError(
                'negative_age',
                'Age cannot be negative: {age}',
                {'age': v}
            )
        return v
```

## Integration Patterns (2025)

### FastAPI Integration

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Pydantic automatically validates request body
    return UserResponse(id=1, **user.model_dump())
```

### MCP Server Integration

```python
# Example from our taskwarrior server
from pydantic import BaseModel, Field
from fastmcp import FastMCP

class AddTaskParams(BaseModel):
    description: str = Field(..., description="Task description")
    project: Optional[str] = Field(None, description="Project name")
    priority: Optional[str] = Field(None, description="Priority: H, M, L")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    due: Optional[str] = Field(None, description="Due date in ISO format")

mcp = FastMCP("taskwarrior")

@mcp.tool()
async def add_task(params: AddTaskParams) -> Dict[str, Any]:
    # FastMCP automatically validates params using Pydantic
    # params is guaranteed to match AddTaskParams schema
    return {"success": True, "task_id": 123}
```

## Performance Optimization

### Best Practices

```python
from pydantic import BaseModel, ConfigDict

class HighPerformanceModel(BaseModel):
    model_config = ConfigDict(
        # Disable validation on assignment for performance
        validate_assignment=False,
        # Use slots for memory efficiency
        extra='forbid',
        # Avoid deep copying when possible
        arbitrary_types_allowed=True
    )
    
    # Use specific types instead of Any
    name: str  # Not: name: Any
    count: int  # Not: count: Union[int, str]
```

### Computed Fields

```python
from pydantic import BaseModel, computed_field

class User(BaseModel):
    first_name: str
    last_name: str
    
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

user = User(first_name="John", last_name="Doe")
print(user.full_name)  # "John Doe"
```

## Common Patterns and Solutions

### Optional Fields with Defaults

```python
from typing import Optional
from pydantic import BaseModel, Field

class Task(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(default="medium", description="Task priority")
    tags: list[str] = Field(default_factory=list)
```

### Handling Different Input Formats

```python
from pydantic import BaseModel, field_validator

class DateModel(BaseModel):
    event_date: datetime
    
    @field_validator('event_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            # Handle multiple date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y']:
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError('Invalid date format')
        return v
```

### Model Inheritance

```python
class BaseEntity(BaseModel):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class User(BaseEntity):
    name: str
    email: str

class Product(BaseEntity):
    name: str
    price: float
```

## Testing with Pydantic

### Unit Testing Models

```python
import pytest
from pydantic import ValidationError

def test_user_creation():
    user = User(name="John Doe", age=30)
    assert user.name == "John Doe"
    assert user.age == 30

def test_user_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        User(name="John", age="not_a_number")
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('age',)
    assert 'int' in errors[0]['type']
```

## Monitoring and Debugging

### Integration with Logfire (2025)

```python
from pydantic import BaseModel
import logfire

# Enable Pydantic instrumentation
logfire.instrument_pydantic()

class User(BaseModel):
    name: str
    age: int

# Validation events are automatically logged to Logfire
user = User(name="John", age=30)
```

## Migration from Pydantic v1

### Key Changes in v2

```python
# v1 Style (deprecated)
class OldUser(BaseModel):
    class Config:
        extra = 'forbid'
    
    name: str

# v2 Style (current)
class NewUser(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    name: str

# Method name changes
# v1: user.dict() -> v2: user.model_dump()
# v1: user.json() -> v2: user.model_dump_json()
# v1: User.parse_obj() -> v2: User.model_validate()
```

## Resources for Learning

### Official Resources
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GitHub Examples](https://github.com/pydantic/pydantic/tree/main/docs/examples)
- [Logfire Integration](https://logfire.pydantic.dev/)

### Community Resources
- Stack Overflow: `python-pydantic` tag
- Discord: Pydantic community server
- GitHub Discussions for Q&A

## Getting Started Checklist

1. **Install Pydantic**: `pip install pydantic`
2. **Start Simple**: Create basic models with type hints
3. **Add Validation**: Use Field constraints and validators
4. **Handle Errors**: Implement proper ValidationError handling
5. **Test Thoroughly**: Write unit tests for your models
6. **Optimize**: Use configuration options for performance
7. **Integrate**: Connect with your web framework or application

Remember: Pydantic's power comes from leveraging Python's type system. Start with type hints and gradually add more sophisticated validation as needed!