from typing import Any, Callable, Dict, Type, TypeVar, Optional
from pydantic import BaseModel
from fastapi import HTTPException
from .base import Command, Query, CommandResponse, QueryResponse

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')

class CommandBus:
    def __init__(self):
        self._handlers: Dict[Type[BaseModel], Callable] = {}
    
    def register_handler(self, command_type: Type[T], handler: Callable[[T], Any]):
        """Register a handler for a specific command type."""
        self._handlers[command_type] = handler
    
    async def execute(self, command: BaseModel) -> Any:
        """Execute a command with its registered handler."""
        command_type = type(command)
        handler = self._handlers.get(command_type)
        
        if not handler:
            raise ValueError(f"No handler registered for {command_type.__name__}")
        
        try:
            result = await handler(command)
            return result
        except HTTPException:
            raise
        except Exception as e:
            # Log the error and re-raise as HTTPException
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error: {str(e)}"
            )

# Global command bus instance
command_bus = CommandBus()

def command_handler(command_type: Type[T]):
    """Decorator to register a command handler."""
    def decorator(handler: Callable[[T], Any]):
        command_bus.register_handler(command_type, handler)
        return handler
    return decorator
