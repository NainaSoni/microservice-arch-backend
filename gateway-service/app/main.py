from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import httpx
import os
from . import schemas
from .config import settings
from shared.auth import (
    Token, User, create_access_token, verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(
    title="Organization Management Gateway",
    description="Gateway service for managing organization feedback and members",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "feedback",
            "description": "Operations with feedback"
        },
        {
            "name": "members",
            "description": "Operations with members"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OAuth2 with password flow
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scheme_name="OAuth2PasswordBearer",
    auto_error=True
)

# Service URLs
FEEDBACK_SERVICE_URL = os.getenv("FEEDBACK_SERVICE_URL")
MEMBER_SERVICE_URL = os.getenv("MEMBER_SERVICE_URL")

@app.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.MEMBER_SERVICE_URL}/token",
            data={"username": form_data.username, "password": form_data.password}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return response.json()

@app.post("/members/", tags=["members"])
async def create_member(
    member_data: schemas.MemberCreate,
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.MEMBER_SERVICE_URL}/members/",
            json=member_data.dict(),
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

@app.get("/members/", tags=["members"])
async def get_members(
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.MEMBER_SERVICE_URL}/members/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

@app.delete("/members/", tags=["members"])
async def delete_members(
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.MEMBER_SERVICE_URL}/members/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

@app.post("/feedback/", tags=["feedback"])
async def create_feedback(
    feedback_data: schemas.FeedbackCreate,
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.FEEDBACK_SERVICE_URL}/feedback/",
            json=feedback_data.dict(),
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

@app.get("/feedback/", tags=["feedback"])
async def get_feedback(
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FEEDBACK_SERVICE_URL}/feedback/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

@app.delete("/feedback/", tags=["feedback"])
async def delete_feedback(
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.FEEDBACK_SERVICE_URL}/feedback/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

@app.delete("/feedback/{feedback_id}", tags=["feedback"])
async def delete_feedback_by_id(
    feedback_id: int,
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.FEEDBACK_SERVICE_URL}/feedback/{feedback_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

@app.delete("/members/{member_id}", tags=["members"])
async def delete_member_by_id(
    member_id: int,
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.MEMBER_SERVICE_URL}/member/{member_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json() 