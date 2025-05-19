from fastapi import Depends, HTTPException
from typing import Type, TypeVar, Generic, Any, Optional
from pydantic import BaseModel
from .command_bus import command_bus
from .base import Command, Query, CommandResponse, QueryResponse

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')

class CommandDependency(Generic[T, R]):
    def __init__(self, command_type: Type[T]):
        self.command_type = command_type
    
    async def __call__(self, command: T) -> R:
        """Execute a command and return the result."""
        return await command_bus.execute(command)

def execute_command(command_type: Type[T]) -> CommandDependency[T, R]:
    """Dependency to execute a command.
    
    Usage in FastAPI route:
    @app.post("/documents/")
    async def create_document(
        result: CommandResponse[Document] = Depends(execute_command(CreateDocument))
    ):
        return result
    """
    return CommandDependency[command_type, CommandResponse[R]](command_type)

class QueryDependency(Generic[T, R]):
    def __init__(self, query_type: Type[T]):
        self.query_type = query_type
    
    async def __call__(self, query: T) -> R:
        """Execute a query and return the result."""
        return await command_bus.execute(query)

def execute_query(query_type: Type[T]) -> QueryDependency[T, R]:
    """Dependency to execute a query.
    
    Usage in FastAPI route:
    @app.get("/documents/{id}")
    async def get_document(
        result: QueryResponse[Document] = Depends(execute_query(GetDocument))
    ):
        return result
    """
    return QueryDependency[query_type, QueryResponse[R]](query_type)
