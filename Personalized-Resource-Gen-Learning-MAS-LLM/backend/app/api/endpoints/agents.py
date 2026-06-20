from datetime import datetime, timezone
import json
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.learning import LearningPath, PathNode
from app.models.resource import Resource
from app.models.user import User
from app.services.spark_service import spark_service

router = APIRouter()

RESOURCE_TYPE_LABELS = {
    "document": "讲解文档",
    "mindmap": "思维导图",
    "quiz": "练习题",
    "reading": "拓展阅读",
    "video": "视频脚本",
    "code": "代码案例",
}


def _serialize_resource(resource: Resource) -> Dict[str, Any]:
    return {
        "id": resource.id,
        "user_id": resource.user_id,
        "title": resource.title,
        "resource_type": resource.resource_type,
        "content": resource.content,
        "metadata": resource.metadata_json or {},
        "status": resource.status,
        "created_at": resource.created_at,
        "updated_at": resource.updated_at,
    }


def _extract_json_object(text: str) -> dict:
    try:
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]
        else:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                text = text[start : end + 1]
        return json.loads(text.strip())
    except Exception:
        return {}


async def _call_spark(messages: list[dict[str, str]], max_tokens: int = 2048) -> str:
    try:
        content = await run_in_threadpool(spark_service.chat, messages, 0.7, max_tokens)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not content:
        raise HTTPException(status_code=502, detail="大模型返回为空")
    if content.startswith("请求错误") or content.startswith("连接错误"):
        raise HTTPException(status_code=502, detail=content)
    return content


