from fastapi import FastAPI, Depends, HTTPException
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
from .seed import seed_members
import logging

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
            seed_members()
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
    title="Member Service",
    description="API for managing members",
    version="1.0.0",
    openapi_tags=[{
        "name": "members",
        "description": "Operations with members"
    }]
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

@app.post("/members/", response_model=schemas.Member, tags=["members"])
def create_member(member: schemas.MemberCreate, db: Session = Depends(database.get_db)):
    try:
        db_member = models.Member(**member.dict())
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "members_login_key" in error_msg:
            raise DuplicateDataError(
                "Member with this login already exists",
                {"login": member.login}
            )
        elif "members_email_key" in error_msg:
            raise DuplicateDataError(
                "Member with this email already exists",
                {"email": member.email}
            )
        raise DatabaseError("Failed to create member", {"error": str(e.orig)})
    except Exception as e:
        db.rollback()
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to create member", {"error": str(e)})

@app.get("/members/", response_model=List[schemas.Member], tags=["members"])
def get_members(db: Session = Depends(database.get_db)):
    try:
        members = db.query(models.Member)\
            .filter(models.Member.is_deleted == False)\
            .order_by(models.Member.created_at.desc())\
            .all()
            
        if not members:
            raise NoDataFoundError(
                "No active members found",
                {"service": "member-service"}
            )
            
        return members
    except Exception as e:
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to fetch members", {"error": str(e)})

@app.delete("/members/", tags=["members"])
def delete_members(db: Session = Depends(database.get_db)):
    try:
        # Check if there are any active members to delete
        active_members = db.query(models.Member)\
            .filter(models.Member.is_deleted == False)\
            .count()
            
        if active_members == 0:
            raise NoDataFoundError(
                "No active members found to delete",
                {"service": "member-service"}
            )
            
        db.query(models.Member).update({"is_deleted": True})
        db.commit()
        return {"message": "All members have been soft deleted"}
    except Exception as e:
        db.rollback()
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to delete members", {"error": str(e)}) 