from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RatingValue(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"

class RatingCreate(BaseModel):
    dish_id: int
    rating: RatingValue
    comment: Optional[str] = None

class RatingResponse(BaseModel):
    id: int
    dish_id: int
    user_id: int
    rating: RatingValue
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    rating_summary: Dict[str, Any]
    suggestions: str
    improvement_areas: list[str]
    
    class Config:
        from_attributes = True