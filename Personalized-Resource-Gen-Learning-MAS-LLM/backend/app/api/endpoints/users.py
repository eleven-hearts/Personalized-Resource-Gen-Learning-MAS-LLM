from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_db)):
    # TODO: 从token获取当前用户
    pass


@router.put("/me", response_model=UserResponse)
def update_me(user_update: UserUpdate, db: Session = Depends(get_db)):
    # TODO: 更新当前用户信息
    pass


@router.get("/{user_id}/profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user.profile or {}


@router.put("/{user_id}/profile")
def update_user_profile(user_id: int, profile: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.profile = profile
    db.commit()
    db.refresh(user)
    return user.profile
