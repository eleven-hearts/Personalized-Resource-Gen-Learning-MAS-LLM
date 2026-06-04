from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None


class UserProfile(BaseModel):
    knowledge_base: Optional[str] = None
    cognitive_style: Optional[str] = None
    error_prone_points: Optional[list] = None
    learning_pace: Optional[str] = None
    interest_direction: Optional[str] = None
    learning_goals: Optional[list] = None


class UserInDB(UserBase):
    id: int
    profile: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass
