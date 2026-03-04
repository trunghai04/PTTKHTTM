from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from app.database.db import Base
import enum

class PredictionType(str, enum.Enum):
    SPAM = "spam"
    NEWS = "news"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # null for Google-only users
    google_id = Column(String, unique=True, index=True, nullable=True)
    google_refresh_token = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, server_default=UserRole.USER.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    type = Column(Enum(PredictionType), nullable=False)
    predicted_label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, nullable=True)
    source = Column(String, nullable=True)  # 'gmail' | 'manual' | null
    email_subject = Column(String, nullable=True)
    email_snippet = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type.value,
            "predicted_label": self.predicted_label,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source,
            "email_subject": self.email_subject,
            "email_snippet": self.email_snippet,
        }
