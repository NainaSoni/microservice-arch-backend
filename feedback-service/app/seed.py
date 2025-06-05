from .database import SessionLocal
from .models import Feedback

def seed_feedback():
    db = SessionLocal()
    try:
        # Check if we already have feedbacks
        existing_feedbacks = db.query(Feedback).first()
        if existing_feedbacks:
            return

        # Sample feedbacks
        feedbacks = [
            Feedback(
                feedback="Great team culture and work environment!",
            ),
            Feedback(
                feedback="Excellent opportunities for growth and learning.",
            ),
            Feedback(
                feedback="Strong leadership and clear communication.",
            ),
        ]

        # Add feedbacks to database
        for feedback in feedbacks:
            db.add(feedback)
        
        db.commit()
    except Exception as e:
        print(f"Error seeding feedback data: {e}")
        db.rollback()
    finally:
        db.close() 