async def _generate_resource_content(
    course: str,
    topic: str,
    resource_type: str,
    requirements: str,
    profile: dict | None = None,
) -> str:
    label = RESOURCE_TYPE_LABELS.get(resource_type, "学习资源")
    prompt = f"""请生成一份个性化学习资源。

资源类型：{label}
课程：{course or '未指定'}
知识点：{topic or '未指定'}
特殊要求：{requirements or '无'}
学生画像：{json.dumps(profile or {}, ensure_ascii=False)}

输出要求：
1. 直接输出 Markdown 内容
2. 内容必须完整、可直接给学生使用
3. 根据资源类型组织结构，例如文档要有讲解，练习题要有题目和参考解析，代码案例要有代码
4. 不要说明"我是模型"，不要输出无关寒暄
"""
    return await _call_spark(
        [
            {"role": "system", "content": "你是多智能体学习资源生成系统中的资源生成专家。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
    )


@router.post("/generate")
async def generate_resource(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    触发多智能体协同生成资源。
    """
    user_id = request.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="缺少 user_id")

    course = (request.get("course") or "").strip()
    topic = (request.get("topic") or "").strip()
    requirements = (request.get("requirements") or "").strip()
    resource_types = request.get("types") or request.get("resource_types") or ["document"]
    profile = request.get("profile") or {}
    task_id = uuid4().hex

    resources = []
    for resource_type in resource_types:
        label = RESOURCE_TYPE_LABELS.get(resource_type, "学习资源")
        title_prefix = course or "个性化学习"
        title_topic = topic or label
        resource = Resource(
            user_id=user_id,
            title=f"{title_prefix} - {title_topic}（{label}）",
            resource_type=resource_type,
            content=await _generate_resource_content(course, topic, resource_type, requirements, profile),
            metadata_json={
                "course": course,
                "topic": topic,
                "requirements": requirements,
                "description": f"面向{topic or course or '当前学习目标'}的{label}",
                "task_id": task_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            status="completed",
        )
        db.add(resource)
        resources.append(resource)

    db.commit()
    for resource in resources:
        db.refresh(resource)

    return {
        "message": "资源生成完成",
        "task_id": task_id,
        "resources": [_serialize_resource(resource) for resource in resources],
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态。
    """
    return {"task_id": task_id, "status": "completed", "progress": 100}


@router.post("/learning-path")
async def generate_learning_path(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    生成个性化学习路径。

    作用：
    1. 接收课程名称、学习目标、学生画像
    2. 调用大模型生成学习路径
    3. 持久化到数据库并返回阶段化学习计划
    """
    course = (request.get("course") or "机器学习基础").strip()
    goals = request.get("goals") or ["理解核心概念", "完成练习巩固", "做一个小项目"]
    resources = request.get("resources") or []
    profile = request.get("profile") or {}
    resource_titles = [
        resource.get("title", "学习资源")
        for resource in resources[:10]
        if isinstance(resource, dict)
    ]
    prompt = f"""请为学生生成个性化学习路径。

课程：{course}
学习目标：{json.dumps(goals, ensure_ascii=False)}
学生画像：{json.dumps(profile, ensure_ascii=False)}
可用资源：{json.dumps(resource_titles, ensure_ascii=False)}

请只输出 JSON，对象结构如下：
{{
  "stages": [
    {{
      "title": "阶段标题",
      "description": "阶段说明",
      "duration": "第1周",
      "status": "success|primary|info",
      "resources": ["资源名"],
      "progress": 0
    }}
  ]
}}
"""
    response = await _call_spark(
        [
            {"role": "system", "content": "你是个性化学习路径规划智能体，只输出可解析 JSON。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2048,
    )
    parsed = _extract_json_object(response)
    stages = parsed.get("stages")
    if not isinstance(stages, list):
        raise HTTPException(status_code=502, detail="大模型学习路径返回格式无法解析")

    learning_path = LearningPath(
        user_id=current_user.id,
        title=request.get("course") or request.get("topic") or "AI生成路径",
        source_type="ai",
    )
    db.add(learning_path)
    db.flush()

    for i, stage in enumerate(stages):
        node = PathNode(
            path_id=learning_path.id,
            title=stage.get("title", "") or stage.get("name", ""),
            description=stage.get("description", "") or stage.get("content", ""),
            order_index=i,
            status="active" if i == 0 else "locked",
            resources=stage.get("resources", []) or [],
        )
        db.add(node)

    db.commit()

    return {"message": "学习路径已生成", "stages": stages, "path_id": learning_path.id}


@router.post("/generate-path-from-resource/{resource_id}")
async def generate_path_from_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将学习资源的 Markdown 内容发送给 AI，直接生成一条全新学习路径"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    if resource.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该资源")

    content = resource.content or ""
    title = resource.title or "学习资源"

    prompt = f"""请根据以下学习资料内容，为学生生成一条个性化学习路径。

资料标题：{title}
资料内容：
{content[:6000]}

请只输出 JSON，对象结构如下：
{{
  "stages": [
    {{
      "title": "阶段标题",
      "description": "阶段说明（100字以内）",
      "duration": "第1周",
      "resources": ["推荐资源名"]
    }}
  ]
}}

要求：
1. 生成 5-8 个学习阶段，由浅入深
2. 每个阶段描述要具体、可执行
3. 阶段之间要有逻辑递进关系
4. 结合资料内容映射到知识点划分
"""
    response = await _call_spark(
        [
            {"role": "system", "content": "你是个性化学习路径规划智能体，根据学习资料划分学习阶段，只输出可解析 JSON。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
    )
    parsed = _extract_json_object(response)
    stages = parsed.get("stages")
    if not isinstance(stages, list):
        raise HTTPException(status_code=502, detail="大模型学习路径返回格式无法解析")

    learning_path = LearningPath(
        user_id=current_user.id,
        title=f"从「{title}」生成的学习路径",
        source_type="ai",
        source_name=title,
    )
    db.add(learning_path)
    db.flush()

    for i, stage in enumerate(stages):
        node = PathNode(
            path_id=learning_path.id,
            title=stage.get("title", "") or stage.get("name", ""),
            description=stage.get("description", "") or stage.get("content", ""),
            order_index=i,
            status="active" if i == 0 else "locked",
            resources=stage.get("resources", []) or [],
        )
        db.add(node)

    db.commit()

    return {"message": "学习路径已生成", "stages": stages, "path_id": learning_path.id, "path_title": learning_path.title}
