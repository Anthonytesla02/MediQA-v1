from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Rename table to avoid SQL reserved keyword
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_histories = db.relationship('ChatHistory', backref='user', lazy=True, cascade="all, delete-orphan")
    case_attempts = db.relationship('CaseAttempt', backref='user', lazy=True, cascade="all, delete-orphan")
    challenge_attempts = db.relationship('ChallengeAttempt', backref='user', lazy=True, cascade="all, delete-orphan")
    flashcard_progresses = db.relationship('FlashcardProgress', backref='user', lazy=True, cascade="all, delete-orphan")
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade="all, delete-orphan")

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    messages = db.Column(db.Text, nullable=False)  # Stored as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Case(db.Model):
    __tablename__ = 'cases'  # Rename table to avoid SQL reserved keyword
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)  # Stored as JSON
    diagnosis = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('CaseAttempt', backref='case', lazy=True, cascade="all, delete-orphan")

class CaseAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer, default=0)  # in seconds
    diagnosis = db.Column(db.Text)  # Changed from String(120) to Text for longer answers
    correct = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Challenge(db.Model):
    __tablename__ = 'challenges'  # Rename table to avoid SQL reserved keyword
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)  # Stored as JSON
    points = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    attempts = db.relationship('ChallengeAttempt', backref='challenge', lazy=True, cascade="all, delete-orphan")

class ChallengeAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Flashcard(db.Model):
    __tablename__ = 'flashcards'  # Rename table to avoid SQL reserved keyword
    
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    progresses = db.relationship('FlashcardProgress', backref='flashcard', lazy=True, cascade="all, delete-orphan")

class FlashcardProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.id', ondelete='CASCADE'), nullable=False)
    ease_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=1)  # in days
    next_review = db.Column(db.DateTime)
    last_reviewed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    __tablename__ = 'achievements'  # Rename table to avoid SQL reserved keyword
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    badge_icon = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=10)
    
    # Relationships
    users = db.relationship('UserAchievement', backref='achievement', lazy=True, cascade="all, delete-orphan")

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
