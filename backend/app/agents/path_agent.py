from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.spark_service import spark_service


class PathAgent(BaseAgent):
    """
    学习路径规划智能体
    负责根据学生画像和课程目标规划个性化学习路径
    """

    def __init__(self):
        super().__init__(
            name="学习路径规划师",
            role="path_planner",
            description="根据学生的画像、学习目标和课程知识体系，规划科学、动态的个性化学习路径。",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成个性化学习路径
        :param context: 包含学生画像、课程信息、已有资源
        :return: 学习路径规划
        """
        profile = context.get("profile", {})
        course = context.get("course", "")
        goals = context.get("goals", [])
        available_resources = context.get("available_resources", [])

        prompt = self._build_path_prompt(profile, course, goals, available_resources)

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        content = spark_service.chat(messages)

        # 解析学习路径
        learning_path = self._parse_learning_path(content)

        return {
            "course": course,
            "path": learning_path,
            "raw_content": content,
        }

    def _build_path_prompt(self, profile, course, goals, resources) -> str:
        resources_info = "\n".join([f"- {r['title']} ({r['resource_type']})" for r in resources[:10]])

        return f"""请为以下学生规划{course}的个性化学习路径。

学生画像：
- 知识基础：{profile.get('knowledge_base', '未知')}
- 认知风格：{profile.get('cognitive_style', '未知')}
- 学习节奏：{profile.get('learning_pace', '中等')}
- 兴趣方向：{profile.get('interest_direction', '未知')}
- 学习目标：{', '.join(goals) if goals else '系统掌握课程知识'}

可用资源：
{resources_info}

请输出包含以下信息的学习路径：
1. 学习阶段划分（每个阶段的目标、时长）
2. 每个阶段推荐的学习资源
3. 阶段检测点
4. 动态调整建议

以JSON格式输出。"""

    def _parse_learning_path(self, content: str) -> List[Dict]:
        """解析学习路径内容"""
        import json
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            return json.loads(json_str.strip())
        except Exception:
            return [{"stage": "默认阶段", "content": content}]
