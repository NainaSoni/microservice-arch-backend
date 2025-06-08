from .database import SessionLocal
from .models import Member
from sqlalchemy.exc import IntegrityError
from shared.error_handling import DatabaseError
import logging
from passlib.context import CryptContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_members():
    logger.info("Starting member seeding process...")
    db = SessionLocal()
    try:
        # Check if we have any active members
        existing_members = db.query(Member).filter(Member.is_deleted == False).first()
        if existing_members:
            logger.info("Active members already exist, skipping seed")
            return

        logger.info("No active members found, proceeding with seeding...")

        # Sample members
        members = [
            Member(
                first_name="John",
                last_name="Doe",
                login="johndoe",
                avatar_url="https://example.com/avatars/john.jpg",
                followers=150,
                following=45,
                title="Senior Developer",
                email="john.doe@example.com",
                password=pwd_context.hash("testpassword123")
            ),
            Member(
                first_name="Jane",
                last_name="Smith",
                login="janesmith",
                avatar_url="https://example.com/avatars/jane.jpg",
                followers=200,
                following=60,
                title="Lead Developer",
                email="jane.smith@example.com",
                password=pwd_context.hash("testpassword123")
            ),
            Member(
                first_name="Mike",
                last_name="Johnson",
                login="mikejohnson",
                avatar_url="https://example.com/avatars/mike.jpg",
                followers=100,
                following=30,
                title="Software Engineer",
                email="mike.johnson@example.com",
                password=pwd_context.hash("testpassword123")
            ),
            Member(
                first_name="Test",
                last_name="User",
                login="testuser",
                avatar_url="https://example.com/avatars/test.jpg",
                followers=0,
                following=0,
                title="Test User",
                email="test.user@example.com",
                password=pwd_context.hash("testpassword123")
            ),
        ]

        # Add members to database
        for member in members:
            try:
                logger.info(f"Adding member: {member.login}")
                db.add(member)
                db.commit()
                logger.info(f"Successfully added member: {member.login}")
            except IntegrityError as e:
                db.rollback()
                logger.error(f"Error adding member {member.login}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error during member seeding: {e}")
        db.rollback()
        raise DatabaseError("Failed to seed member data", {"error": str(e)})
    finally:
        db.close() 