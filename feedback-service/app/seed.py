from .database import SessionLocal
from .models import Feedback
from sqlalchemy.exc import IntegrityError
from shared.error_handling import DatabaseError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_feedback():
    logger.info("Starting feedback seeding process...")
    db = SessionLocal()
    try:
        # Check if we have any active feedbacks
        existing_feedbacks = db.query(Feedback).filter(Feedback.is_deleted == False).first()
        if existing_feedbacks:
            logger.info("Active feedbacks already exist, skipping seed")
            return

        logger.info("No active feedbacks found, proceeding with seeding...")

        # Sample feedbacks
        feedbacks = [
            Feedback(
                feedback="Great team culture and work environment!"
            ),
            Feedback(
                feedback="Excellent learning opportunities and growth."
            ),
            Feedback(
                feedback="Very supportive management and colleagues."
            ),
        ]

        # Add feedbacks to database
        for feedback in feedbacks:
            try:
                logger.info(f"Adding feedback: {feedback.feedback[:30]}...")
                db.add(feedback)
                db.commit()
                logger.info(f"Successfully added feedback")
            except IntegrityError as e:
                db.rollback()
                logger.error(f"Error adding feedback: {str(e)}")
                continue

        logger.info("Successfully completed feedback seeding")
    except Exception as e:
        logger.error(f"Error during feedback seeding: {e}")
        db.rollback()
        raise DatabaseError("Failed to seed feedback data", {"error": str(e)})
    finally:
        db.close() 