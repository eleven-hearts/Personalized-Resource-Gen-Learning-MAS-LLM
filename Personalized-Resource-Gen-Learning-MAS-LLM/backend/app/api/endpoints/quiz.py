import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learning import LearningPath, PathNode, QuizQuestion, WrongAnswer
from app.models.resource import Resource
from app.services.spark_service import spark_service

router = APIRouter()


def _extract_json_object(text: str) -> dict:
    try:
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]
        else:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                text = text[start : end + 1]
        return json.loads(text.strip())
    except Exception:
        return {}


async def _call_spark(messages: list[dict[str, str]], max_tokens: int = 4096) -> str:
    try:
        content = await run_in_threadpool(spark_service.chat, messages, 0.7, max_tokens)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not content:
        raise HTTPException(status_code=502, detail="大模型返回为空")
    if content.startswith("请求错误") or content.startswith("连接错误"):
        raise HTTPException(status_code=502, detail=content)
    return content


def _serialize_node(node: PathNode) -> dict:
    return {
        "id": node.id,
        "path_id": node.path_id,
        "order_index": node.order_index,
        "title": node.title,
        "description": node.description,
        "duration": node.duration,
        "status": node.status,
        "resources": node.resources or [],
        "progress": node.progress,
        "quiz_passed": node.quiz_passed,
        "quiz_score": node.quiz_score,
        "quiz_total": node.quiz_total,
    }


def _serialize_path(path: LearningPath, nodes: List[PathNode]) -> dict:
    return {
        "id": path.id,
        "user_id": path.user_id,
        "title": path.title,
        "source_type": path.source_type,
        "source_name": path.source_name,
        "nodes": [_serialize_node(n) for n in nodes],
        "created_at": path.created_at,
    }


# ===================== PDF 上传 & 路径生成 =====================

@router.post("/upload-pdf")
async def upload_pdf_and_generate_path(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传PDF文件，AI解析后生成个性化学习路径"""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传PDF文件")
    if file.size and file.size > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="PDF文件不能超过20MB")

    # 读取PDF文件内容
    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="PDF文件为空")

    # 尝试用 PyPDF2 提取文本，如果不可用则使用简易方式
    pdf_text = ""
    try:
        from PyPDF2 import PdfReader
        from io import BytesIO
        reader = PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
    except ImportError:
        # 如果没有 PyPDF2，尝试基本提取
        pdf_text = pdf_bytes.decode("utf-8", errors="ignore")
        # 过滤掉不可打印字符
        pdf_text = "".join(c for c in pdf_text if c.isprintable() or c in "\n\r\t")

    if not pdf_text.strip():
        raise HTTPException(status_code=400, detail="无法从PDF中提取文本，请确认PDF包含可读文字")

    # 截取前15000字符避免超token
    pdf_text_trimmed = pdf_text[:15000]

    # 调用AI生成学习路径
    prompt = f"""请根据以下PDF教材/文档内容，分析并生成一个结构化学习路径。

PDF内容摘要：
{pdf_text_trimmed}

请只输出JSON对象，格式如下：
{{
  "title": "基于《XXX》的学习路径",
  "stages": [
    {{
      "title": "阶段名称",
      "description": "阶段说明，100字以内",
      "duration": "预计学习时间",
      "resources": ["推荐资源1", "推荐资源2"],
      "order_index": 0
    }}
  ]
}}

要求：
1. 分为5-8个阶段
2. 按知识递进关系排序
3. 每个阶段给出清晰的描述和预计学习时间
4. order_index从0开始递增
"""
    response = await _call_spark(
        [
            {"role": "system", "content": "你是个性化学习路径规划专家，根据教材内容生成结构化学习路径，只输出可解析JSON。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
    )
    parsed = _extract_json_object(response)
    stages = parsed.get("stages")
    if not isinstance(stages, list) or len(stages) == 0:
        raise HTTPException(status_code=502, detail="AI未能从PDF生成有效学习路径")

    # 保存到数据库
    path = LearningPath(
        user_id=current_user.id,
        title=parsed.get("title", f"基于《{file.filename}》的学习路径"),
        source_type="pdf",
        source_name=file.filename,
    )
    db.add(path)
    db.flush()

    nodes = []
    for i, stage in enumerate(stages):
        node = PathNode(
            path_id=path.id,
            order_index=stage.get("order_index", i),
            title=stage.get("title", f"阶段{i + 1}"),
            description=stage.get("description", ""),
            duration=stage.get("duration", ""),
            status="active" if i == 0 else "locked",
            resources=stage.get("resources", []),
            progress=0,
        )
        db.add(node)
        nodes.append(node)

    db.commit()
    for node in nodes:
        db.refresh(node)

    return {
        "message": "学习路径生成成功",
        "path": _serialize_path(path, nodes),
    }


# ===================== 获取学习路径 =====================

@router.get("/paths")
async def list_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有学习路径"""
    paths = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == current_user.id)
        .order_by(LearningPath.created_at.desc())
        .all()
    )
    result = []
    for path in paths:
        nodes = (
            db.query(PathNode)
            .filter(PathNode.path_id == path.id)
            .order_by(PathNode.order_index)
            .all()
        )
        result.append(_serialize_path(path, nodes))
    return result


