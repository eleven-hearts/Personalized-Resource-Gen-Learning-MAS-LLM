from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.spark_service import spark_service


class ResourceAgent(BaseAgent):
    """
    资源生成智能体
    负责生成各类个性化学习资源
    """

    RESOURCE_TYPES = {
        "document": "专业课程讲解文档",
        "mindmap": "知识点思维导图",
        "quiz": "练习题目",
        "reading": "拓展阅读材料",
        "video": "教学视频脚本",
        "code": "代码实操案例",
    }

    def __init__(self, resource_type: str = "document"):
        self.resource_type = resource_type
        type_name = self.RESOURCE_TYPES.get(resource_type, "学习资源")
        super().__init__(
            name=f"{type_name}生成专家",
            role="resource_generator",
            description=f"专注于生成高质量的{type_name}，根据学生画像和学习需求定制内容。",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成指定类型的学习资源
        :param context: 包含学生画像、课程信息、生成需求
        :return: 生成的资源内容
        """
        profile = context.get("profile", {})
        course = context.get("course", "")
        topic = context.get("topic", "")
        requirements = context.get("requirements", "")

        prompt = self._build_resource_prompt(profile, course, topic, requirements)

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        content = spark_service.chat(messages)

        return {
            "resource_type": self.resource_type,
            "title": f"{course} - {topic}",
            "content": content,
            "metadata": {
                "course": course,
                "topic": topic,
                "target_profile": profile,
            },
        }

    def _build_resource_prompt(self, profile, course, topic, requirements) -> str:
        return f"""请为以下学生生成一份{self.RESOURCE_TYPES.get(self.resource_type)}。

学生画像：
- 知识基础：{profile.get('knowledge_base', '未知')}
- 认知风格：{profile.get('cognitive_style', '未知')}
- 学习节奏：{profile.get('learning_pace', '中等')}
- 兴趣方向：{profile.get('interest_direction', '未知')}

课程信息：{course}
知识点：{topic}
特殊要求：{requirements}

请确保内容：
1. 符合学生的知识基础和认知风格
2. 难度适中，循序渐进
3. 包含实际案例或应用场景
4. 格式清晰，便于学习

直接输出资源内容。"""
