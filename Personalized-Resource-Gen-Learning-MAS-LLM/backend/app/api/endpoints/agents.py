from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.agents.coordinator import coordinator

router = APIRouter()


class LearningPathRequest(BaseModel):
    """
    学习路径生成请求格式
    """
    course: str
    goals: List[str] = []
    profile: Optional[Dict[str, Any]] = None
    available_resources: Optional[List[Dict[str, Any]]] = None


@router.post("/generate")
async def generate_resource(request: Dict[str, Any]):
    """
    预留接口：多智能体协同生成资源。

    资源生成现在主要使用：
    POST /api/v1/resources/generate
    """
    return {
        "message": "资源生成接口已迁移到 /api/v1/resources/generate",
        "suggested_api": "/api/v1/resources/generate"
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    预留接口：获取任务状态。
    当前系统还没有异步任务队列，先返回固定状态。
    """
    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100
    }


@router.post("/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """
    生成个性化学习路径。

    作用：
    1. 接收课程名称、学习目标、学生画像
    2. 调用 PathAgent 生成学习路径
    3. 返回阶段化学习计划
    """
    context = {
        "course": request.course,
        "goals": request.goals,
        "profile": request.profile or {},
        "available_resources": request.available_resources or [],
    }

    result = await coordinator.plan_learning_path(context)

    return {
        "message": "学习路径生成成功",
        "course": request.course,
        "goals": request.goals,
        "learning_path": result.get("path", []),
        "raw_content": result.get("raw_content", "")
    }