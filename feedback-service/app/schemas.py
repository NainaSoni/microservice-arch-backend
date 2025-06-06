from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from shared.validation.validators import InputSanitizer

class FeedbackBase(BaseModel):
    feedback: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Feedback content",
        example="This is a great service! The interface is intuitive and the features are exactly what I needed."
    )

    @validator('feedback', pre=True, always=True)
    def sanitize_feedback(cls, v):
        if v is None:
            return v
        return InputSanitizer.sanitize_string(v)

    class Config:
        schema_extra = {
            "example": {
                "feedback": "This is a great service! The interface is intuitive and the features are exactly what I needed."
            }
        }

class FeedbackCreate(FeedbackBase):
    class Config:
        schema_extra = {
            "example": {
                "feedback": "This is a great service! The interface is intuitive and the features are exactly what I needed."
            }
        }

class Feedback(FeedbackBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 