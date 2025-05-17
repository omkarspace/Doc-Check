from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk import init
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from app.config import settings
import logging
import time
from typing import Dict, Any
from datetime import datetime

class Monitoring:
    def __init__(self):
        # Prometheus Metrics
        self.DOCUMENTS_PROCESSED = Counter(
            'documents_processed_total',
            'Total number of documents processed',
            ['document_type', 'status', 'environment']
        )

        self.PROCESSING_TIME = Histogram(
            'document_processing_seconds',
            'Time taken to process documents',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            labelnames=['document_type', 'environment']
        )

        self.ERRORS = Counter(
            'document_processing_errors_total',
            'Total number of processing errors',
            ['error_type', 'environment']
        )

        self.ACTIVE_REQUESTS = Gauge(
            'document_processing_active_requests',
            'Number of active document processing requests',
            ['environment']
        )

        # Initialize Prometheus instrumentator
        self.instrumentator = Instrumentator()
        
        # Initialize Sentry for error tracking if DSN is provided
        if settings.SENTRY_DSN and settings.SENTRY_DSN != "your-sentry-dsn-here":
            init(
                dsn=settings.SENTRY_DSN,
                traces_sample_rate=1.0,
                environment=settings.ENVIRONMENT,
                integrations=[SentryAsgiMiddleware],
                release=settings.VERSION
            )
            self.sentry_enabled = True
        else:
            self.sentry_enabled = False
            logging.warning("Sentry DSN not configured. Error tracking will be limited to logs.")

    def setup_metrics(self, app):
        """Setup Prometheus metrics for the FastAPI app"""
        self.instrumentator.add(
            Instrumentator().instrument(app)
        )
        self.instrumentator.expose(app)

    def setup_sentry(self, app):
        """Setup Sentry for error tracking if enabled"""
        if self.sentry_enabled:
            return SentryAsgiMiddleware(app)
        return app

    def track_document_processing(self, document_type: str, status: str, processing_time: float):
        """Track document processing metrics"""
        self.ACTIVE_REQUESTS.labels(environment=settings.ENVIRONMENT).dec()
        self.DOCUMENTS_PROCESSED.labels(
            document_type=document_type,
            status=status,
            environment=settings.ENVIRONMENT
        ).inc()
        
        self.PROCESSING_TIME.labels(
            document_type=document_type,
            environment=settings.ENVIRONMENT
        ).observe(processing_time)

    def track_error(self, error_type: str, document_type: str):
        """Track processing errors"""
        self.ERRORS.labels(
            error_type=error_type,
            environment=settings.ENVIRONMENT
        ).inc()
        
        # Send to Sentry
        self._send_to_sentry(error_type, document_type)

    def track_active_request(self):
        """Track active requests"""
        self.ACTIVE_REQUESTS.labels(environment=settings.ENVIRONMENT).inc()

    def _send_to_sentry(self, error_type: str, document_type: str):
        """Send error to Sentry"""
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_type", error_type)
            scope.set_tag("document_type", document_type)
            scope.set_tag("environment", settings.ENVIRONMENT)
            sentry_sdk.capture_exception()

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
