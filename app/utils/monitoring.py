from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk import init
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from app.config import settings
import logging
import time
from typing import Dict, Any

class Monitoring:
    def __init__(self):
        # Initialize Prometheus metrics
        self.instrumentator = Instrumentator()
        
        # Initialize Sentry for error tracking
        init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=1.0,
            environment=settings.ENVIRONMENT
        )

    def setup_metrics(self, app):
        """Setup Prometheus metrics for the FastAPI app"""
        self.instrumentator.add(
            Instrumentator().instrument(app)
        )
        self.instrumentator.expose(app)

    def setup_sentry(self, app):
        """Setup Sentry error tracking"""
        return SentryAsgiMiddleware(app)

    def track_request(self, endpoint: str, status_code: int, duration: float):
        """Track request metrics"""
        logging.info(
            f"Request completed - endpoint: {endpoint}, status: {status_code}, duration: {duration}s"
        )

class Analytics:
    def __init__(self):
        self.processing_times = []
        self.success_count = 0
        self.error_count = 0
        self.total_requests = 0

    def track_document_processing(self, document_type: str, processing_time: float, success: bool):
        """Track document processing metrics"""
        self.processing_times.append(processing_time)
        self.total_requests += 1
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        if not self.processing_times:
            return {
                "total_requests": 0,
                "success_rate": 0,
                "average_processing_time": 0,
                "error_rate": 0
            }

        avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        success_rate = (self.success_count / self.total_requests) * 100
        error_rate = (self.error_count / self.total_requests) * 100

        return {
            "total_requests": self.total_requests,
            "success_rate": success_rate,
            "average_processing_time": avg_processing_time,
            "error_rate": error_rate
        }

def setup_monitoring(app):
    """Setup monitoring for the application"""
    monitoring = Monitoring()
    app = monitoring.setup_sentry(app)
    monitoring.setup_metrics(app)
    return app
