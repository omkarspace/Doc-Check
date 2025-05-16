from typing import List, Dict, Optional
from app.models.batch import Batch, BatchStatus
from app.models.document import Document
from app.services.document_processor import DocumentProcessor
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
import asyncio
from datetime import datetime

class BatchProcessor:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.batch_size = settings.BATCH_SIZE

    async def create_batch(self, name: str, description: str, document_type: str, owner_id: int, db: Session) -> Dict:
        """
        Create a new batch processing job
        """
        batch = Batch(
            name=name,
            description=description,
            document_type=document_type,
            owner_id=owner_id
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch.__dict__

    async def add_documents_to_batch(self, batch_id: int, files: List[bytes], db: Session) -> Dict:
        """
        Add documents to an existing batch
        """
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")

        if batch.status != BatchStatus.PENDING:
            raise ValueError("Cannot add documents to a non-pending batch")

        documents = []
        for file in files:
            document = Document(
                filename=f"batch_{batch_id}_{len(batch.documents) + 1}",
                file_type=file.filename.split('.')[-1],
                document_type=batch.document_type,
                batch_id=batch_id,
                owner_id=batch.owner_id
            )
            documents.append(document)

        db.add_all(documents)
        batch.total_documents += len(files)
        db.commit()

        return {
            "batch_id": batch_id,
            "documents_added": len(files),
            "total_documents": batch.total_documents
        }

    async def process_batch(self, batch_id: int, db: Session) -> Dict:
        """
        Process all documents in a batch
        """
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")

        if batch.status != BatchStatus.PENDING:
            raise ValueError("Batch is not in pending state")

        try:
            batch.status = BatchStatus.PROCESSING
            db.commit()

            documents = db.query(Document).filter(
                Document.batch_id == batch_id,
                Document.status == "pending"
            ).all()

            # Process documents in parallel
            results = await asyncio.gather(
                *[self.document_processor.process_document(
                    doc.file_content,
                    doc.file_type,
                    doc.document_type
                ) for doc in documents]
            )

            # Update document statuses
            for result, doc in zip(results, documents):
                doc.processed_text = result["text"]
                doc.ai_analysis = result["analysis"]
                doc.status = "processed"
                batch.processed_documents += 1
                batch.success_count += 1

            batch.status = BatchStatus.COMPLETED
            db.commit()

            return {
                "batch_id": batch_id,
                "status": batch.status,
                "processed_documents": batch.processed_documents,
                "success_count": batch.success_count,
                "error_count": batch.error_count
            }

        except Exception as e:
            batch.status = BatchStatus.FAILED
            batch.error_count += 1
            db.commit()
            raise Exception(f"Error processing batch: {str(e)}")

    async def get_batch_status(self, batch_id: int, db: Session) -> Dict:
        """
        Get the status of a batch processing job
        """
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")

        return {
            "batch_id": batch.id,
            "name": batch.name,
            "status": batch.status,
            "total_documents": batch.total_documents,
            "processed_documents": batch.processed_documents,
            "success_count": batch.success_count,
            "error_count": batch.error_count,
            "created_at": batch.created_at.isoformat(),
            "updated_at": batch.updated_at.isoformat()
        }

    async def list_batches(self, owner_id: int, db: Session) -> List[Dict]:
        """
        List all batches for a user
        """
        batches = db.query(Batch).filter(Batch.owner_id == owner_id).all()
        return [batch.__dict__ for batch in batches]
