import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from app.config import settings
from app.logger import logger

class RateLimitExceeded(HTTPException):
    """Exception raised when a rate limit is exceeded."""
    
    def __init__(
        self, 
        detail: str = "Rate limit exceeded",
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers or {}
        )

class RateLimiter:
    """
    A simple rate limiter that tracks requests per client.
    
    This implementation uses a sliding window algorithm to track requests.
    """
    
    def __init__(
        self, 
        rate_limit: str = None,
        block_duration: int = 300,  # 5 minutes
        prefix: str = "rate_limit:",
        storage: Any = None
    ):
        """
        Initialize the rate limiter.
        
        Args:
            rate_limit: Rate limit string in the format "requests/seconds" (e.g., "100/minute")
            block_duration: Duration in seconds to block after rate limit is exceeded
            prefix: Prefix for storage keys
            storage: Storage backend (defaults to in-memory dict if not provided)
        """
        self.rate_limit = rate_limit or settings.RATE_LIMIT
        self.block_duration = block_duration
        self.prefix = prefix
        self.storage = storage or {}
        
        # Parse rate limit string (e.g., "100/minute" -> (100, 60))
        self.limit, self.period = self._parse_rate_limit(self.rate_limit)
    
    def _parse_rate_limit(self, rate_limit: str) -> Tuple[int, int]:
        """Parse rate limit string into (limit, period_seconds)."""
        try:
            num_requests, period = rate_limit.split("/")
            num_requests = int(num_requests.strip())
            
            period = period.strip().lower()
            if period.startswith("second"):
                period_seconds = 1
            elif period.startswith("minute"):
                period_seconds = 60
            elif period.startswith("hour"):
                period_seconds = 3600
            elif period.startswith("day"):
                period_seconds = 86400
            else:
                raise ValueError(f"Invalid period: {period}")
                
            return num_requests, period_seconds
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Invalid rate limit format: {rate_limit}. Using default 100/minute.")
            return 100, 60  # Default to 100 requests per minute
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get a unique identifier for the client."""
        # In production, you might want to use a more reliable method
        # like API keys, user ID, or a combination of headers
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        return f"{self.prefix}{client_ip}:{user_agent}"
    
    def _get_current_window(self, now: float) -> Tuple[int, int]:
        """Get the current time window."""
        return int(now // self.period)
    
    def _get_window_key(self, client_id: str, window: int) -> str:
        """Get the storage key for a window."""
        return f"{client_id}:{window}"
    
    def is_rate_limited(self, client_id: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if a client has exceeded the rate limit.
        
        Returns:
            Tuple of (is_limited, headers)
        """
        now = time.time()
        current_window = self._get_current_window(now)
        
        # Clean up old windows
        self._cleanup_old_windows(client_id, current_window)
        
        # Check if client is blocked
        block_key = f"{client_id}:blocked"
        if block_key in self.storage:
            block_until = self.storage[block_key]
            if now < block_until:
                retry_after = int(block_until - now) + 1
                headers = {
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(block_until)),
                }
                return True, headers
            else:
                del self.storage[block_key]
        
        # Get or initialize the current window
        window_key = self._get_window_key(client_id, current_window)
        current_count = self.storage.get(window_key, 0)
        
        # Calculate remaining requests
        remaining = max(0, self.limit - current_count - 1)
        
        # Prepare headers
        reset_time = (current_window + 1) * self.period
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(reset_time)),
        }
        
        # Check if rate limit is exceeded
        if current_count >= self.limit:
            # Block the client
            self.storage[block_key] = now + self.block_duration
            headers["Retry-After"] = str(self.block_duration)
            return True, headers
        
        # Increment the counter
        self.storage[window_key] = current_count + 1
        return False, headers
    
    def _cleanup_old_windows(self, client_id: str, current_window: int) -> None:
        """Remove old window data to prevent memory leaks."""
        # Only keep the current window and previous window for better rate limiting
        keys_to_keep = [
            self._get_window_key(client_id, current_window - 1),
            self._get_window_key(client_id, current_window),
        ]
        
        # Remove all keys except the ones to keep
        for key in list(self.storage.keys()):
            if key.startswith(f"{client_id}:") and key not in keys_to_keep and not key.endswith(":blocked"):
                del self.storage[key]

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting requests.
    
    This middleware can be configured globally or per-route.
    """
    
    def __init__(
        self, 
        app,
        rate_limit: str = None,
        block_duration: int = 300,
        exclude_paths: List[str] = None,
        **kwargs
    ):
        super().__init__(app)
        self.rate_limiter = RateLimiter(
            rate_limit=rate_limit,
            block_duration=block_duration,
            **kwargs
        )
        self.exclude_paths = set(exclude_paths or ["/docs", "/redoc", "/openapi.json", "/health"])
    
    async def dispatch(
        self, 
        request: StarletteRequest,
        call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get client identifier
        client_id = self.rate_limiter._get_client_identifier(request)
        
        # Check rate limit
        is_limited, headers = self.rate_limiter.is_rate_limited(client_id)
        
        if is_limited:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
                headers=headers
            )
            response.headers.update(headers)
            return response
        
        # Add rate limit headers to the response
        response = await call_next(request)
        response.headers.update(headers)
        return response

def rate_limit(
    rate_limit: str = None,
    block_duration: int = 300,
    key_func: Callable[[Request], str] = None,
    exclude: List[str] = None
):
    """
    Decorator to apply rate limiting to a specific endpoint.
    
    Example:
        @app.get("/api/endpoint")
        @rate_limit("10/minute")
        async def endpoint(request: Request):
            return {"message": "Hello, World!"}
    """
    def decorator(func):
        limiter = RateLimiter(
            rate_limit=rate_limit,
            block_duration=block_duration
        )
        
        if key_func is None:
            def default_key_func(request: Request) -> str:
                return limiter._get_client_identifier(request)
            _key_func = default_key_func
        else:
            _key_func = key_func
        
        _exclude = set(exclude or [])
        
        async def wrapper(request: Request, *args, **kwargs):
            # Skip rate limiting for excluded paths
            if request.url.path in _exclude:
                return await func(request, *args, **kwargs)
                
            # Get client identifier
            client_id = _key_func(request)
            
            # Check rate limit
            is_limited, headers = limiter.is_rate_limited(client_id)
            
            if is_limited:
                raise RateLimitExceeded(headers=headers)
                
            # Call the original function
            response = await func(request, *args, **kwargs)
            
            # Add rate limit headers to the response
            if hasattr(response, 'headers'):
                response.headers.update(headers)
            
            return response
            
        return wrapper
    
    return decorator
