from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Statistics(Base):
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_dishes = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    created_at = Column(DateTime)
    
    user = relationship("User", back_populates="statistics")