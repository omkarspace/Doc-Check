from typing import List, Dict, Optional
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
import json
import csv
from openpyxl import Workbook
from xml.etree import ElementTree as ET

class ExportService:
    def __init__(self):
        self.supported_formats = ["json", "csv", "xlsx", "xml"]

    async def export_document(
        self,
        document_id: int,
        format: str,
        version: Optional[int] = None,
        db: Session = Depends(get_db)
    ) -> bytes:
        """
        Export a document in the specified format
        """
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}")

        if version:
            document = await self._get_document_version(document_id, version, db)
        else:
            document = await self._get_latest_document(document_id, db)

        if not document:
            raise ValueError("Document not found")

        data = {
            "metadata": {
                "document_id": document.id,
                "filename": document.filename,
                "document_type": document.document_type,
                "processed_at": document.created_at.isoformat()
            },
            "content": document.processed_text,
            "analysis": document.ai_analysis
        }

        return await self._export_data(data, format)

    async def export_batch(
        self,
        batch_id: int,
        format: str,
        db: Session = Depends(get_db)
    ) -> bytes:
        """
        Export all documents in a batch
        """
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}")

        documents = db.query(Document).filter(
            Document.batch_id == batch_id
        ).all()

        if not documents:
            raise ValueError("No documents found in batch")

        data = []
        for doc in documents:
            doc_data = {
                "metadata": {
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "document_type": doc.document_type,
                    "processed_at": doc.created_at.isoformat()
                },
                "content": doc.processed_text,
                "analysis": doc.ai_analysis
            }
            data.append(doc_data)

        return await self._export_data(data, format)

    async def _get_document_version(
        self,
        document_id: int,
        version: int,
        db: Session
    ) -> Optional[DocumentVersion]:
        """
        Get a specific version of a document
        """
        version = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version
        ).first()
        return version

    async def _get_latest_document(
        self,
        document_id: int,
        db: Session
    ) -> Optional[Document]:
        """
        Get the latest version of a document
        """
        document = db.query(Document).filter(
            Document.id == document_id
        ).first()
        return document

    async def _export_data(self, data: Dict, format: str) -> bytes:
        """
        Export data in the specified format
        """
        if format == "json":
            return self._export_json(data)
        elif format == "csv":
            return self._export_csv(data)
        elif format == "xlsx":
            return self._export_xlsx(data)
        elif format == "xml":
            return self._export_xml(data)
        return b""

    def _export_json(self, data: Dict) -> bytes:
        """
        Export data as JSON
        """
        return json.dumps(data, indent=2).encode('utf-8')

    def _export_csv(self, data: Dict) -> bytes:
        """
        Export data as CSV
        """
        if isinstance(data, dict):
            data = [data]

        keys = set()
        for item in data:
            keys.update(item["metadata"].keys())
            keys.update(item["content"].keys())
            keys.update(item["analysis"].keys())

        csv_data = []
        for item in data:
            row = {}
            row.update(item["metadata"])
            row.update({f"content_{k}": v for k, v in item["content"].items()})
            row.update({f"analysis_{k}": v for k, v in item["analysis"].items()})
            csv_data.append(row)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=sorted(keys))
        writer.writeheader()
        writer.writerows(csv_data)
        return output.getvalue().encode('utf-8')

    def _export_xlsx(self, data: Dict) -> bytes:
        """
        Export data as Excel
        """
        if isinstance(data, dict):
            data = [data]

        wb = Workbook()
        ws = wb.active

        # Write header
        headers = []
        for item in data:
            headers.extend(item["metadata"].keys())
            headers.extend(f"content_{k}" for k in item["content"].keys())
            headers.extend(f"analysis_{k}" for k in item["analysis"].keys())
        headers = sorted(set(headers))
        ws.append(headers)

        # Write data
        for item in data:
            row = {}
            row.update(item["metadata"])
            row.update({f"content_{k}": v for k, v in item["content"].items()})
            row.update({f"analysis_{k}": v for k, v in item["analysis"].items()})
            ws.append([row.get(header, "") for header in headers])

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    def _export_xml(self, data: Dict) -> bytes:
        """
        Export data as XML
        """
        if isinstance(data, dict):
            data = [data]

        root = ET.Element("documents")
        for item in data:
            doc = ET.SubElement(root, "document")
            
            metadata = ET.SubElement(doc, "metadata")
            for key, value in item["metadata"].items():
                ET.SubElement(metadata, key).text = str(value)
            
            content = ET.SubElement(doc, "content")
            for key, value in item["content"].items():
                ET.SubElement(content, key).text = str(value)
            
            analysis = ET.SubElement(doc, "analysis")
            for key, value in item["analysis"].items():
                ET.SubElement(analysis, key).text = str(value)

        return ET.tostring(root, encoding='utf-8', method='xml')
