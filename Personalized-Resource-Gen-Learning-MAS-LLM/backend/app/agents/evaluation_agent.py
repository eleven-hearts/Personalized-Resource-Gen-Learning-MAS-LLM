from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.services.spark_service import spark_service


class EvaluationAgent(BaseAgent):
    """
    学习效果评估智能体
    负责跟踪学习行为，多维度评估学习效果
    """

    def __init__(self):
        super().__init__(
            name="学习效果评估师",
            role="evaluator",
            description="通过分析学生的学习行为、练习测试情况和资源使用反馈，多维度评估学习效果并提供优化建议。",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估学习效果
        :param context: 包含学习行为数据、测试记录、资源使用记录
        :return: 评估报告和优化建议
        """
        profile = context.get("profile", {})
        learning_logs = context.get("learning_logs", [])
        quiz_results = context.get("quiz_results", [])
        resource_usage = context.get("resource_usage", [])

        prompt = self._build_evaluation_prompt(profile, learning_logs, quiz_results, resource_usage)

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        evaluation = spark_service.chat(messages)

        return {
            "evaluation_report": evaluation,
            "dimensions": self._extract_dimensions(evaluation),
            "suggestions": self._extract_suggestions(evaluation),
        }

    def _build_evaluation_prompt(self, profile, logs, quiz_results, resource_usage) -> str:
        return f"""请根据以下数据对学生的学习效果进行评估。

学生画像：{profile}

学习行为记录（最近7天）：
{self._format_logs(logs)}

练习测试结果：
{self._format_quiz_results(quiz_results)}

资源使用情况：
{self._format_resource_usage(resource_usage)}

请从以下维度进行评估：
1. 知识掌握度
2. 学习投入度
3. 学习效率
4. 薄弱环节
5. 进步趋势

并给出：
1. 综合评分（百分制）
2. 各维度评分
3. 具体优化建议
4. 学习资源调整方案

以JSON格式输出。"""

    def _format_logs(self, logs: List[Dict]) -> str:
        if not logs:
            return "暂无记录"
        return "\n".join([f"- {log.get('date')}: {log.get('action')}" for log in logs[:10]])

    def _format_quiz_results(self, results: List[Dict]) -> str:
        if not results:
            return "暂无记录"
        return "\n".join([f"- {r.get('topic')}: {r.get('score')}/{r.get('total')}" for r in results[:10]])

    def _format_resource_usage(self, usage: List[Dict]) -> str:
        if not usage:
            return "暂无记录"
        return "\n".join([f"- {u.get('resource')}: {u.get('duration')}分钟" for u in usage[:10]])

    def _extract_dimensions(self, evaluation: str) -> Dict[str, float]:
        """提取各维度评分"""
        import re
        dimensions = {}
        # 简单提取数字作为评分
        scores = re.findall(r'(\d+)(?:\s*分)?', evaluation)
        if scores:
            dimensions["overall"] = float(scores[0])
        return dimensions

    def _extract_suggestions(self, evaluation: str) -> List[str]:
        """提取优化建议"""
        suggestions = []
        lines = evaluation.split("\n")
        for line in lines:
            if "建议" in line or "优化" in line or "调整" in line:
                suggestions.append(line.strip())
        return suggestions[:5]
