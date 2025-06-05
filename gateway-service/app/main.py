from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from . import schemas

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

# Service URLs
FEEDBACK_SERVICE_URL = os.getenv("FEEDBACK_SERVICE_URL")
MEMBER_SERVICE_URL = os.getenv("MEMBER_SERVICE_URL")

@app.post("/api/feedback", tags=["feedback"])
async def create_feedback(feedback: schemas.FeedbackCreate):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FEEDBACK_SERVICE_URL}/feedback/", json=feedback.dict())
        return response.json()

@app.get("/api/feedback", tags=["feedback"])
async def get_feedbacks():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FEEDBACK_SERVICE_URL}/feedback/")
        return response.json()

@app.delete("/api/feedback", tags=["feedback"])
async def delete_feedbacks():
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{FEEDBACK_SERVICE_URL}/feedback/")
        return response.json()

@app.post("/api/members", tags=["members"])
async def create_member(member: schemas.MemberCreate):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MEMBER_SERVICE_URL}/members/", json=member.dict())
        return response.json()

@app.get("/api/members", tags=["members"])
async def get_members():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MEMBER_SERVICE_URL}/members/")
        return response.json()

@app.delete("/api/members", tags=["members"])
async def delete_members():
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{MEMBER_SERVICE_URL}/members/")
        return response.json() 