from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse
from app.agents.coordinator import coordinator

router = APIRouter()
class ResourceGenerateRequest(BaseModel):
    """
    AI 资源生成请求格式
    """
    user_id: int = 1
    course: str
    topic: str
    resource_types: List[str] = ["document"]
    requirements: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    save_to_db: bool = False

@router.post("/generate")
async def generate_resources(
    request: ResourceGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    AI 生成个性化学习资源。

    这是比赛核心接口之一：
    1. 接收课程、知识点、资源类型、学生画像
    2. 调用 ResourceAgent 生成资源
    3. 可选择保存到数据库
    4. 返回生成结果
    """
    context = {
        "course": request.course,
        "topic": request.topic,
        "resource_types": request.resource_types,
        "requirements": request.requirements or "",
        "profile": request.profile or {},
    }

    generated_resources = await coordinator.generate_resources(context)

    saved_resources = []

    if request.save_to_db:
        for item in generated_resources:
            db_resource = Resource(
                user_id=request.user_id,
                title=item.get("title", f"{request.course} - {request.topic}"),
                resource_type=item.get("resource_type", "document"),
                content=item.get("content", ""),
                resource_metadata=item.get("metadata", {}),
                status="completed",
            )
            db.add(db_resource)
            db.commit()
            db.refresh(db_resource)

            saved_resources.append({
                "id": db_resource.id,
                "title": db_resource.title,
                "resource_type": db_resource.resource_type,
                "content": db_resource.content,
                "metadata": db_resource.resource_metadata,
                "status": db_resource.status,
            })

    return {
        "message": "资源生成成功",
        "course": request.course,
        "topic": request.topic,
        "resources": saved_resources if request.save_to_db else generated_resources,
    }


@router.post("/", response_model=ResourceResponse)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    db_resource = Resource(**resource.model_dump())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


@router.get("/", response_model=List[ResourceResponse])
def list_resources(
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Resource)
    if user_id:
        query = query.filter(Resource.user_id == user_id)
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    return query.offset(skip).limit(limit).all()


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, resource_update: ResourceUpdate, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    for field, value in resource_update.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    db.delete(resource)
    db.commit()
    return {"message": "资源已删除"}
