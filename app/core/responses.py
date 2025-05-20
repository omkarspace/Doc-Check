from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from fastapi import status
from fastapi.responses import JSONResponse

T = TypeVar('T')

class ErrorResponse(BaseModel):
    """Standard error response model."""
    success: bool = Field(default=False, description="Indicates if the request was successful")
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")

class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response model with data."""
    success: bool = Field(default=True, description="Indicates if the request was successful")
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(default=None, description="Optional success message")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class PaginatedResponse(SuccessResponse[List[T]]):
    """Paginated response model."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    @classmethod
    def create(
        cls, 
        items: List[T], 
        total: int, 
        page: int, 
        limit: int,
        **kwargs
    ) -> 'PaginatedResponse[T]':
        """Create a paginated response."""
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        return cls(
            data=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            **kwargs
        )

class APIResponse(JSONResponse):
    """Custom JSON response with consistent structure."""
    
    def __init__(
        self,
        data: Any = None,
        status_code: int = status.HTTP_200_OK,
        message: str = None,
        meta: Dict[str, Any] = None,
        **kwargs
    ):
        response_data = {
            "success": status_code < 400,
        }
        
        if data is not None:
            response_data["data"] = data
        
        if message is not None:
            response_data["message"] = message
            
        if meta is not None:
            response_data["meta"] = meta
        
        # Handle error responses
        if status_code >= 400:
            if "error" not in response_data and "detail" in response_data:
                response_data["error"] = response_data.pop("detail")
            response_data["code"] = status_code
        
        super().__init__(
            content=response_data,
            status_code=status_code,
            **kwargs
        )

# Common HTTP responses
class HTTPResponses:
    """Common HTTP responses with consistent structure."""
    
    @staticmethod
    def ok(
        data: Any = None, 
        message: str = "Request successful",
        **kwargs
    ) -> APIResponse:
        """200 OK response."""
        return APIResponse(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK,
            **kwargs
        )
    
    @staticmethod
    def created(
        data: Any = None, 
        message: str = "Resource created successfully",
        **kwargs
    ) -> APIResponse:
        """201 Created response."""
        return APIResponse(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            **kwargs
        )
    
    @staticmethod
    def no_content() -> APIResponse:
        """204 No Content response."""
        return APIResponse(
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @staticmethod
    def bad_request(
        error: str = "Bad Request",
        details: Dict[str, Any] = None,
        **kwargs
    ) -> APIResponse:
        """400 Bad Request response."""
        content = {"error": error}
        if details is not None:
            content["details"] = details
        return APIResponse(
            **content,
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs
        )
    
    @staticmethod
    def unauthorized(
        error: str = "Not authenticated",
        **kwargs
    ) -> APIResponse:
        """401 Unauthorized response."""
        return APIResponse(
            error=error,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )
    
    @staticmethod
    def forbidden(
        error: str = "Forbidden",
        **kwargs
    ) -> APIResponse:
        """403 Forbidden response."""
        return APIResponse(
            error=error,
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs
        )
    
    @staticmethod
    def not_found(
        resource: str = "Resource",
        **kwargs
    ) -> APIResponse:
        """404 Not Found response."""
        return APIResponse(
            error=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs
        )
    
    @staticmethod
    def conflict(
        error: str = "Conflict",
        **kwargs
    ) -> APIResponse:
        """409 Conflict response."""
        return APIResponse(
            error=error,
            status_code=status.HTTP_409_CONFLICT,
            **kwargs
        )
    
    @staticmethod
    def too_many_requests(
        error: str = "Too many requests",
        retry_after: int = None,
        **kwargs
    ) -> APIResponse:
        """429 Too Many Requests response."""
        headers = {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)
        return APIResponse(
            error=error,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers=headers,
            **kwargs
        )
    
    @staticmethod
    def internal_server_error(
        error: str = "Internal Server Error",
        **kwargs
    ) -> APIResponse:
        """500 Internal Server Error response."""
        return APIResponse(
            error=error,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )
    
    @staticmethod
    def service_unavailable(
        error: str = "Service Unavailable",
        **kwargs
    ) -> APIResponse:
        """503 Service Unavailable response."""
        return APIResponse(
            error=error,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            **kwargs
        )

# Alias for easier access
responses = HTTPResponses()
