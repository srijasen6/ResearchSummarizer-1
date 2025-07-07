# AI Research Assistant

## Overview

The AI Research Assistant is a Flask-based web application that provides intelligent document analysis, summarization, and Q&A capabilities. It leverages local CPU-friendly AI models to offer document-grounded responses without requiring GPU resources. The application supports PDF and TXT document uploads and provides two interaction modes: free-form Q&A and AI-generated challenge questions.

## System Architecture

### Backend Architecture
- **Flask Web Framework**: Python-based web server handling HTTP requests and responses
- **SQLAlchemy ORM**: Database abstraction layer for managing document and question data
- **Modular Service Layer**: Separated concerns across multiple services:
  - Document processing and text extraction
  - AI inference and question answering
  - Vector storage and similarity search
  - Database operations

### Frontend Architecture
- **Server-side Rendered Templates**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Progressive Enhancement**: JavaScript for dynamic interactions and AJAX calls
- **Modern Web Standards**: HTML5, CSS3, and ES6+ JavaScript features

### Data Storage
- **SQLite Database**: Default lightweight database for development
- **PostgreSQL Support**: Configurable via environment variables for production
- **File Storage**: Local filesystem for uploaded documents
- **Vector Cache**: FAISS indices stored on disk for document embeddings

## Key Components

### Document Processing Pipeline
1. **File Upload**: Secure file handling with type validation and size limits (16MB)
2. **Text Extraction**: PDF parsing via PyPDF2 and TXT file reading
3. **Text Chunking**: Document segmentation for better context retrieval
4. **Embedding Generation**: Sentence transformers for semantic search
5. **Vector Indexing**: FAISS for efficient similarity search

### AI Service Layer
- **Local LLM**: CPU-optimized quantized models (GGUF format)
- **Embedding Model**: all-MiniLM-L6-v2 for lightweight semantic understanding
- **Fallback Responses**: Graceful degradation when models are unavailable
- **Context-aware Processing**: Document-grounded responses with source attribution

### Database Schema
- **Document**: Stores file metadata, content, and processing status
- **Question**: Tracks user queries, AI responses, and justifications
- **ChatSession**: Manages conversation context and follow-up questions

## Data Flow

1. **Document Upload**: User uploads PDF/TXT → File validation → Secure storage
2. **Text Processing**: Content extraction → Text cleaning → Chunking → Embedding generation
3. **Vector Storage**: Embeddings → FAISS index creation → Disk persistence
4. **Query Processing**: User question → Similarity search → Context retrieval → AI response
5. **Response Generation**: Context + Question → LLM inference → Grounded answer + justification

## External Dependencies

### AI Models
- **llama-cpp-python**: Local LLM inference without GPU requirements
- **sentence-transformers**: Lightweight embedding models
- **FAISS**: Facebook's vector similarity search library

### Document Processing
- **PyPDF2**: PDF text extraction
- **Werkzeug**: Secure file handling utilities

### Web Framework
- **Flask**: Core web framework
- **SQLAlchemy**: Database ORM
- **Bootstrap 5**: Frontend CSS framework

## Deployment Strategy

### Local Development
- SQLite database for simplicity
- Local file storage in uploads directory
- Development server with debug mode
- Automatic model downloading and caching

### Production Considerations
- PostgreSQL database via DATABASE_URL environment variable
- ProxyFix middleware for reverse proxy deployment
- Session management with configurable secret keys
- Connection pooling and database optimization

## Changelog
- July 07, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.