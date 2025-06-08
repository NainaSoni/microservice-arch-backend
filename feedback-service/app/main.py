from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine
import time
from sqlalchemy.exc import OperationalError, IntegrityError
from shared.error_handling import (
    ServiceException,
    ValidationError,
    NotFoundError,
    InternalError,
    DuplicateDataError,
    NoDataFoundError,
    DatabaseError,
    ErrorCode
)
from fastapi.responses import JSONResponse
from .seed import seed_feedback
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from shared.auth import (
    Token, User, create_access_token, verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    max_retries = 5
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info("Attempting to create database tables...")
            models.Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
            # Seed the database
            logger.info("Starting database seeding...")
            seed_feedback()
            logger.info("Database seeding completed")
            return
        except OperationalError as e:
            if attempt == max_retries - 1:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                raise DatabaseError("Database connection failed", {"error": str(e)})
            logger.warning(f"Database not ready. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

# Initialize database with retry mechanism
logger.info("Initializing database...")
init_db()
logger.info("Database initialization completed")

app = FastAPI(
    title="Feedback Service",
    description="API for managing feedback",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "feedback",
            "description": "Operations with feedback"
        },
        {
            "name": "authentication",
            "description": "Authentication operations"
        }
    ]
)

# Configure OAuth2 with password flow
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scheme_name="OAuth2PasswordBearer",
    auto_error=True
)

@app.exception_handler(ServiceException)
async def service_exception_handler(request, exc: ServiceException):
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.error_code.value if isinstance(exc.error_code, ErrorCode) else exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )

@app.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    # In a real application, you would verify the password against a hashed password
    member = db.query(models.Member).filter(models.Member.login == form_data.username).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": member.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/feedback/", response_model=schemas.Feedback, tags=["feedback"])
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    try:
        db_feedback = models.Feedback(**feedback.dict())
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
    except Exception as e:
        db.rollback()
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to create feedback", {"error": str(e)})

@app.get("/feedback/", response_model=List[schemas.Feedback], tags=["feedback"])
def get_feedbacks(
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    try:
        feedbacks = db.query(models.Feedback)\
            .filter(models.Feedback.is_deleted == False)\
            .order_by(models.Feedback.created_at.desc())\
            .all()
            
        if not feedbacks:
            raise NoDataFoundError(
                "No active feedbacks found",
                {"service": "feedback-service"}
            )
            
        return feedbacks
    except Exception as e:
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to fetch feedbacks", {"error": str(e)})

@app.delete("/feedback/", tags=["feedback"])
def delete_feedbacks(
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    try:
        # Check if there are any active feedbacks to delete
        active_feedbacks = db.query(models.Feedback)\
            .filter(models.Feedback.is_deleted == False)\
            .count()
            
        if active_feedbacks == 0:
            raise NoDataFoundError(
                "No active feedbacks found to delete",
                {"service": "feedback-service"}
            )
            
        db.query(models.Feedback).update({"is_deleted": True})
        db.commit()
        return {"message": "All feedbacks have been soft deleted"}
    except Exception as e:
        db.rollback()
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to delete feedbacks", {"error": str(e)})

@app.delete("/feedback/{feedback_id}", tags=["feedback"])
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    try:
        feedback = db.query(models.Feedback)\
            .filter(models.Feedback.id == feedback_id, models.Feedback.is_deleted == False)\
            .first()
            
        if not feedback:
            raise NotFoundError(
                f"Feedback with id {feedback_id} not found",
                {"service": "feedback-service"}
            )
            
        feedback.is_deleted = True
        db.commit()
        return {"message": f"Feedback with id {feedback_id} has been soft deleted"}
    except Exception as e:
        db.rollback()
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to delete feedback", {"error": str(e)}) 