from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.agents.coordinator import coordinator

router = APIRouter()


class EvaluationRequest(BaseModel):
    """
    学习效果评估请求格式
    """
    profile: Optional[Dict[str, Any]] = None
    learning_logs: Optional[List[Dict[str, Any]]] = None
    quiz_results: Optional[List[Dict[str, Any]]] = None
    resource_usage: Optional[List[Dict[str, Any]]] = None


@router.post("/analyze")
async def analyze_learning_effect(request: EvaluationRequest):
    """
    分析学习效果。

    作用：
    1. 接收学生画像、学习行为、测试结果、资源使用情况
    2. 调用 EvaluationAgent 生成评估报告
    3. 返回综合评价、维度评分和学习建议
    """
    context = {
        "profile": request.profile or {},
        "learning_logs": request.learning_logs or [],
        "quiz_results": request.quiz_results or [],
        "resource_usage": request.resource_usage or [],
    }

    result = await coordinator.evaluate(context)

    return {
        "message": "学习效果评估成功",
        "evaluation_report": result.get("evaluation_report", ""),
        "dimensions": result.get("dimensions", {}),
        "suggestions": result.get("suggestions", [])
    }