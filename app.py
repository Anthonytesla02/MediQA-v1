import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    """Initialize the core application"""
    app = Flask(__name__)
    
    # Setup configuration
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from models import Users, ChatHistory, Cases, CaseAttempt, Challenges
        from models import ChallengeAttempt, Flashcards, FlashcardProgress, Achievements, UserAchievement
        
        # Create database tables if they don't exist
        db.create_all()
        
        # Initialize default data
        init_achievements()
        
        # Import routes
        from routes import register_routes
        register_routes(app)
        
        return app

def init_achievements():
    """Initialize default achievements if they don't exist."""
    from models import Achievements
    
    # Check if achievements table is empty
    if db.session.query(Achievements).count() == 0:
        default_achievements = [
            {
                'name': 'First Login',
                'description': 'Logged in for the first time',
                'badge_icon': 'award',
                'points': 5
            },
            {
                'name': 'Streak Starter',
                'description': 'Maintained a 3-day streak',
                'badge_icon': 'calendar',
                'points': 10
            },
            {
                'name': 'Consistent Learner',
                'description': 'Maintained a 7-day streak',
                'badge_icon': 'calendar-check',
                'points': 25
            },
            {
                'name': 'Diagnosis Expert',
                'description': 'Correctly diagnosed 5 cases',
                'badge_icon': 'clipboard-check',
                'points': 25
            },
            {
                'name': 'Knowledge Seeker',
                'description': 'Reviewed 10 flashcards',
                'badge_icon': 'book-open',
                'points': 15
            },
            {
                'name': 'Quiz Master',
                'description': 'Completed 3 daily challenges',
                'badge_icon': 'clipboard-pulse',
                'points': 20
            }
        ]
        
        for achievement_data in default_achievements:
            achievement = Achievements(**achievement_data)
            db.session.add(achievement)
        
        db.session.commit()
        print("Default achievements initialized")