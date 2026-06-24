from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.spark_service import spark_service


class ProfileAgent(BaseAgent):
    """
    学习画像构建智能体
    负责通过对话自动抽取学生特征，构建动态学习画像
    """

    def __init__(self):
        super().__init__(
            name="学习画像分析师",
            role="profile_builder",
            description="通过自然语言对话分析学生的学习特征，构建包含知识基础、认知风格、易错点偏好、学习节奏、兴趣方向、学习目标等维度的动态学生画像。",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析对话内容，更新学习画像
        :param context: 包含对话历史、当前消息、现有画像
        :return: 更新后的画像
        """
        conversation = context.get("conversation", [])
        current_profile = context.get("current_profile", {})
        message = context.get("message", "")

        # 构建提示词
        prompt = self._build_profile_prompt(conversation, current_profile, message)

        # 调用大模型分析
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        response = spark_service.chat(messages)

        # 解析响应，提取画像更新
        updated_profile = self._parse_profile_response(response, current_profile)
        return {"profile": updated_profile, "analysis": response}

    def _build_profile_prompt(self, conversation, current_profile, message) -> str:
        return f"""请根据以下对话内容，分析并更新学生的学习画像。

当前画像：{current_profile}

最新对话：
用户：{message}

请输出JSON格式的画像更新，包含以下维度：
- knowledge_base: 知识基础评估
- cognitive_style: 认知风格（如视觉型、听觉型、动手型等）
- error_prone_points: 易错点偏好列表
- learning_pace: 学习节奏（快/中/慢）
- interest_direction: 兴趣方向
- learning_goals: 学习目标列表

只输出JSON，不要其他内容。"""

    def _parse_profile_response(self, response: str, current_profile: Dict) -> Dict:
        """解析模型响应，合并到现有画像"""
        import json
        try:
            # 尝试提取JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response

            updates = json.loads(json_str.strip())
            # 合并更新到现有画像
            updated = {**current_profile, **updates}
            return updated
        except Exception:
            return current_profile
