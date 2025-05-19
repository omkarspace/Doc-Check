import os
import shutil
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.batch import Batch, BatchStatus
from app.models.document import Document, DocumentType
from app.models.document_version import DocumentVersion
from app.services.document_processor import process_document

def process_batch(batch_id: int, db: Session):
    """
    Process a batch of documents asynchronously.
    This function is designed to be run in a background task.
    """
    try:
        # Get the batch
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            print(f"Batch {batch_id} not found")
            return
        
        # Update batch status to PROCESSING
        batch.status = BatchStatus.PROCESSING
        batch.updated_at = datetime.utcnow()
        db.commit()
        
        # Process each file in the batch directory
        processed_count = 0
        for filename in os.listdir(batch.file_path):
            file_path = os.path.join(batch.file_path, filename)
            
            if os.path.isfile(file_path):
                try:
                    # Process the document
                    process_document(
                        file_path=file_path,
                        document_type=batch.document_type,
                        batch_id=batch.id,
                        owner_id=batch.owner_id,
                        db=db
                    )
                    processed_count += 1
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        # Update batch status
        batch.status = BatchStatus.COMPLETED
        batch.processed_count = processed_count
        batch.completed_at = datetime.utcnow()
        batch.updated_at = datetime.utcnow()
        
    except Exception as e:
        print(f"Error processing batch {batch_id}: {str(e)}")
        if batch:
            batch.status = BatchStatus.FAILED
            batch.updated_at = datetime.utcnow()
    
    finally:
        db.commit()
        db.close()

def process_document(
    file_path: str,
    document_type: DocumentType,
    batch_id: int,
    owner_id: int,
    db: Session
) -> Document:
    """
    Process a single document and create corresponding database records.
    """
    try:
        # Extract filename from path
        filename = os.path.basename(file_path)
        
        # Create document record
        document = Document(
            title=filename,
            content=None,  # Will be extracted during processing
            file_path=file_path,
            document_type=document_type,
            owner_id=owner_id,
            batch_id=batch_id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create initial document version
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content=None,  # Will be extracted during processing
            file_path=file_path,
            created_by=owner_id
        )
        
        db.add(version)
        db.commit()
        
        # TODO: Add document processing logic here
        # For example, extract text, process content, etc.
        
        return document
        
    except Exception as e:
        db.rollback()
        print(f"Error processing document {file_path}: {str(e)}")
        raise
