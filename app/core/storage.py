import os
import shutil
import uuid
from pathlib import Path
from typing import IO, Any, BinaryIO, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from app.config import settings
from app.logger import logger

class StorageException(Exception):
    """Base exception for storage-related errors."""
    pass

class StorageFileNotFound(StorageException):
    """Raised when a file is not found in storage."""
    pass

class StoragePermissionDenied(StorageException):
    """Raised when there's a permission issue with storage."""
    pass

class StorageBackend:
    """Abstract base class for storage backends."""
    
    def save(self, file_data: Union[bytes, BinaryIO], file_path: str, content_type: str = None) -> str:
        """Save file data to storage."""
        raise NotImplementedError
    
    def get(self, file_path: str) -> Tuple[bytes, str]:
        """Retrieve file data from storage."""
        raise NotImplementedError
    
    def delete(self, file_path: str) -> bool:
        """Delete a file from storage."""
        raise NotImplementedError
    
    def exists(self, file_path: str) -> bool:
        """Check if a file exists in storage."""
        raise NotImplementedError
    
    def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Generate a URL to access the file."""
        raise NotImplementedError
    
    def get_size(self, file_path: str) -> int:
        """Get the size of a file in bytes."""
        raise NotImplementedError

class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, root_path: str = "uploads"):
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, file_path: str) -> Path:
        """Get the full filesystem path for a given file path."""
        # Prevent directory traversal
        normalized_path = Path(file_path).resolve()
        full_path = (self.root_path / normalized_path).resolve()
        
        # Ensure the path is within the root directory
        try:
            full_path.relative_to(self.root_path.resolve())
        except ValueError:
            raise StoragePermissionDenied("Invalid file path")
            
        return full_path
    
    def save(self, file_data: Union[bytes, BinaryIO], file_path: str, content_type: str = None) -> str:
        try:
            full_path = self._get_full_path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(file_data, bytes):
                full_path.write_bytes(file_data)
            else:
                with open(full_path, 'wb') as f:
                    shutil.copyfileobj(file_data, f)
            
            return str(full_path.relative_to(self.root_path))
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            raise StorageException(f"Failed to save file: {e}")
    
    def get(self, file_path: str) -> Tuple[bytes, str]:
        try:
            full_path = self._get_full_path(file_path)
            if not full_path.exists():
                raise StorageFileNotFound(f"File not found: {file_path}")
            
            content_type = "application/octet-stream"
            if full_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                content_type = f"image/{full_path.suffix[1:].lower()}"
            elif full_path.suffix.lower() == '.pdf':
                content_type = 'application/pdf'
                
            return full_path.read_bytes(), content_type
        except StorageFileNotFound:
            raise
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise StorageException(f"Failed to read file: {e}")
    
    def delete(self, file_path: str) -> bool:
        try:
            full_path = self._get_full_path(file_path)
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise StorageException(f"Failed to delete file: {e}")
    
    def exists(self, file_path: str) -> bool:
        try:
            full_path = self._get_full_path(file_path)
            return full_path.exists()
        except StoragePermissionDenied:
            return False
    
    def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        # In a real app, you might want to serve files through a web server
        return f"/files/{file_path}"
    
    def get_size(self, file_path: str) -> int:
        try:
            full_path = self._get_full_path(file_path)
            return full_path.stat().st_size
        except Exception as e:
            logger.error(f"Error getting file size for {file_path}: {e}")
            raise StorageException(f"Failed to get file size: {e}")

class S3Storage(StorageBackend):
    """Amazon S3 storage backend."""
    
    def __init__(self, bucket_name: str = None, **kwargs):
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            **kwargs
        )
    
    def _get_object_key(self, file_path: str) -> str:
        """Convert file path to S3 object key."""
        return str(Path(file_path).as_posix())
    
    def save(self, file_data: Union[bytes, BinaryIO], file_path: str, content_type: str = None) -> str:
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                
            self.client.upload_fileobj(
                file_data if hasattr(file_data, 'read') else file_data,
                self.bucket_name,
                self._get_object_key(file_path),
                ExtraArgs=extra_args
            )
            return file_path
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise StorageException(f"Failed to upload file to S3: {e}")
    
    def get(self, file_path: str) -> Tuple[bytes, str]:
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=self._get_object_key(file_path)
            )
            return response['Body'].read(), response.get('ContentType', 'application/octet-stream')
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise StorageFileNotFound(f"File not found: {file_path}")
            logger.error(f"S3 download error: {e}")
            raise StorageException(f"Failed to download file from S3: {e}")
    
    def delete(self, file_path: str) -> bool:
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=self._get_object_key(file_path)
            )
            return True
        except ClientError as e:
            logger.error(f"S3 delete error: {e}")
            raise StorageException(f"Failed to delete file from S3: {e}")
    
    def exists(self, file_path: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=self._get_object_key(file_path)
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"S3 head_object error: {e}")
            raise StorageException(f"Failed to check if file exists in S3: {e}")
    
    def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': self._get_object_key(file_path)
                },
                ExpiresIn=expires_in
            )
        except ClientError as e:
            logger.error(f"S3 generate_presigned_url error: {e}")
            raise StorageException(f"Failed to generate presigned URL: {e}")
    
    def get_size(self, file_path: str) -> int:
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=self._get_object_key(file_path)
            )
            return response['ContentLength']
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise StorageFileNotFound(f"File not found: {file_path}")
            logger.error(f"S3 head_object error: {e}")
            raise StorageException(f"Failed to get file size from S3: {e}")

def get_storage(backend: str = None) -> StorageBackend:
    """Get the configured storage backend."""
    backend = backend or settings.STORAGE_BACKEND.lower()
    
    if backend == 's3':
        return S3Storage()
    elif backend == 'local':
        return LocalStorage()
    else:
        raise ValueError(f"Unsupported storage backend: {backend}")

# Default storage instance
storage = get_storage()

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """Save an uploaded file to the storage backend."""
    try:
        # Generate a unique filename
        file_ext = Path(upload_file.filename).suffix
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = str(Path(destination) / filename)
        
        # Save the file
        storage.save(upload_file.file, file_path, upload_file.content_type)
        return file_path
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )

def get_file_response(file_path: str, filename: str = None, as_attachment: bool = False):
    """Get a FastAPI FileResponse for a file in storage."""
    try:
        file_data, media_type = storage.get(file_path)
        
        # If filename not provided, use the last part of the file_path
        if not filename:
            filename = Path(file_path).name
        
        # Create a temporary file to return
        temp_path = Path("temp") / filename
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_bytes(file_data)
        
        return FileResponse(
            path=temp_path,
            filename=filename,
            media_type=media_type,
            headers={"Content-Disposition": f"{'attachment' if as_attachment else 'inline'}; filename={filename}"}
        )
    except StorageFileNotFound:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error retrieving file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve file")
