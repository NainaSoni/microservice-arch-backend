from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from shared.validation.validators import InputSanitizer

class MemberBase(BaseModel):
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

    @validator('first_name', 'last_name', 'login', 'avatar_url', 'title', pre=True, always=True)
    def sanitize_strings(cls, v):
        if v is None:
            return v
        return InputSanitizer.sanitize_string(v)

    @validator('login')
    def login_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Login must be alphanumeric')
        return v

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

class MemberCreate(MemberBase):
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

class Member(MemberBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 