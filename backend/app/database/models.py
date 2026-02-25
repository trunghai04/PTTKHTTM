from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from app.database.db import Base
import enum

class PredictionType(str, enum.Enum):
    SPAM = "spam"
    NEWS = "news"

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    type = Column(Enum(PredictionType), nullable=False)
    predicted_label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type.value,
            "predicted_label": self.predicted_label,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
