from typing import Dict, List, Optional, Any
from app.utils.ocr import TesseractOCR
from app.utils.ai import OpenAIProcessor
from app.utils.storage import S3Storage
from app.utils.validation import DocumentValidator
from app.utils.logging import DocumentLogger
from app.utils.metrics import MetricsCollector
from app.models.document import Document, DocumentStatus, DocumentType
from app.security import get_current_user
import json
import time
from datetime import datetime
from fastapi import HTTPException
from app.utils.exceptions import DocumentProcessingError

class DocumentProcessor:
    def __init__(self):
        self.ocr = TesseractOCR()
        self.ai_processor = OpenAIProcessor()
        self.storage = S3Storage()
        self.validator = DocumentValidator()
        self.logger = DocumentLogger()
        self.metrics = MetricsCollector()
        self.supported_formats = settings.SUPPORTED_FILE_TYPES
        self.max_file_size = settings.MAX_FILE_SIZE

    async def process_document(self, document: Document) -> Dict[str, Any]:
        """
        Process a document with enhanced validation and error handling
        """
        try:
            # 1. Validate document
            if not self.validator.validate(document):
                raise DocumentProcessingError("Document validation failed")
            
            # 2. Extract text using OCR
            text = await self.ocr.extract_text(document)
            
            # 3. Process with AI
            processed_data = await self.ai_processor.process(text)
            
            # 4. Store processed document
            await self.storage.store_processed_document(document, processed_data)
            
            # 5. Log processing
            self.logger.log_processing(document, processed_data)
            
            # 6. Collect metrics
            processing_time = time.time() - document.created_at.timestamp()
            self.metrics.collect_metrics(document, processed_data, processing_time)
            
            return {
                "status": "success",
                "document_id": document.id,
                "processed_data": processed_data,
                "processing_time": processing_time,
                "processed_at": datetime.utcnow().isoformat()
            }
        except DocumentProcessingError as e:
            self.logger.log_error(document, str(e))
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )
        except Exception as e:
            self.logger.log_error(document, str(e))
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during document processing"
            )

    async def _extract_text_from_file(self, file: bytes, file_type: str) -> str:
        """
        Extract text from PDF or DOCX file
        """
        if file_type == '.pdf':
            # Convert PDF to images and process
            images = await self._convert_pdf_to_images(file)
            return await self.process_multiple_images(images)
            return await process_multiple_images(images)
        elif file_type == '.docx':
            # Extract text from DOCX
            return await self._extract_text_from_docx(file)
        return ""

    async def _convert_pdf_to_images(self, pdf_file: bytes) -> List[bytes]:
        """
        Convert PDF to images for OCR processing
        """
        # Implementation using pdf2image
        pass

    async def _extract_text_from_docx(self, docx_file: bytes) -> str:
        """
        Extract text from DOCX file
        """
        # Implementation using python-docx
        pass

    def get_processing_statistics(self) -> Dict:
        """
        Get document processing statistics
        """
        if not self.processing_times:
            return {
                "total_documents": 0,
                "average_processing_time": 0,
                "fastest_processing": 0,
                "slowest_processing": 0
            }

        avg_time = sum(self.processing_times) / len(self.processing_times)
        fastest = min(self.processing_times)
        slowest = max(self.processing_times)

        return {
            "total_documents": len(self.processing_times),
            "average_processing_time": avg_time,
            "fastest_processing": fastest,
            "slowest_processing": slowest
        }
