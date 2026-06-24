from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体任务"""
        pass

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return f"你是{self.name}，角色：{self.role}。{self.description}"
