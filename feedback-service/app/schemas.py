from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
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