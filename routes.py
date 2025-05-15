from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import json
from datetime import datetime, timedelta

from app import db, login_manager
from models import Users, ChatHistory, Cases, CaseAttempt
from models import Challenges, ChallengeAttempt, Flashcards, FlashcardProgress, Achievements, UserAchievement

# Setup user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))

def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Render the home page"""
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = Users.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            
            flash('Invalid username or password', 'danger')
            
        return render_template('login.html')
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """Handle user registration"""
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Check if user already exists
            existing_user = Users.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'danger')
                return render_template('signup.html')
            
            existing_email = Users.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already registered', 'danger')
                return render_template('signup.html')
            
            # Create new user
            new_user = Users(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Add 'First Login' achievement
            first_login_achievement = Achievements.query.filter_by(name='First Login').first()
            if first_login_achievement:
                user_achievement = UserAchievement(
                    user_id=new_user.id,
                    achievement_id=first_login_achievement.id
                )
                new_user.points += first_login_achievement.points
                db.session.add(user_achievement)
                db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
            
        return render_template('signup.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Handle user logout"""
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Render user dashboard"""
        # Get user achievements
        user_achievements = db.session.query(
            Achievements
        ).join(
            UserAchievement, UserAchievement.achievement_id == Achievements.id
        ).filter(
            UserAchievement.user_id == current_user.id
        ).all()
        
        # Get stats
        case_attempts = CaseAttempt.query.filter_by(user_id=current_user.id).count()
        challenge_attempts = ChallengeAttempt.query.filter_by(user_id=current_user.id).count()
        flashcard_count = db.session.query(FlashcardProgress).filter_by(user_id=current_user.id).count()
        
        return render_template(
            'dashboard.html', 
            user=current_user,
            achievements=user_achievements,
            case_attempts=case_attempts,
            challenge_attempts=challenge_attempts,
            flashcard_count=flashcard_count
        )
    
    @app.route('/chat')
    def chat():
        """Render chat page"""
        return render_template('chat.html')
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        """Handle chat API requests"""
        data = request.json
        query = data.get('query', '')
        
        # Get user ID if logged in
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Import AI service here to avoid circular imports
        from ai_service import get_diagnosis_response
        
        # Get AI response
        response = get_diagnosis_response(query)
        
        # Save chat history if user is logged in
        if user_id:
            # Update user streak
            update_user_streak(user_id)
            
            # Add chat to history
            chat_history = ChatHistory(
                user_id=user_id,
                query=query,
                response=response
            )
            db.session.add(chat_history)
            db.session.commit()
        
        return jsonify({"response": response})
    
    @app.route('/simulation')
    def simulation():
        """Render case simulation page"""
        return render_template('simulation.html')
    
    @app.route('/api/generate_simulation', methods=['GET'])
    def api_generate_simulation():
        """Generate a new case simulation"""
        # Import AI service here to avoid circular imports
        from ai_service import generate_case_simulation
        
        case = generate_case_simulation()
        
        # Store the generated case in session
        session['current_case'] = case
        
        # Return the case without the answers
        return jsonify({
            "patient_age": case.get("patient_age"),
            "patient_gender": case.get("patient_gender"),
            "symptoms": case.get("symptoms"),
            "medical_history": case.get("medical_history")
        })
    
    @app.route('/api/submit_simulation', methods=['POST'])
    def api_submit_simulation():
        """Submit a simulation answer for evaluation"""
        data = request.json
        answers = data.get('answers', {})
        
        current_case = session.get('current_case', {})
        if not current_case:
            return jsonify({"error": "No active case found"}), 400
        
        # Evaluate diagnosis
        diagnosis_key_terms = re.findall(r'\b\w{4,}\b', current_case.get('diagnosis', '').lower())
        user_diagnosis_lower = answers.get('diagnosis', '').lower()
        matched_terms = sum(1 for term in diagnosis_key_terms if term in user_diagnosis_lower)
        
        # Calculate diagnosis score
        if matched_terms == len(diagnosis_key_terms) or user_diagnosis_lower == current_case.get('diagnosis', '').lower():
            # Exact match or all key terms present
            diagnosis_score = 100
            diagnosis_feedback = "Excellent! Your diagnosis is correct."
        elif matched_terms >= len(diagnosis_key_terms) * 0.7:
            # Most key terms are present
            diagnosis_score = 80
            diagnosis_feedback = "Good job! Your diagnosis is mostly correct."
        elif matched_terms >= len(diagnosis_key_terms) * 0.4:
            # Some key terms are present
            diagnosis_score = 60
            diagnosis_feedback = "Your diagnosis is partially correct, but missing some key elements."
        elif matched_terms > 0:
            # Few terms are present
            diagnosis_score = 40
            diagnosis_feedback = "Your diagnosis has some correct elements, but is mostly off."
        else:
            # No matches
            diagnosis_score = 0
            diagnosis_feedback = "Your diagnosis does not match the expected answer."
        
        # Evaluate treatment (similar approach)
        treatment_key_terms = re.findall(r'\b\w{4,}\b', current_case.get('treatment', '').lower())
        user_treatment_lower = answers.get('treatment', '').lower()
        
        # Handle API error case
        if "Error connecting to AI service" in current_case.get('treatment', ''):
            treatment_score = 80
            treatment_feedback = "Treatment evaluation unavailable. You've been given a generous score."
        else:
            matched_terms = sum(1 for term in treatment_key_terms if term in user_treatment_lower)
            
            # Calculate treatment score
            if matched_terms == len(treatment_key_terms) or user_treatment_lower == current_case.get('treatment', '').lower():
                treatment_score = 100
                treatment_feedback = "Excellent! Your treatment plan is correct."
            elif matched_terms >= len(treatment_key_terms) * 0.7:
                treatment_score = 80
                treatment_feedback = "Good job! Your treatment plan is mostly correct."
            elif matched_terms >= len(treatment_key_terms) * 0.4:
                treatment_score = 60
                treatment_feedback = "Your treatment plan is partially correct, but missing key elements."
            elif matched_terms > 0:
                treatment_score = 40
                treatment_feedback = "Your treatment plan has some correct elements, but is mostly off."
            else:
                treatment_score = 0
                treatment_feedback = "Your treatment plan does not match the expected approach."
        
        # Calculate overall score
        overall_score = (diagnosis_score + treatment_score) / 2
        
        # Save the attempt if user is logged in
        if current_user.is_authenticated:
            # First save the case if it's not already in the database
            case_title = f"Case: {current_case.get('symptoms', '')[:50]}..."
            existing_case = Cases.query.filter_by(title=case_title).first()
            
            if not existing_case:
                new_case = Cases(
                    title=case_title,
                    description=current_case.get('symptoms', ''),
                    patient_age=current_case.get('patient_age'),
                    patient_gender=current_case.get('patient_gender'),
                    symptoms=current_case.get('symptoms', ''),
                    medical_history=current_case.get('medical_history', ''),
                    diagnosis=current_case.get('diagnosis', ''),
                    treatment=current_case.get('treatment', '')
                )
                db.session.add(new_case)
                db.session.commit()
                case_id = new_case.id
            else:
                case_id = existing_case.id
            
            # Save the attempt
            attempt = CaseAttempt(
                user_id=current_user.id,
                case_id=case_id,
                diagnosis=answers.get('diagnosis', ''),
                treatment=answers.get('treatment', ''),
                score=overall_score,
                feedback=f"Diagnosis: {diagnosis_feedback} Treatment: {treatment_feedback}"
            )
            db.session.add(attempt)
            
            # Update user points
            current_user.points += int(overall_score / 10)
            
            # Update user streak
            update_user_streak(current_user.id)
            
            # Check for achievement: "Diagnosis Expert"
            if CaseAttempt.query.filter_by(user_id=current_user.id).count() >= 5:
                diagnosis_expert = Achievements.query.filter_by(name='Diagnosis Expert').first()
                if diagnosis_expert and not UserAchievement.query.filter_by(
                    user_id=current_user.id, 
                    achievement_id=diagnosis_expert.id
                ).first():
                    user_achievement = UserAchievement(
                        user_id=current_user.id,
                        achievement_id=diagnosis_expert.id
                    )
                    current_user.points += diagnosis_expert.points
                    db.session.add(user_achievement)
            
            db.session.commit()
        
        # Return the evaluation results
        return jsonify({
            "diagnosis_score": diagnosis_score,
            "diagnosis_feedback": diagnosis_feedback,
            "treatment_score": treatment_score,
            "treatment_feedback": treatment_feedback,
            "overall_score": overall_score,
            "correct_diagnosis": current_case.get('diagnosis', ''),
            "correct_treatment": current_case.get('treatment', '')
        })
    
    # Helper functions
    def update_user_streak(user_id):
        """Update the user's streak count"""
        user = Users.query.get(user_id)
        if not user:
            return
        
        now = datetime.utcnow()
        
        # If last streak date is yesterday or today, update streak
        if user.last_streak_date:
            date_diff = (now - user.last_streak_date).days
            
            if date_diff == 0:
                # Already updated today, do nothing
                pass
            elif date_diff == 1:
                # Consecutive day, increment streak
                user.streak_count += 1
                user.last_streak_date = now
                
                # Check for streak achievements
                check_streak_achievements(user)
            elif date_diff > 1:
                # Streak broken, reset
                user.streak_count = 1
                user.last_streak_date = now
        else:
            # First time, set streak to 1
            user.streak_count = 1
            user.last_streak_date = now
        
        db.session.commit()
    
    def check_streak_achievements(user):
        """Check and award streak-based achievements"""
        # Streak Starter (3-day streak)
        if user.streak_count >= 3:
            streak_starter = Achievements.query.filter_by(name='Streak Starter').first()
            if streak_starter and not UserAchievement.query.filter_by(
                user_id=user.id, 
                achievement_id=streak_starter.id
            ).first():
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=streak_starter.id
                )
                user.points += streak_starter.points
                db.session.add(user_achievement)
        
        # Consistent Learner (7-day streak)
        if user.streak_count >= 7:
            consistent_learner = Achievements.query.filter_by(name='Consistent Learner').first()
            if consistent_learner and not UserAchievement.query.filter_by(
                user_id=user.id, 
                achievement_id=consistent_learner.id
            ).first():
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=consistent_learner.id
                )
                user.points += consistent_learner.points
                db.session.add(user_achievement)
        
        db.session.commit()
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500