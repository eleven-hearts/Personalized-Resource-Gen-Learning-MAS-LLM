from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class LearningPath(Base):
    """学习路径主表"""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False, default="个性化学习路径")
    source_type = Column(String(50), default="ai")  # "ai" 或 "pdf"
    source_name = Column(String(255))  # PDF文件名（如果来源是PDF）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PathNode(Base):
    """学习路径节点（阶段）"""
    __tablename__ = "path_nodes"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    order_index = Column(Integer, nullable=False)  # 排序序号
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration = Column(String(100))  # 如 "第1-2周"
    status = Column(String(50), default="locked")  # locked / active / completed
    resources = Column(JSON, default=list)  # 推荐资源列表
    progress = Column(Integer, default=0)  # 0-100
    quiz_passed = Column(Boolean, default=False)  # 答题是否通过
    quiz_score = Column(Integer, default=0)  # 答对题数
    quiz_total = Column(Integer, default=10)  # 总题数
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QuizQuestion(Base):
    """Quiz 题目（AI生成）"""
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("path_nodes.id"), nullable=False)
    question_type = Column(String(50), default="single_choice")  # single_choice / multi_choice / true_false
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # ["A. xxx", "B. xxx", "C. xxx", "D. xxx"]
    correct_answer = Column(String(10), nullable=False)  # 如 "A" 或 "A,C"
    explanation = Column(Text)  # 答案解释
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WrongAnswer(Base):
    """错题本 — 持久化用户答错的题目"""
    __tablename__ = "wrong_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("path_nodes.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"))
    node_title = Column(String(255))
    question = Column(Text, nullable=False)
    options = Column(JSON)
    user_answer = Column(String(10))
    correct_answer = Column(String(10))
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
