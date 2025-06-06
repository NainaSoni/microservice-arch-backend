from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine
from .seed import seed_feedback
import time
from sqlalchemy.exc import OperationalError

def init_db():
    max_retries = 5
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            models.Base.metadata.create_all(bind=engine)
            # Seed the database
            seed_feedback()
            return
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Database not ready. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

# Initialize database with retry mechanism
init_db()

app = FastAPI(
    title="Feedback Service",
    description="API for managing feedback",
    version="1.0.0",
    openapi_tags=[{
        "name": "feedback",
        "description": "Operations with feedback"
    }]
)

@app.post("/feedback/", response_model=schemas.Feedback, tags=["feedback"])
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(database.get_db)):
    db_feedback = models.Feedback(feedback=feedback.feedback)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@app.get("/feedback/", response_model=List[schemas.Feedback], tags=["feedback"])
def get_feedbacks(db: Session = Depends(database.get_db)):
    feedbacks = db.query(models.Feedback).filter(models.Feedback.is_deleted == False).all()
    return feedbacks

@app.delete("/feedback/", tags=["feedback"])
def delete_feedbacks(db: Session = Depends(database.get_db)):
    db.query(models.Feedback).update({"is_deleted": True})
    db.commit()
    return {"message": "All feedbacks have been soft deleted"} 