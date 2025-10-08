from database import db
from datetime import datetime

class Inspection(db.Model):
    """Modelo para uma inspeção."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.relationship('Answer', backref='inspection', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Inspection {self.title}>'

class Question(db.Model):
    """Modelo para uma pergunta da auditoria."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    weight = db.Column(db.Float, nullable=False, default=1.0)

    def __repr__(self):
        return f'<Question {self.text}>'

class Answer(db.Model):
    """Modelo para uma resposta a uma pergunta em uma inspeção."""
    id = db.Column(db.Integer, primary_key=True)
    response = db.Column(db.String(50), nullable=False)  # e.g., 'Conforme', 'Não Conforme', 'N/A'
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.relationship('Question', backref='answers')
    photos = db.relationship('Photo', backref='answer', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Answer {self.id}>'

class Photo(db.Model):
    """Modelo para uma foto de evidência."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)

    def __repr__(self):
        return f'<Photo {self.filename}>'