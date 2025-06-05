from .database import SessionLocal
from .models import Member

def seed_members():
    db = SessionLocal()
    try:
        # Check if we already have members
        existing_members = db.query(Member).first()
        if existing_members:
            return

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
                email="john.doe@example.com"
            ),
            Member(
                first_name="Jane",
                last_name="Smith",
                login="janesmith",
                avatar_url="https://example.com/avatars/jane.jpg",
                followers=200,
                following=60,
                title="Lead Developer",
                email="jane.smith@example.com"
            ),
            Member(
                first_name="Mike",
                last_name="Johnson",
                login="mikejohnson",
                avatar_url="https://example.com/avatars/mike.jpg",
                followers=100,
                following=30,
                title="Software Engineer",
                email="mike.johnson@example.com"
            ),
        ]

        # Add members to database
        for member in members:
            db.add(member)
        
        db.commit()
    except Exception as e:
        print(f"Error seeding member data: {e}")
        db.rollback()
    finally:
        db.close() 