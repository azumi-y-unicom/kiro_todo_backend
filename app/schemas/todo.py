from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# Constants for field validation
TITLE_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 1000


class TodoBase(BaseModel):
    """Base schema for Todo items with common fields."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=TITLE_MAX_LENGTH,
        description=f"Todo title (required, max {TITLE_MAX_LENGTH} characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=DESCRIPTION_MAX_LENGTH,
        description=(
            f"Todo description (optional, max {DESCRIPTION_MAX_LENGTH} "
            "characters)"
        )
    )
    completed: bool = Field(default=False, description="Completion status")
    end_date: Optional[datetime] = Field(
        None, 
        description="Task deadline in ISO 8601 format (e.g., '2025-01-15T10:30:00Z'). Optional field for setting task completion deadlines."
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not just whitespace."""
        if v and not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class TodoCreate(TodoBase):
    """Schema for creating a new Todo item."""
    pass


class TodoUpdate(BaseModel):
    """Schema for updating an existing Todo item."""
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=TITLE_MAX_LENGTH,
        description=f"Todo title (optional, max {TITLE_MAX_LENGTH} characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=DESCRIPTION_MAX_LENGTH,
        description=(
            f"Todo description (optional, max {DESCRIPTION_MAX_LENGTH} "
            "characters)"
        )
    )
    completed: Optional[bool] = Field(None, description="Completion status")
    end_date: Optional[datetime] = Field(
        None, 
        description="Task deadline in ISO 8601 format (e.g., '2025-01-15T10:30:00Z'). Optional field for setting task completion deadlines."
    )


class TodoResponse(TodoBase):
    """Schema for Todo item responses including database fields."""
    id: int = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class TodoSearchParams(BaseModel):
    """Schema for Todo item search parameters with validation."""
    completed: Optional[bool] = Field(
        None, 
        description="Filter by completion status"
    )
    end_date_from: Optional[datetime] = Field(
        None, 
        description="Filter todos with end_date from this datetime (ISO 8601 format)"
    )
    end_date_to: Optional[datetime] = Field(
        None, 
        description="Filter todos with end_date until this datetime (ISO 8601 format)"
    )
    skip: int = Field(
        0, 
        ge=0, 
        description="Number of records to skip for pagination"
    )
    limit: int = Field(
        100, 
        ge=1, 
        le=1000, 
        description="Maximum number of records to return (1-1000)"
    )

    @model_validator(mode='after')
    def validate_date_range(self) -> 'TodoSearchParams':
        """Validate that end_date_from is not after end_date_to."""
        if (self.end_date_from and self.end_date_to and 
            self.end_date_from > self.end_date_to):
            raise ValueError('end_date_from must be before or equal to end_date_to')
        return self
