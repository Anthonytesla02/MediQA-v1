import logging
from datetime import datetime, timedelta
from app import db
from models import User, Achievement, UserAchievement
from config import DAILY_STREAK_POINTS

logger = logging.getLogger(__name__)

def update_user_streak(user_id):
    """Update a user's streak if they've been active recently."""
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            return False
        
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        
        # Check if the user was last active yesterday or today
        if user.last_active is None or user.last_active.date() < yesterday.date():
            # Reset streak if more than 1 day has passed
            if user.last_active is None or user.last_active.date() < (now - timedelta(days=2)).date():
                user.streak = 1
            else:
                # Increment streak if exactly 1 day has passed
                user.streak += 1
                
            # Award streak points
            user.points += DAILY_STREAK_POINTS
            
            # Check for streak achievements
            check_streak_achievements(user)
        
        # Update last active time
        user.last_active = now
        db.session.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error updating user streak: {e}")
        db.session.rollback()
        return False

def add_points(user_id, points):
    """Add points to a user's account."""
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            return False
        
        user.points += points
        db.session.commit()
        
        # Check for point-based achievements
        check_point_achievements(user)
        
        return True
    except Exception as e:
        logger.error(f"Error adding points: {e}")
        db.session.rollback()
        return False

def award_achievement(user_id, achievement_id):
    """Award an achievement to a user."""
    try:
        # Check if user already has this achievement
        existing = UserAchievement.query.filter_by(
            user_id=user_id, 
            achievement_id=achievement_id
        ).first()
        
        if existing:
            return False
        
        # Create new achievement
        new_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            earned_at=datetime.utcnow()
        )
        
        # Add points from achievement
        achievement = Achievement.query.get(achievement_id)
        if achievement:
            user = User.query.get(user_id)
            if user:
                user.points += achievement.points
        
        db.session.add(new_achievement)
        db.session.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error awarding achievement: {e}")
        db.session.rollback()
        return False

def check_streak_achievements(user):
    """Check if a user has earned any streak-based achievements."""
    streak_achievements = {
        3: 1,   # 3-day streak (achievement ID 1)
        7: 2,   # 7-day streak (achievement ID 2)
        30: 3,  # 30-day streak (achievement ID 3)
        100: 4  # 100-day streak (achievement ID 4)
    }
    
    for streak_days, achievement_id in streak_achievements.items():
        if user.streak >= streak_days:
            award_achievement(user.id, achievement_id)

def check_point_achievements(user):
    """Check if a user has earned any point-based achievements."""
    point_achievements = {
        100: 5,    # 100 points (achievement ID 5)
        500: 6,    # 500 points (achievement ID 6)
        1000: 7,   # 1000 points (achievement ID 7)
        5000: 8    # 5000 points (achievement ID 8)
    }
    
    for points, achievement_id in point_achievements.items():
        if user.points >= points:
            award_achievement(user.id, achievement_id)

def get_leaderboard(limit=10):
    """Get the top users by points for the leaderboard."""
    try:
        leaders = User.query.order_by(User.points.desc()).limit(limit).all()
        return [
            {
                "id": user.id, 
                "username": user.username, 
                "points": user.points,
                "streak": user.streak
            }
            for user in leaders
        ]
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return []

def get_user_achievements(user_id):
    """Get all achievements for a user."""
    try:
        achievements = db.session.query(
            Achievement, UserAchievement.earned_at
        ).join(
            UserAchievement, UserAchievement.achievement_id == Achievement.id
        ).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        return [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "badge_icon": a.badge_icon,
                "points": a.points,
                "earned_at": earned_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for a, earned_at in achievements
        ]
    except Exception as e:
        logger.error(f"Error getting user achievements: {e}")
        return []

def initialize_achievements():
    """Initialize default achievements if they don't exist."""
    default_achievements = [
        # As per the schema fixes summary document
        {"name": "First Login", "description": "Logged in for the first time", "badge_icon": "award", "points": 5},
        {"name": "Streak Starter", "description": "Maintained a 3-day streak", "badge_icon": "calendar", "points": 10},
        {"name": "Consistent Learner", "description": "Maintained a 7-day streak", "badge_icon": "calendar-check", "points": 25},
        {"name": "Diagnosis Expert", "description": "Correctly diagnosed 5 cases", "badge_icon": "clipboard-check", "points": 25},
        {"name": "Knowledge Seeker", "description": "Reviewed 10 flashcards", "badge_icon": "book-open", "points": 15},
        {"name": "Quiz Master", "description": "Completed 3 daily challenges", "badge_icon": "clipboard-pulse", "points": 20},
    ]
    
    try:
        # Check if we already have achievements to avoid duplicates
        if Achievement.query.count() == 0:
            for achievement_data in default_achievements:
                new_achievement = Achievement(
                    name=achievement_data["name"],
                    description=achievement_data["description"],
                    badge_icon=achievement_data["badge_icon"],
                    points=achievement_data["points"]
                )
                db.session.add(new_achievement)
            
            db.session.commit()
            logger.info("Default achievements initialized")
            return True
        else:
            logger.info("Achievements already exist, skipping initialization")
            return True
    except Exception as e:
        logger.error(f"Error initializing achievements: {e}")
        db.session.rollback()
        return False
