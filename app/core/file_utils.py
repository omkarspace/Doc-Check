import hashlib
import io
import magic
import mimetypes
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple, Union

from fastapi import UploadFile, HTTPException, status
from fastapi.datastructures import UploadFile as FastAPIUploadFile

from app.config import settings
from app.logger import logger

def get_file_extension(filename: str) -> str:
    """Extract the file extension from a filename."""
    return Path(filename).suffix.lower()

def get_mime_type(file_path: Union[str, Path]) -> str:
    """Get the MIME type of a file."""
    file_path = str(file_path)
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

def get_file_size(file: Union[str, Path, UploadFile]) -> int:
    """Get the size of a file in bytes."""
    if isinstance(file, (str, Path)):
        return Path(file).stat().st_size
    elif hasattr(file, 'size'):
        return file.size
    elif hasattr(file, 'file') and hasattr(file.file, 'tell'):
        current_pos = file.file.tell()
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(current_pos)  # Seek back to original position
        return size
    else:
        raise ValueError("Unsupported file type")

def calculate_file_hash(file: Union[str, Path, BinaryIO], hash_algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
    """Calculate the hash of a file."""
    hash_func = getattr(hashlib, hash_algorithm, hashlib.sha256)
    hasher = hash_func()
    
    if isinstance(file, (str, Path)):
        with open(file, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
    elif hasattr(file, 'read'):
        current_pos = file.tell()
        file.seek(0)
        for chunk in iter(lambda: file.read(chunk_size), b''):
            hasher.update(chunk)
        file.seek(current_pos)
    else:
        raise ValueError("Unsupported file type")
    
    return hasher.hexdigest()

def is_file_type_allowed(filename: str, allowed_extensions: list = None) -> bool:
    """Check if a file's extension is in the allowed list."""
    if allowed_extensions is None:
        allowed_extensions = settings.ALLOWED_EXTENSIONS
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_upload_file(
    file: UploadFile, 
    max_size: int = None, 
    allowed_extensions: list = None,
    allowed_mime_types: list = None
) -> None:
    """
    Validate an uploaded file.
    
    Args:
        file: The uploaded file
        max_size: Maximum file size in bytes
        allowed_extensions: List of allowed file extensions
        allowed_mime_types: List of allowed MIME types
    
    Raises:
        HTTPException: If the file is invalid
    """
    if max_size is None:
        max_size = settings.MAX_UPLOAD_SIZE
    
    if allowed_extensions is None:
        allowed_extensions = settings.ALLOWED_EXTENSIONS
    
    if allowed_mime_types is None:
        allowed_mime_types = settings.ALLOWED_MIME_TYPES
    
    # Check if file has a name
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )
    
    # Check file extension
    if not is_file_type_allowed(file.filename, allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    file_size = get_file_size(file)
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {max_size / (1024 * 1024):.1f}MB"
        )
    
    # Check MIME type
    if allowed_mime_types:
        # Read first 2048 bytes for MIME type detection
        file_content = file.file.read(2048)
        file.file.seek(0)  # Reset file pointer
        
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(file_content)
        
        if detected_mime not in allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Detected: {detected_mime}"
            )

def save_upload_file(
    upload_file: UploadFile,
    destination: Union[str, Path],
    filename: str = None,
    create_dirs: bool = True
) -> Path:
    """
    Save an uploaded file to the specified destination.
    
    Args:
        upload_file: The uploaded file
        destination: Directory to save the file in
        filename: Optional custom filename (defaults to the original filename)
        create_dirs: Whether to create parent directories if they don't exist
    
    Returns:
        Path to the saved file
    """
    destination = Path(destination)
    if create_dirs:
        destination.mkdir(parents=True, exist_ok=True)
    
    filename = filename or upload_file.filename
    file_path = destination / filename
    
    # Ensure the filename is unique
    counter = 1
    while file_path.exists():
        name = f"{file_path.stem}_{counter}{file_path.suffix}"
        file_path = destination / name
        counter += 1
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}"
        )
    finally:
        upload_file.file.close()
    
    return file_path

def create_temp_file(
    content: bytes,
    prefix: str = "temp",
    suffix: str = "",
    directory: Union[str, Path] = None
) -> Path:
    """
    Create a temporary file with the given content.
    
    Args:
        content: File content as bytes
        prefix: File name prefix
        suffix: File name suffix (including extension)
        directory: Directory to create the file in (defaults to system temp dir)
    
    Returns:
        Path to the created temporary file
    """
    if directory is not None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(
        mode='wb',
        prefix=prefix,
        suffix=suffix,
        dir=directory,
        delete=False
    ) as temp_file:
        temp_file.write(content)
        return Path(temp_file.name)

def extract_zip(
    zip_file: Union[str, Path, BinaryIO],
    extract_to: Union[str, Path],
    allowed_extensions: list = None,
    max_total_size: int = None
) -> List[Path]:
    """
    Extract a ZIP file to the specified directory.
    
    Args:
        zip_file: Path to the ZIP file or file-like object
        extract_to: Directory to extract files to
        allowed_extensions: List of allowed file extensions (None to allow all)
        max_total_size: Maximum total size of extracted files in bytes
    
    Returns:
        List of paths to the extracted files
    """
    if max_total_size is None:
        max_total_size = settings.MAX_EXTRACT_SIZE
    
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)
    
    extracted_files = []
    total_size = 0
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # First, validate all files
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                    
                # Check file extension
                if allowed_extensions and not is_file_type_allowed(file_info.filename, allowed_extensions):
                    continue
                
                # Check individual file size
                if file_info.file_size > settings.MAX_UPLOAD_SIZE:
                    continue
                
                # Check total extracted size
                total_size += file_info.file_size
                if total_size > max_total_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Extracted files exceed maximum allowed size"
                    )
            
            # Extract files
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                    
                # Skip files with invalid extensions
                if allowed_extensions and not is_file_type_allowed(file_info.filename, allowed_extensions):
                    continue
                
                # Extract the file
                extracted_path = zip_ref.extract(file_info, extract_to)
                extracted_files.append(Path(extracted_path))
    
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ZIP file"
        )
    except Exception as e:
        # Clean up any extracted files if there was an error
        for file_path in extracted_files:
            try:
                file_path.unlink()
            except OSError:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract ZIP file: {e}"
        )
    
    return extracted_files

def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Returns:
        Dictionary containing file information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    stat = file_path.stat()
    mime_type = get_mime_type(file_path)
    
    return {
        'filename': file_path.name,
        'path': str(file_path),
        'size': stat.st_size,
        'created': stat.st_ctime,
        'modified': stat.st_mtime,
        'mime_type': mime_type,
        'extension': file_path.suffix.lower(),
        'is_dir': file_path.is_dir(),
        'is_file': file_path.is_file(),
    }

def convert_to_upload_file(
    file_path: Union[str, Path],
    filename: str = None,
    content_type: str = None
) -> UploadFile:
    """
    Convert a file on disk to a FastAPI UploadFile.
    
    Args:
        file_path: Path to the file
        filename: Optional custom filename
        content_type: Optional content type
    
    Returns:
        FastAPI UploadFile instance
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    filename = filename or file_path.name
    
    if content_type is None:
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    file_obj = file_path.open('rb')
    
    # Create a file-like object that can be read multiple times
    file_content = file_obj.read()
    file_obj.close()
    
    return FastAPIUploadFile(
        filename=filename,
        file=io.BytesIO(file_content),
        content_type=content_type,
        size=len(file_content)
    )
