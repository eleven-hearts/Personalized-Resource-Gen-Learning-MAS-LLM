from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ResourceType(str, enum.Enum):
    DOCUMENT = "document"
    MINDMAP = "mindmap"
    QUIZ = "quiz"
    READING = "reading"
    VIDEO = "video"
    CODE = "code"


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=False)
    content = Column(Text)
    metadata = Column(JSON, default=dict)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
