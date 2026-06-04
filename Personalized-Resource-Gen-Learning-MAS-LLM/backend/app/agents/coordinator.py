from typing import Dict, Any, List
from app.agents.profile_agent import ProfileAgent
from app.agents.resource_agent import ResourceAgent
from app.agents.path_agent import PathAgent
from app.agents.tutor_agent import TutorAgent
from app.agents.evaluation_agent import EvaluationAgent


class AgentCoordinator:
    """
    多智能体协调器
    负责调度和协调各智能体协同工作
    """

    def __init__(self):
        self.profile_agent = ProfileAgent()
        self.path_agent = PathAgent()
        self.tutor_agent = TutorAgent()
        self.evaluation_agent = EvaluationAgent()

    async def build_profile(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用画像智能体构建学习画像"""
        return await self.profile_agent.execute(context)

    async def generate_resources(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        调用多个资源生成智能体协同生成资源
        生成至少5种类型的资源
        """
        resource_types = context.get("resource_types", ["document", "mindmap", "quiz", "reading", "code"])
        results = []

        for rtype in resource_types:
            agent = ResourceAgent(resource_type=rtype)
            result = await agent.execute(context)
            results.append(result)

        return results

    async def plan_learning_path(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用路径规划智能体生成学习路径"""
        return await self.path_agent.execute(context)

    async def tutor(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用辅导智能体解答问题"""
        return await self.tutor_agent.execute(context)

    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用评估智能体评估学习效果"""
        return await self.evaluation_agent.execute(context)

    async def full_learning_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        完整学习工作流：
        1. 构建/更新画像
        2. 生成个性化资源
        3. 规划学习路径
        """
        # 1. 更新画像
        profile_result = await self.build_profile(context)
        profile = profile_result.get("profile", {})

        # 2. 生成资源
        resource_context = {**context, "profile": profile}
        resources = await self.generate_resources(resource_context)

        # 3. 规划路径
        path_context = {
            **context,
            "profile": profile,
            "available_resources": resources,
        }
        path = await self.plan_learning_path(path_context)

        return {
            "profile": profile,
            "resources": resources,
            "learning_path": path,
        }


coordinator = AgentCoordinator()
