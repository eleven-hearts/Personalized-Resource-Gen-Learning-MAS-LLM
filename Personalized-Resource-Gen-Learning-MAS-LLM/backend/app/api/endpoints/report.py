from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.services.spark_service import spark_service

router = APIRouter()


class ReportGenerateRequest(BaseModel):
    """
    学习报告生成请求格式
    """
    user_info: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    learning_path: Optional[List[Dict[str, Any]]] = None
    resource_usage: Optional[List[Dict[str, Any]]] = None
    quiz_results: Optional[List[Dict[str, Any]]] = None
    evaluation_result: Optional[Dict[str, Any]] = None
    report_type: str = "weekly"


@router.post("/generate")
async def generate_learning_report(request: ReportGenerateRequest):
    """
    生成学习报告。

    作用：
    1. 汇总学生画像、学习路径、资源使用、测评结果
    2. 调用大模型生成结构化学习报告
    3. 返回适合前端展示的报告内容
    """
    prompt = f"""
你是一名智能学习分析师。请根据以下数据生成一份个性化学习报告。

一、学生基本信息：
{request.user_info or {}}

二、学生画像：
{request.profile or {}}

三、学习路径：
{request.learning_path or []}

四、资源使用情况：
{request.resource_usage or []}

五、测评结果：
{request.quiz_results or []}

六、已有评估结果：
{request.evaluation_result or {}}

请生成一份 {request.report_type} 学习报告，要求包括：

1. 学习总体总结
2. 知识掌握情况
3. 已完成内容
4. 薄弱知识点
5. 学习行为分析
6. 后续学习建议
7. 下一阶段学习计划
8. 可视化指标数据

请用清晰的 Markdown 格式输出。
"""

    messages = [
        {
            "role": "system",
            "content": "你是一个个性化学习报告生成智能体，擅长根据学习数据生成结构清晰、建议具体的学习报告。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    report_content = spark_service.chat(
        messages=messages,
        temperature=0.6,
        max_tokens=4096
    )

    return {
        "message": "学习报告生成成功",
        "report_type": request.report_type,
        "report_content": report_content,
        "summary_cards": {
            "knowledge_mastery": 75,
            "learning_completion": 80,
            "quiz_score": 70,
            "activity_score": 85
        },
        "chart_data": {
            "radar": [
                {"name": "知识掌握", "value": 75},
                {"name": "学习投入", "value": 85},
                {"name": "学习效率", "value": 78},
                {"name": "练习表现", "value": 70},
                {"name": "资源利用", "value": 82}
            ],
            "weak_points": [
                {"name": "HashMap扩容机制", "value": 40},
                {"name": "链表结构", "value": 55},
                {"name": "泛型使用", "value": 60}
            ]
        }
    }