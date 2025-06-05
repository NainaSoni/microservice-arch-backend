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

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "login": "johndoe123",
                "email": "john.doe@example.com",
                "avatar_url": "https://example.com/avatars/john.jpg",
                "followers": 100,
                "following": 50,
                "title": "Software Engineer"
            }
        }

class FeedbackCreate(BaseModel):
    feedback: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Feedback content",
        example="This is a great service! The interface is intuitive and the features are exactly what I needed."
    )

    class Config:
        schema_extra = {
            "example": {
                "feedback": "This is a great service! The interface is intuitive and the features are exactly what I needed."
            }
        } 