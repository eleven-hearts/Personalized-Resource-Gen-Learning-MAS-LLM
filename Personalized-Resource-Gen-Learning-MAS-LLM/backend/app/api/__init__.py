from fastapi import APIRouter
from app.api.endpoints import auth, users, resources, agents, chat

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(users.router, prefix="/users", tags=["用户"])
router.include_router(resources.router, prefix="/resources", tags=["资源"])
router.include_router(agents.router, prefix="/agents", tags=["智能体"])
router.include_router(chat.router, prefix="/chat", tags=["对话"])
