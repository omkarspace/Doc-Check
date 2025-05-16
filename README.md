# DocuGenie - Intelligent Document Processing for BFSI

An AI-powered document processing platform for BFSI institutions that automates the extraction, classification, and summarization of unstructured data from various document types.

## Features

- Multi-format document upload (PDF, DOCX, JPG/PNG)
- AI-powered document parsing and OCR
- Named Entity Recognition and Summarization
- Document classification
- Secure data export in multiple formats
- Role-based access control
- Integration with multiple AI models

## Tech Stack

- Backend: FastAPI
- AI/ML: OpenAI, Tesseract OCR
- Database: PostgreSQL + MongoDB
- Storage: AWS S3
- Security: JWT, OAuth2

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Swagger UI: http://localhost:8000/docs

## Security

- All data is encrypted at rest and in transit
- PII redaction implemented
- Role-based access control
- Audit trails for all operations

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.
