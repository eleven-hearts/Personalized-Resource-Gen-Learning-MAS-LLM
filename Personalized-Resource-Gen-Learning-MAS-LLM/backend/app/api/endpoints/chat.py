from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter()

# 简单的连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # TODO: 调用大模型进行对话处理，构建学习画像
            response = {
                "type": "message",
                "content": f"收到消息: {message.get('content', '')}",
            }
            await manager.send_personal_message(json.dumps(response), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/message")
async def chat_message(message: Dict[str, str]):
    """
    HTTP方式对话接口
    """
    # TODO: 调用大模型进行对话处理
    return {"response": "这是模拟回复", "profile_update": None}
