from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json

from app.agents.coordinator import coordinator

router = APIRouter()


class ChatRequest(BaseModel):
    """
    聊天请求数据格式
    """
    message: str
    course: Optional[str] = None
    question_type: Optional[str] = "concept"
    profile: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """
    聊天响应数据格式
    """
    response: str
    profile_update: Optional[Dict[str, Any]] = None
    answer_type: Optional[str] = None
    suggested_resources: Optional[List[Dict[str, Any]]] = None


# 简单的 WebSocket 连接管理器，后面可以用于流式聊天
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


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    HTTP 聊天接口。

    作用：
    1. 接收前端传来的学生问题
    2. 调用智能辅导 Agent
    3. 返回 AI 解答结果
    """
    context = {
        "question": request.message,
        "course": request.course or "通用课程",
        "question_type": request.question_type or "concept",
        "profile": request.profile or {},
    }

    result = await coordinator.tutor(context)

    return ChatResponse(
        response=result.get("answer", ""),
        profile_update=None,
        answer_type=result.get("answer_type"),
        suggested_resources=result.get("suggested_resources", []),
    )