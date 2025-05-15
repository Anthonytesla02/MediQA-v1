from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app import db

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    streak_count = Column(Integer, default=0)
    last_streak_date = Column(DateTime, default=datetime.utcnow)
    points = Column(Integer, default=0)
    
    # Relationships
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    case_attempts = relationship("CaseAttempt", back_populates="user", cascade="all, delete-orphan")
    challenge_attempts = relationship("ChallengeAttempt", back_populates="user", cascade="all, delete-orphan")
    flashcard_progress = relationship("FlashcardProgress", back_populates="user", cascade="all, delete-orphan")
    user_achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    
    def get_id(self):
        return str(self.id)

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("Users", back_populates="chat_history")

class Cases(db.Model):
    __tablename__ = 'cases'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    patient_age = Column(Integer)
    patient_gender = Column(String(10))
    symptoms = Column(Text)
    medical_history = Column(Text)
    diagnosis = Column(Text, nullable=False)
    treatment = Column(Text, nullable=False)
    difficulty = Column(String(20), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = relationship("CaseAttempt", back_populates="case", cascade="all, delete-orphan")

class CaseAttempt(db.Model):
    __tablename__ = 'case_attempt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    case_id = Column(Integer, ForeignKey('cases.id', ondelete="CASCADE"), nullable=False)
    diagnosis = Column(Text)
    treatment = Column(Text)
    score = Column(Float)
    feedback = Column(Text)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("Users", back_populates="case_attempts")
    case = relationship("Cases", back_populates="attempts")

class Challenges(db.Model):
    __tablename__ = 'challenges'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # Stored as JSON
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text)
    difficulty = Column(String(20), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = relationship("ChallengeAttempt", back_populates="challenge", cascade="all, delete-orphan")

class ChallengeAttempt(db.Model):
    __tablename__ = 'challenge_attempt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey('challenges.id', ondelete="CASCADE"), nullable=False)
    answer = Column(String(1))
    is_correct = Column(Boolean)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("Users", back_populates="challenge_attempts")
    challenge = relationship("Challenges", back_populates="attempts")

class Flashcards(db.Model):
    __tablename__ = 'flashcards'
    id = Column(Integer, primary_key=True)
    topic = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    progress = relationship("FlashcardProgress", back_populates="flashcard", cascade="all, delete-orphan")

class FlashcardProgress(db.Model):
    __tablename__ = 'flashcard_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    flashcard_id = Column(Integer, ForeignKey('flashcards.id', ondelete="CASCADE"), nullable=False)
    familiarity = Column(Integer, default=0)  # 0-5 scale
    last_reviewed = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("Users", back_populates="flashcard_progress")
    flashcard = relationship("Flashcards", back_populates="progress")

class Achievements(db.Model):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    badge_icon = Column(String(50))
    points = Column(Integer, default=0)
    
    # Relationships
    users = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

class UserAchievement(db.Model):
    __tablename__ = 'user_achievement'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id', ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("Users", back_populates="user_achievements")
    achievement = relationship("Achievements", back_populates="users")