import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

from app.config import settings

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Log format
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (e.g., 'DEBUG', 'INFO')
        log_file: Optional file to write logs to (in addition to console)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    if level is None:
        level = settings.LOG_LEVEL
    
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times in case get_logger is called multiple times
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_path = log_dir / log_file
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    
    return logger

# Default logger instance
logger = get_logger(__name__)

def log_exceptions(logger: logging.Logger = logger):
    """
    Decorator to log exceptions raised by the decorated function.
    
    Args:
        logger: Logger instance to use (defaults to root logger)
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}: {str(e)}")
                raise
                
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}: {str(e)}")
                raise
                
        return async_wrapper if hasattr(func, '__await__') else sync_wrapper
    
    return decorator
