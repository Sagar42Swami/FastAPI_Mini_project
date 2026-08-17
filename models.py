import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Tea(Base):
    __tablename__ = "teas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    flavor = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    brews = relationship("BrewLog", back_populates="tea", cascade="all, delete-orphan")

class BrewLog(Base):
    __tablename__ = "brew_logs"

    id = Column(Integer, primary_key=True, index=True)
    tea_id = Column(Integer, ForeignKey("teas.id", ondelete="CASCADE"), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)  # Rating from 1 to 5
    brewed_at = Column(DateTime, default=datetime.datetime.utcnow)

    tea = relationship("Tea", back_populates="brews")
