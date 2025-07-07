import os
import uuid
import logging
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from app import app, db
from models import Document, Question, ChatSession
from services.document_processor import DocumentProcessor
from services.ai_service import AIService
from services.vector_store import VectorStore

# Initialize services
document_processor = DocumentProcessor()
ai_service = AIService()
vector_store = VectorStore()

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF or TXT files.'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Process document
        content = document_processor.extract_text(file_path, filename.split('.')[-1])
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_type=filename.split('.')[-1].lower(),
            content=content
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Generate summary
        summary = ai_service.generate_summary(content)
        document.summary = summary
        document.processed = True
        db.session.commit()
        
        # Create vector embeddings
        vector_store.create_embeddings(document.id, content)
        
        # Create chat session
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            document_id=document.id,
            session_id=session_id
        )
        db.session.add(chat_session)
        db.session.commit()
        
        session['current_document_id'] = document.id
        session['current_session_id'] = session_id
        
        return jsonify({
            'success': True,
            'document_id': document.id,
            'session_id': session_id,
            'summary': summary,
            'filename': filename
        })
        
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': f'Failed to process document: {str(e)}'}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle free-form questions"""
    try:
        data = request.json
        question = data.get('question', '').strip()
        document_id = data.get('document_id') or session.get('current_document_id')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not document_id:
            return jsonify({'error': 'No document selected'}), 400
        
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Get relevant context from vector store
        relevant_chunks = vector_store.search_similar(document_id, question, k=3)
        
        # Generate answer
        answer_data = ai_service.answer_question(question, relevant_chunks, document.content)
        
        # Save question and answer
        question_record = Question(
            document_id=document_id,
            question_text=question,
            question_type='user',
            answer=answer_data['answer'],
            justification=answer_data['justification'],
            source_reference=answer_data['source_reference']
        )
        
        db.session.add(question_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'answer': answer_data['answer'],
            'justification': answer_data['justification'],
            'source_reference': answer_data['source_reference']
        })
        
    except Exception as e:
        logging.error(f"Error answering question: {str(e)}")
        return jsonify({'error': f'Failed to answer question: {str(e)}'}), 500

@app.route('/challenge', methods=['POST'])
def generate_challenge():
    """Generate challenge questions"""
    try:
        data = request.json
        document_id = data.get('document_id') or session.get('current_document_id')
        
        if not document_id:
            return jsonify({'error': 'No document selected'}), 400
        
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Generate challenge questions
        questions = ai_service.generate_challenge_questions(document.content)
        
        # Save challenge questions
        challenge_records = []
        for q in questions:
            question_record = Question(
                document_id=document_id,
                question_text=q['question'],
                question_type='challenge',
                answer=q['expected_answer'],
                justification=q['justification'],
                source_reference=q['source_reference']
            )
            db.session.add(question_record)
            challenge_records.append(question_record)
        
        db.session.commit()
        
        # Return questions without answers
        challenge_questions = [
            {
                'id': q.id,
                'question': q.question_text
            }
            for q in challenge_records
        ]
        
        return jsonify({
            'success': True,
            'questions': challenge_questions
        })
        
    except Exception as e:
        logging.error(f"Error generating challenge: {str(e)}")
        return jsonify({'error': f'Failed to generate challenge: {str(e)}'}), 500

@app.route('/evaluate', methods=['POST'])
def evaluate_answer():
    """Evaluate user's answer to challenge question"""
    try:
        data = request.json
        question_id = data.get('question_id')
        user_answer = data.get('answer', '').strip()
        
        if not question_id or not user_answer:
            return jsonify({'error': 'Question ID and answer are required'}), 400
        
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Evaluate the answer
        evaluation = ai_service.evaluate_answer(
            question.question_text,
            user_answer,
            question.answer,
            question.justification
        )
        
        return jsonify({
            'success': True,
            'evaluation': evaluation,
            'correct_answer': question.answer,
            'justification': question.justification,
            'source_reference': question.source_reference
        })
        
    except Exception as e:
        logging.error(f"Error evaluating answer: {str(e)}")
        return jsonify({'error': f'Failed to evaluate answer: {str(e)}'}), 500

@app.route('/document/<int:document_id>')
def view_document(document_id):
    """View document analysis page"""
    document = Document.query.get_or_404(document_id)
    session['current_document_id'] = document_id
    return render_template('document_analysis.html', document=document)

@app.route('/api/documents')
def get_documents():
    """Get all uploaded documents"""
    documents = Document.query.order_by(Document.upload_date.desc()).all()
    return jsonify([
        {
            'id': doc.id,
            'filename': doc.original_filename,
            'upload_date': doc.upload_date.isoformat(),
            'processed': doc.processed,
            'summary': doc.summary[:100] + '...' if doc.summary and len(doc.summary) > 100 else doc.summary
        }
        for doc in documents
    ])

@app.route('/api/document/<int:document_id>/history')
def get_document_history(document_id):
    """Get question history for a document"""
    questions = Question.query.filter_by(document_id=document_id).order_by(Question.created_date.desc()).all()
    return jsonify([
        {
            'id': q.id,
            'question': q.question_text,
            'answer': q.answer,
            'justification': q.justification,
            'source_reference': q.source_reference,
            'type': q.question_type,
            'created_date': q.created_date.isoformat()
        }
        for q in questions
    ])

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500
