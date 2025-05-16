from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics
    """
    # TODO: Replace with actual database queries
    return {
        "total_documents": 245,
        "processed_today": 48,
        "success_rate": 98.5,
        "processing_time": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "data": [2.5, 3.2, 2.8, 3.5, 2.9, 3.1]
        },
        "document_types": {
            "labels": ["PDF", "Word", "Images", "Other"],
            "data": [45, 30, 15, 10]
        }
    }

@router.get("/dashboard/recent-activity")
async def get_recent_activity():
    """
    Get recent document processing activity
    """
    # TODO: Replace with actual database queries
    return [
        {
            "id": 1,
            "document_name": "Annual Report 2023.pdf",
            "status": "processed",
            "processed_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "processing_time": 2.8
        },
        {
            "id": 2,
            "document_name": "Invoice 12345.docx",
            "status": "processing",
            "processed_at": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "processing_time": 3.2
        }
    ]
