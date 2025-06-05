from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine
from .seed import seed_feedback

models.Base.metadata.create_all(bind=engine)
# Seed the database
seed_feedback()

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