import os
import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
def create_app():
    app = Flask(__name__)
    
    # Setup secret key, required by sessions
    app.secret_key = os.environ.get("SESSION_SECRET")
    
    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    return app

# Create the Flask application
app = create_app()


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


def background_initialization():
    """Initialize components that can run in the background."""
    try:
        from document_processor import initialize_document_processor
        from rag_engine import initialize_rag_engine
        
        # Initialize document processor
        initialize_document_processor()
        
        # Initialize RAG engine with processed document
        initialize_rag_engine()
        
        print("Background initialization completed")
    except Exception as e:
        print(f"Error in background initialization: {str(e)}")


def auto_initialize():
    """Run all initialization tasks."""
    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        import models
        
        # Create all tables if they don't exist
        db.create_all()
        
        # Initialize achievements
        init_achievements()
        
        # Create a flag file to indicate initialization is complete
        with open(".app_initialized", "w") as f:
            f.write("App initialized successfully")
        
        print("Database initialization complete")
    
    # Start background initialization in a separate thread
    threading.Thread(target=background_initialization, daemon=True).start()


# Import routes after app is created to avoid circular imports
from routes import *

if __name__ == "__main__":
    # Check if the app has been initialized
    if not os.path.exists(".app_initialized"):
        auto_initialize()
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)