from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import Dict, List
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.spark_service import spark_service

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 聊天接口，当前先保留基础功能。
    后期可以改成大模型流式输出。
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            response = {
                "type": "message",
                "content": f"收到消息: {message.get('content', '')}",
            }

            await manager.send_personal_message(
                json.dumps(response, ensure_ascii=False),
                websocket,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


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


async def _call_spark(messages: List[Dict[str, str]], max_tokens: int = 2048) -> str:
    try:
        content = await run_in_threadpool(spark_service.chat, messages, 0.7, max_tokens)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not content:
        raise HTTPException(status_code=502, detail="大模型返回为空")
    if content.startswith("请求错误") or content.startswith("连接错误"):
        raise HTTPException(status_code=502, detail=content)
    return content


async def _build_profile_by_model(content: str, current_profile: dict) -> dict:
    prompt = f"""请根据学生最新对话更新学习画像。

当前画像：
{json.dumps(current_profile or {}, ensure_ascii=False)}

学生最新对话：
{content}

请只输出 JSON 对象，字段包含：
- knowledge_base: 知识基础
- cognitive_style: 认知风格
- error_prone_points: 易错点列表
- learning_pace: 学习节奏
- interest_direction: 兴趣方向
- learning_goals: 学习目标列表
"""
    response = await _call_spark(
        [
            {"role": "system", "content": "你是学习画像分析师，只输出可解析 JSON。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
    )
    updates = _extract_json_object(response)
    return {**(current_profile or {}), **updates, "latest_dialogue": content}


async def _answer_by_model(content: str, profile: dict) -> str:
    prompt = f"""学生画像：
{json.dumps(profile or {}, ensure_ascii=False)}

学生问题：
{content}

请作为智能学习辅导老师直接回复学生。要求：
1. 使用中文
2. 根据学生画像调整难度
3. 解释清楚概念或步骤
4. 给出一个可执行的下一步学习建议
"""
    return await _call_spark(
        [
            {"role": "system", "content": "你是耐心、专业的智能学习辅导老师。"},
            {"role": "user", "content": prompt},
        ]
    )


@router.post("/message")
async def chat_message(
    message: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    HTTP 聊天接口。

    作用：
    1. 接收前端传来的学生问题
    2. 调用智能辅导 Agent
    3. 返回 AI 解答结果
    """
    content = (message.get("content") or "").strip()
    if not content:
        return {"response": "请先输入你的学习需求或问题。", "profile_update": current_user.profile or {}}

    profile = await _build_profile_by_model(content, current_user.profile or {})
    response = await _answer_by_model(content, profile)

    current_user.profile = profile
    db.commit()
    db.refresh(current_user)

    return {"response": response, "profile_update": profile}
