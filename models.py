from app import db
from datetime import datetime
from sqlalchemy import Text, Integer, String, DateTime, Boolean

class Document(db.Model):
    id = db.Column(Integer, primary_key=True)
    filename = db.Column(String(255), nullable=False)
    original_filename = db.Column(String(255), nullable=False)
    file_path = db.Column(String(500), nullable=False)
    file_type = db.Column(String(10), nullable=False)
    upload_date = db.Column(DateTime, default=datetime.utcnow)
    summary = db.Column(Text)
    content = db.Column(Text)
    processed = db.Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<Document {self.filename}>'

class Question(db.Model):
    id = db.Column(Integer, primary_key=True)
    document_id = db.Column(Integer, db.ForeignKey('document.id'), nullable=False)
    question_text = db.Column(Text, nullable=False)
    question_type = db.Column(String(50), nullable=False)  # 'user' or 'challenge'
    answer = db.Column(Text)
    justification = db.Column(Text)
    source_reference = db.Column(Text)
    created_date = db.Column(DateTime, default=datetime.utcnow)
    
    document = db.relationship('Document', backref=db.backref('questions', lazy=True))
    
    def __repr__(self):
        return f'<Question {self.id}>'

class ChatSession(db.Model):
    id = db.Column(Integer, primary_key=True)
    document_id = db.Column(Integer, db.ForeignKey('document.id'), nullable=False)
    session_id = db.Column(String(100), nullable=False)
    created_date = db.Column(DateTime, default=datetime.utcnow)
    
    document = db.relationship('Document', backref=db.backref('chat_sessions', lazy=True))
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'
