from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class MemberCreate(BaseModel):
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="First name of the member",
        example="John"
    )
    last_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Last name of the member",
        example="Doe"
    )
    login: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Unique login username",
        example="johndoe123"
    )
    avatar_url: Optional[str] = Field(
        None, 
        max_length=255, 
        description="URL to member's avatar image",
        example="https://example.com/avatars/john.jpg"
    )
    followers: Optional[int] = Field(
        0, 
        ge=0, 
        description="Number of followers",
        example=100
    )
    following: Optional[int] = Field(
        0, 
        ge=0, 
        description="Number of people following",
        example=50
    )
    title: Optional[str] = Field(
        None, 
        max_length=100, 
        description="Member's title or role",
        example="Software Engineer"
    )
    email: EmailStr = Field(
        ..., 
        description="Valid email address",
        example="john.doe@example.com"
    )
    password: str = Field(..., min_length=6, example="testpassword123")

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "login": "janedoe",
                "avatar_url": "https://example.com/avatars/jane.jpg",
                "followers": 150,
                "following": 70,
                "title": "Data Scientist",
                "email": "jane.doe@example.com",
                "password": "securepassword123"
            }
        }

class FeedbackCreate(BaseModel):
    feedback: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Text content of the feedback",
        example="This is a great team, always supportive and innovative!"
    )

    class Config:
        schema_extra = {
            "example": {
                "feedback": "The project management could be improved with more frequent updates."
            }
        } 