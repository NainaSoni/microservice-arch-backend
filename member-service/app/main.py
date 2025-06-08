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
from .seed import seed_members
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from shared.auth import (
    Token, User, create_access_token, verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from passlib.context import CryptContext

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
    openapi_tags=[
        {
            "name": "members",
            "description": "Operations with members"
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    member = db.query(models.Member).filter(models.Member.login == form_data.username, models.Member.is_deleted == False).first()
    if not member or not pwd_context.verify(form_data.password, member.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": member.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/members/", response_model=schemas.Member, tags=["members"], status_code=201)
def create_member(
    member: schemas.MemberCreate,
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    # Check for duplicate login
    db_member_by_login = db.query(models.Member).filter(models.Member.login == member.login).first()
    if db_member_by_login:
        raise ServiceException(
            "Member with this login already exists",
            ErrorCode.DUPLICATE_DATA_ERROR,
            {"login": member.login}
        )

    # Check for duplicate email
    db_member_by_email = db.query(models.Member).filter(models.Member.email == member.email).first()
    if db_member_by_email:
        raise ServiceException(
            "Member with this email already exists",
            ErrorCode.DUPLICATE_DATA_ERROR,
            {"email": member.email}
        )
    
    db_member = models.Member(
        first_name=member.first_name,
        last_name=member.last_name,
        login=member.login,
        avatar_url=member.avatar_url,
        followers=member.followers,
        following=member.following,
        title=member.title,
        email=member.email,
        password=pwd_context.hash(member.password)
    )
    db.add(db_member)
    try:
        db.commit()
        db.refresh(db_member)
        return db_member
    except IntegrityError as e:
        db.rollback()
       
        if "members_login_key" in str(e):
            raise ServiceException(
                "Member with this login already exists (race condition)",
                ErrorCode.DUPLICATE_DATA_ERROR,
                {"login": member.login, "error": str(e)}
            )
        elif "members_email_key" in str(e): 
            raise ServiceException(
                "Member with this email already exists (race condition)",
                ErrorCode.DUPLICATE_DATA_ERROR,
                {"email": member.email, "error": str(e)}
            )
        else:
            raise DatabaseError("Failed to create member due to database constraint violation", {"error": str(e)})

@app.get("/members/", response_model=List[schemas.Member], tags=["members"])
def get_members(
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    try:
        logger.info(f"Getting members for user: {token_data.login}")
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
def delete_members(
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
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

@app.delete("/members/{member_id}", tags=["members"])
def delete_member(
    member_id: int,
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    try:
        logger.info(f"Attempting to delete member with ID: {member_id}")
        # First check if member exists at all
        member = db.query(models.Member).filter(models.Member.id == member_id).first()
        if not member:
            logger.warning(f"Member with ID {member_id} does not exist in the database")
            raise NotFoundError(
                f"Member with id {member_id} not found",
                {"service": "member-service", "details": "Member does not exist in the database"}
            )
            
        # Then check if member is already deleted
        if member.is_deleted:
            logger.warning(f"Member with ID {member_id} is already soft deleted")
            raise NotFoundError(
                f"Member with id {member_id} not found",
                {"service": "member-service", "details": "Member is already soft deleted"}
            )
            
        # Perform the soft delete
        member.is_deleted = True
        try:
            db.commit()
            logger.info(f"Member with ID {member_id} has been soft deleted successfully")
            return {"message": f"Member with id {member_id} has been soft deleted"}
        except Exception as commit_error:
            db.rollback()
            logger.error(f"Failed to commit soft delete for member {member_id}: {str(commit_error)}")
            raise DatabaseError("Failed to commit member deletion", {"error": str(commit_error)})
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting member with ID {member_id}: {str(e)}")
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to delete member", {"error": str(e)})

@app.delete("/internal/members/{member_id}/hard", response_model=dict)
def hard_delete_member(member_id: int, db: Session = Depends(database.get_db)):
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
    return {"message": f"Member with id {member_id} has been hard deleted from the database"}

@app.get("/members/{member_id}", response_model=schemas.Member, tags=["members"])
def get_member(
    member_id: int,
    db: Session = Depends(database.get_db),
    token_data: Token = Depends(verify_token)
):
    try:
        logger.info(f"Attempting to get member with ID: {member_id}")
        member = db.query(models.Member).filter(models.Member.id == member_id).first()
        
        if not member:
            logger.warning(f"Member with ID {member_id} not found")
            raise NotFoundError(
                f"Member with id {member_id} not found",
                {"service": "member-service", "details": "Member does not exist in the database"}
            )
            
        logger.info(f"Found member with ID {member_id}: {member.login}")
        return member
    except Exception as e:
        logger.error(f"Error getting member with ID {member_id}: {str(e)}")
        if isinstance(e, ServiceException):
            raise e
        raise DatabaseError("Failed to get member", {"error": str(e)}) 