@router.get("/path/{path_id}")
async def get_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取学习路径详情（含所有节点）"""
    path = (
        db.query(LearningPath)
        .filter(LearningPath.id == path_id, LearningPath.user_id == current_user.id)
        .first()
    )
    if not path:
        raise HTTPException(status_code=404, detail="学习路径不存在")
    nodes = (
        db.query(PathNode)
        .filter(PathNode.path_id == path.id)
        .order_by(PathNode.order_index)
        .all()
    )
    return _serialize_path(path, nodes)


# ===================== Quiz 出题 =====================

@router.post("/node/{node_id}/generate-questions")
async def generate_quiz_questions(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI为指定节点生成10道测试题目"""
    node = db.query(PathNode).filter(PathNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 验证节点属于当前用户
    path = db.query(LearningPath).filter(LearningPath.id == node.path_id).first()
    if not path or path.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此节点")

    # 删除旧题目
    db.query(QuizQuestion).filter(QuizQuestion.node_id == node_id).delete()

    # 调用AI生成题目
    prompt = f"""请为以下学习节点生成10道测试题目。

节点标题：{node.title}
节点描述：{node.description or '无'}
推荐资源：{json.dumps(node.resources or [], ensure_ascii=False)}

请只输出JSON数组，每个元素格式如下：
[
  {{
    "question": "题目内容",
    "question_type": "single_choice",
    "options": ["A. 选项A内容", "B. 选项B内容", "C. 选项C内容", "D. 选项D内容"],
    "correct_answer": "A",
    "explanation": "答案解释，50字以内"
  }}
]

要求：
1. 生成恰好10道单选题
2. 题目难度适中，覆盖节点核心知识点
3. 每题4个选项
4. 给出正确答案和解释
"""
    response = await _call_spark(
        [
            {"role": "system", "content": "你是个性化学习测评智能体，专门生成高质量测试题目，只输出可解析JSON数组。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
    )

    # 解析题目
    questions_data = _extract_json_object(response)
    if isinstance(questions_data, dict):
        # 可能在 "questions" 键中
        questions_data = questions_data.get("questions", [questions_data])
    if not isinstance(questions_data, list):
        raise HTTPException(status_code=502, detail="AI返回的题目格式无法解析")

    # 保存到数据库
    saved = []
    for q in questions_data[:10]:
        question = QuizQuestion(
            node_id=node_id,
            question_type=q.get("question_type", "single_choice"),
            question=q.get("question", ""),
            options=q.get("options", []),
            correct_answer=q.get("correct_answer", "A"),
            explanation=q.get("explanation", ""),
        )
        db.add(question)
        saved.append(question)

    # 更新节点总题数
    node.quiz_total = len(saved)
    node.quiz_score = 0
    node.quiz_passed = False

    db.commit()
    for q in saved:
        db.refresh(q)

    return {
        "message": f"已生成{len(saved)}道题目",
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "question_type": q.question_type,
                "options": q.options,
            }
            for q in saved
        ],
    }


@router.get("/node/{node_id}/questions")
async def get_quiz_questions(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取节点的题目（不含答案）"""
    node = db.query(PathNode).filter(PathNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    path = db.query(LearningPath).filter(LearningPath.id == node.path_id).first()
    if not path or path.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此节点")

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.node_id == node_id)
        .order_by(QuizQuestion.id)
        .all()
    )
    return {
        "node_id": node_id,
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "question_type": q.question_type,
                "options": q.options,
            }
            for q in questions
        ],
    }


@router.post("/node/{node_id}/submit")
async def submit_quiz_answers(
    node_id: int,
    answers: Dict[str, str],  # {"question_id": "selected_answer"}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交答题答案，判分并更新节点进度"""
    node = db.query(PathNode).filter(PathNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    path = db.query(LearningPath).filter(LearningPath.id == node.path_id).first()
    if not path or path.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此节点")

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.node_id == node_id)
        .all()
    )
    if not questions:
        raise HTTPException(status_code=400, detail="该节点暂无题目，请先生成题目")

    # 判分
    results = []
    correct_count = 0
    for q in questions:
        user_answer = answers.get(str(q.id), "").strip().upper()
        correct = q.correct_answer.strip().upper()
        is_correct = user_answer == correct
        if is_correct:
            correct_count += 1
        results.append({
            "question_id": q.id,
            "question": q.question,
            "user_answer": user_answer,
            "correct_answer": correct,
            "is_correct": is_correct,
            "explanation": q.explanation,
        })

    # 持久化错题到 WrongAnswer 表
    db.query(WrongAnswer).filter(
        WrongAnswer.user_id == current_user.id,
        WrongAnswer.node_id == node_id,
    ).delete()
    for r in results:
        if not r["is_correct"]:
            q_options = None
            for q in questions:
                if q.id == r["question_id"]:
                    q_options = q.options or []
                    break
            wrong = WrongAnswer(
                user_id=current_user.id,
                node_id=node_id,
                question_id=r["question_id"],
                node_title=node.title,
                question=r["question"],
                options=q_options or [],
                user_answer=r["user_answer"],
                correct_answer=r["correct_answer"],
                explanation=r["explanation"],
            )
            db.add(wrong)

    # 更新节点
    node.quiz_score = correct_count
    total = len(questions)
    node.progress = round((correct_count / total) * 100) if total > 0 else 0
    passed = correct_count >= 10  # 答对10题通过

    if passed:
        node.quiz_passed = True
        node.status = "completed"

        # 解锁下一个节点
        next_node = (
            db.query(PathNode)
            .filter(
                PathNode.path_id == node.path_id,
                PathNode.order_index == node.order_index + 1,
            )
            .first()
        )
        if next_node and next_node.status == "locked":
            next_node.status = "active"

    db.commit()
    db.refresh(node)

    return {
        "node_id": node_id,
        "correct_count": correct_count,
        "total": total,
        "passed": passed,
        "progress": node.progress,
        "status": node.status,
        "results": results,
    }


# ===================== 画像智能体 =====================

@router.post("/generate-profile")
async def generate_learning_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    画像智能体：根据用户在所有路径中的答题准确率，AI 生成学习画像。
    不做预设，完全基于真实答题数据。
    """
    paths = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == current_user.id)
        .all()
    )
    path_ids = [p.id for p in paths]
    nodes = (
        db.query(PathNode)
        .filter(PathNode.path_id.in_(path_ids))
        .all()
    ) if path_ids else []

    # 构建答题统计数据
    quiz_data = []
    for node in nodes:
        if node.quiz_score > 0 or node.quiz_total > 0:
            quiz_data.append({
                "node_title": node.title,
                "status": node.status,
                "correct": node.quiz_score,
                "total": node.quiz_total,
                "accuracy": round((node.quiz_score / node.quiz_total) * 100) if node.quiz_total > 0 else 0,
                "passed": node.quiz_passed,
            })

    if not quiz_data:
        profile = {
            "knowledge_base": "尚未开始答题，知识基础待评估",
            "cognitive_style": "待观察",
            "error_prone_points": [],
            "learning_pace": "待评估",
            "interest_direction": [],
            "learning_goals": [],
            "overall_accuracy": 0,
            "total_quiz_count": 0,
        }
        current_user.profile = profile
        db.commit()
        return {"message": "暂无答题数据", "profile": profile}

    total_correct = sum(d["correct"] for d in quiz_data)
    total_questions = sum(d["total"] for d in quiz_data)
    overall_accuracy = round((total_correct / total_questions) * 100) if total_questions > 0 else 0

    prompt = f"""请根据以下学生学习答题数据，生成个性化学习画像。

## 学生答题数据
{json.dumps(quiz_data, ensure_ascii=False, indent=2)}

## 总体统计
- 总答题数：{total_questions}
- 答对数：{total_correct}
- 总体准确率：{overall_accuracy}%

请只输出 JSON 对象，字段如下：
{{
  "knowledge_base": "根据准确率分析出的知识基础（字符串）",
  "cognitive_style": "根据答题表现推断的认知风格（如：视觉型学习者、逻辑推理型、记忆型等）",
  "error_prone_points": ["薄弱知识点列表"],
  "learning_pace": "学习节奏评估（如：快速/稳健/需要强化）",
  "interest_direction": ["推断的兴趣方向列表"],
  "learning_goals": ["建议的学习目标列表"],
  "evaluation_score": 0-100 的综合评分,
  "dimensions": {{
    "knowledge_mastery": 0-100 的知识掌握度评分,
    "cognitive_ability": 0-100 的认知能力评分,
    "learning_efficiency": 0-100 的学习效率评分,
    "weakness_awareness": 0-100 的薄弱点意识评分,
    "consistency": 0-100 的学习一致性评分,
    "growth_potential": 0-100 的成长潜力评分
  }},
  "suggestions": ["3-5条个性化学习建议"]
}}

要求：
1. 所有评分完全基于真实答题数据，不做任何预设
2. 准确率低于50%的节点对应的知识点应列入 error_prone_points
3. 答题通过率反映学习节奏
4. 评分要有区分度，不要全部给70分
"""
    response = await _call_spark(
        [
            {"role": "system", "content": "你是个性化学习画像分析智能体，专门根据学生真实答题数据生成画像。绝不使用预设模板数据。只输出可解析JSON。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
    )
    profile_data = _extract_json_object(response)

    profile = {
        "knowledge_base": profile_data.get("knowledge_base", ""),
        "cognitive_style": profile_data.get("cognitive_style", ""),
        "error_prone_points": profile_data.get("error_prone_points", []),
        "learning_pace": profile_data.get("learning_pace", ""),
        "interest_direction": profile_data.get("interest_direction", []),
        "learning_goals": profile_data.get("learning_goals", []),
        "evaluation_score": profile_data.get("evaluation_score", overall_accuracy),
        "dimensions": profile_data.get("dimensions", {}),
        "suggestions": profile_data.get("suggestions", []),
        "overall_accuracy": overall_accuracy,
        "total_quiz_count": total_questions,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    current_user.profile = profile
    db.commit()
    db.refresh(current_user)

    return {
        "message": "学习画像生成成功",
        "profile": profile,
    }


# ===================== 资源到节点 =====================

@router.post("/node/{node_id}/add-resource")
def add_resource_to_node(
    node_id: int,
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将资源添加到学习路径节点"""
    node = db.query(PathNode).filter(PathNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    current_resources = node.resources or []
    if resource.title not in current_resources:
        current_resources.append(resource.title)
        node.resources = current_resources
        db.commit()
        return {"message": "资源已添加到节点", "resources": current_resources}
    return {"message": "资源已存在于节点中", "resources": current_resources}


@router.delete("/path/{path_id}")
def delete_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除学习路径及其所有节点"""
    path = (
        db.query(LearningPath)
        .filter(LearningPath.id == path_id, LearningPath.user_id == current_user.id)
        .first()
    )
    if not path:
        raise HTTPException(status_code=404, detail="学习路径不存在")

    # 级联删除所有节点
    db.query(PathNode).filter(PathNode.path_id == path_id).delete()
    db.delete(path)
    db.commit()
    return {"message": "学习路径已删除"}
