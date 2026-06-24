from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.spark_service import spark_service


class TutorAgent(BaseAgent):
    """
    智能辅导智能体
    负责解答学生问题，提供多模态答疑服务
    """

    def __init__(self):
        super().__init__(
            name="智能学习辅导老师",
            role="tutor",
            description="耐心、专业地解答学生学习中遇到的问题，提供文字解答、图解说明、代码示例等多模态解答形式。",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        解答学生问题
        :param context: 包含学生画像、问题内容、相关课程
        :return: 多模态解答
        """
        profile = context.get("profile", {})
        question = context.get("question", "")
        course = context.get("course", "")
        question_type = context.get("question_type", "concept")  # concept/code/debug

        prompt = self._build_tutor_prompt(profile, question, course, question_type)

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        answer = spark_service.chat(messages)

        return {
            "question": question,
            "answer": answer,
            "answer_type": question_type,
            "suggested_resources": [],  # TODO: 推荐相关资源
        }

    def _build_tutor_prompt(self, profile, question, course, question_type) -> str:
        type_instructions = {
            "concept": "请用通俗易懂的语言解释概念，可配合类比和例子。",
            "code": "请提供完整的代码示例，并逐行解释关键逻辑。",
            "debug": "请分析可能的错误原因，给出排查步骤和修正方案。",
        }

        return f"""学生问题：{question}

相关课程：{course}
问题类型：{question_type}

学生画像：
- 知识基础：{profile.get('knowledge_base', '未知')}
- 认知风格：{profile.get('cognitive_style', '未知')}

解答要求：
{type_instructions.get(question_type, '请提供详细解答。')}

请确保：
1. 解答符合学生的知识水平
2. 结构清晰，重点突出
3. 如适用，提供示例或练习
4. 引导学生思考，而非直接给答案"""
