import os

if os.environ.get("RUNNING_IN_DOCKER"):
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@feedback-db:5432/feedback_db"
else:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/feedback_db"

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 