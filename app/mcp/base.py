from pydantic import BaseModel, Field
from typing import Any, Generic, TypeVar, Optional
from uuid import uuid4
from datetime import datetime

T = TypeVar('T')

class Command(BaseModel):
    """Base class for all commands."""
    command_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Query(BaseModel):
    """Base class for all queries."""
    query_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CommandResponse(BaseModel, Generic[T]):
    """Generic response for commands."""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
    status_code: int = 200

    @classmethod
    def success(cls, data: T = None, message: str = None, status_code: int = 200) -> 'CommandResponse[T]':
        return cls(success=True, data=data, message=message, status_code=status_code)
    
    @classmethod
    def error(cls, error: str, message: str = None, status_code: int = 400) -> 'CommandResponse[None]':
        return cls(success=False, error=error, message=message, status_code=status_code)

class QueryResponse(BaseModel, Generic[T]):
    """Generic response for queries."""
    data: T
    success: bool = True
    message: Optional[str] = None
    status_code: int = 200
