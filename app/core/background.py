import asyncio
import concurrent.futures
import functools
import inspect
from typing import Any, Callable, Coroutine, Dict, Optional, TypeVar, Union

from fastapi import BackgroundTasks, FastAPI
from fastapi.concurrency import run_in_threadpool

from app.config import settings
from app.logger import logger

T = TypeVar('T')

class BackgroundTaskManager:
    """Manager for background tasks with thread pool and task tracking."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or settings.MAX_WORKERS
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def run_in_background(
        self,
        func: Union[Callable[..., T], Callable[..., Coroutine[Any, Any, T]]],
        *args: Any,
        task_name: str = None,
        **kwargs: Any
    ) -> str:
        """
        Run a function in the background and track the task.
        
        Args:
            func: The function to run (can be sync or async)
            *args: Positional arguments to pass to the function
            task_name: Optional name for the task (for tracking)
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            str: Task ID for tracking
        """
        task_id = task_name or str(id(func)) + str(id(args)) + str(id(kwargs))
        
        async def wrapper():
            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = await run_in_threadpool(
                        self.executor, 
                        functools.partial(func, *args, **kwargs)
                    )
                return result
            except Exception as e:
                logger.error(f"Background task {task_id} failed: {e}", exc_info=True)
                raise
            finally:
                self.running_tasks.pop(task_id, None)
        
        # Create and store the task
        task = asyncio.create_task(wrapper())
        self.running_tasks[task_id] = task
        
        return task_id
    
    async def get_task_result(self, task_id: str, timeout: float = None) -> Any:
        """
        Get the result of a background task.
        
        Args:
            task_id: The ID of the task to get the result for
            timeout: Maximum time to wait for the task to complete (in seconds)
            
        Returns:
            The result of the task if completed
            
        Raises:
            asyncio.TimeoutError: If the task doesn't complete within the timeout
            Exception: If the task raised an exception
        """
        if task_id not in self.running_tasks:
            raise KeyError(f"No task with ID {task_id} found")
        
        task = self.running_tasks[task_id]
        return await asyncio.wait_for(task, timeout=timeout)
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if a task is currently running."""
        if task_id not in self.running_tasks:
            return False
        return not self.running_tasks[task_id].done()
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Returns:
            bool: True if the task was cancelled, False if it was already done
        """
        if task_id not in self.running_tasks:
            return False
            
        task = self.running_tasks[task_id]
        if task.done():
            return False
            
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            return True
        return False
    
    async def shutdown(self):
        """Shut down the background task manager and clean up resources."""
        # Cancel all running tasks
        for task_id in list(self.running_tasks.keys()):
            await self.cancel_task(task_id)
        
        # Shut down the executor
        self.executor.shutdown(wait=True)

# Global background task manager
background_tasks = BackgroundTaskManager()

def background_task(
    func: Callable = None, 
    *,
    task_name: str = None,
    manager: BackgroundTaskManager = None
):
    """
    Decorator to run a function as a background task.
    
    Example:
        @background_task(task_name="process_document")
        async def process_document(doc_id: str):
            # Long-running task
            pass
    """
    def decorator(f):
        task_name_ = task_name or f.__name__
        task_manager = manager or background_tasks
        
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            return await task_manager.run_in_background(
                f, 
                *args, 
                task_name=task_name_, 
                **kwargs
            )
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)

def setup_background_tasks(app: FastAPI):
    """Set up background tasks for FastAPI application."""
    @app.on_event("startup")
    async def startup_event():
        # Initialize background task manager
        app.state.background_tasks = background_tasks
    
    @app.on_event("shutdown")
    async def shutdown_event():
        # Shut down background task manager
        await background_tasks.shutdown()

# Helper function to add a background task to FastAPI's BackgroundTasks
def add_background_task(
    background_tasks: BackgroundTasks,
    func: Callable,
    *args: Any,
    **kwargs: Any
) -> None:
    """
    Add a background task to FastAPI's BackgroundTasks.
    
    This is a convenience function that handles both sync and async functions.
    """
    if inspect.iscoroutinefunction(func):
        background_tasks.add_task(func, *args, **kwargs)
    else:
        async def run_in_thread():
            return await run_in_threadpool(
                background_tasks.loop.run_in_executor,
                None,
                functools.partial(func, *args, **kwargs)
            )
        background_tasks.add_task(run_in_thread)
