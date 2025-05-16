from typing import Dict, List, Optional
from app.utils.ocr import process_image, process_multiple_images
from app.utils.ai import analyze_document
from app.models.document import DocumentType
from app.security.security import redact_pii
import json
import time
from datetime import datetime

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = settings.SUPPORTED_FILE_TYPES
        self.max_file_size = settings.MAX_FILE_SIZE
        self.processing_times = []

    async def process_document(self, file: bytes, file_type: str, document_type: DocumentType) -> Dict:
        """
        Process a document and extract relevant information
        """
        start_time = time.time()

        if file_type not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {file_type}")

        if len(file) > self.max_file_size:
            raise ValueError("File size exceeds maximum allowed size")

        try:
            if file_type in ['.jpg', '.png']:
                # Process image file
                text = await process_image(file)
            else:
                # Process PDF/DOCX file
                text = await self._extract_text_from_file(file, file_type)

            # Redact PII before AI analysis
            redacted_text = redact_pii(text)

            # Analyze document using AI
            analysis = await analyze_document(redacted_text, document_type.value)

            # Track processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)

            return {
                "status": "success",
                "text": text,
                "redacted_text": redacted_text,
                "analysis": analysis,
                "processing_time": processing_time,
                "processed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

    async def _extract_text_from_file(self, file: bytes, file_type: str) -> str:
        """
        Extract text from PDF or DOCX file
        """
        if file_type == '.pdf':
            # Convert PDF to images and process
            images = await self._convert_pdf_to_images(file)
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
