from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learning import LearningPath, PathNode, WrongAnswer, DailyCheckIn

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    返回用户真实学习统计数据：
    - 总做题数 / 答对数 / 答错数 / 准确率
    - 活跃路径数 / 已完成节点数 / 总节点数
    - 路径进度列表
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

    # 聚合答题数据
    attempted_nodes = [n for n in nodes if n.quiz_score > 0]
    total_attempted_questions = sum(n.quiz_total for n in attempted_nodes)
    total_correct = sum(n.quiz_score for n in nodes)

    total_wrong = total_attempted_questions - total_correct
    accuracy = round((total_correct / total_attempted_questions) * 100) if total_attempted_questions > 0 else 0

    completed_nodes = sum(1 for n in nodes if n.status == "completed")
    active_nodes = sum(1 for n in nodes if n.status == "active")
    total_nodes = len(nodes)

    # 路径进度列表
    path_progress = []
    for path in paths:
        path_nodes = [n for n in nodes if n.path_id == path.id]
        if path_nodes:
            avg_progress = round(sum(n.progress for n in path_nodes) / len(path_nodes))
            path_progress.append({
                "id": path.id,
                "title": path.title,
                "progress": avg_progress,
                "total_nodes": len(path_nodes),
                "completed_nodes": sum(1 for n in path_nodes if n.status == "completed"),
            })

    return {
        "total_questions_answered": total_attempted_questions,
        "total_correct": total_correct,
        "total_wrong": total_wrong,
        "accuracy": accuracy,
        "total_paths": len(paths),
        "total_nodes": total_nodes,
        "completed_nodes": completed_nodes,
        "active_nodes": active_nodes,
        "path_progress": path_progress,
    }


@router.get("/wrong-answers")
async def get_wrong_answers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户所有错题，按节点分组"""
    wrongs = (
        db.query(WrongAnswer)
        .filter(WrongAnswer.user_id == current_user.id)
        .order_by(WrongAnswer.created_at.desc())
        .all()
    )
    grouped = {}
    for w in wrongs:
        key = str(w.node_id)
        if key not in grouped:
            grouped[key] = {
                "node_id": w.node_id,
                "node_title": w.node_title,
                "count": 0,
                "items": [],
            }
        grouped[key]["count"] += 1
        grouped[key]["items"].append({
            "id": w.id,
            "question": w.question,
            "options": w.options or [],
            "user_answer": w.user_answer,
            "correct_answer": w.correct_answer,
            "explanation": w.explanation,
            "created_at": w.created_at.isoformat() if w.created_at else "",
        })

    return {
        "total_wrong": len(wrongs),
        "groups": list(grouped.values()),
    }


@router.delete("/wrong-answers/{wrong_id}")
def delete_wrong_answer(
    wrong_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除单道错题"""
    wrong = (
        db.query(WrongAnswer)
        .filter(WrongAnswer.id == wrong_id, WrongAnswer.user_id == current_user.id)
        .first()
    )
    if not wrong:
        raise HTTPException(status_code=404, detail="错题不存在")
    db.delete(wrong)
    db.commit()
    return {"message": "错题已消灭"}


@router.post("/check-in")
def daily_check_in(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """每日打卡 — 登录即打卡，同时汇总当日答题数"""
    from datetime import date as date_mod
    today = date_mod.today().isoformat()

    record = (
        db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == current_user.id, DailyCheckIn.date == today)
        .first()
    )

    # 汇总当日答题数据（从 PathNode 的 quiz 更新时间推断）
    from datetime import datetime, timedelta
    today_start = datetime.combine(date_mod.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)
    today_nodes = (
        db.query(PathNode)
        .filter(
            PathNode.path_id.in_(
                [p.id for p in db.query(LearningPath).filter(LearningPath.user_id == current_user.id).all()]
            ),
            PathNode.updated_at >= today_start,
            PathNode.updated_at < today_end,
            PathNode.quiz_score > 0,
        )
        .all()
    )
    correct_count = sum(n.quiz_score for n in today_nodes)
    total_count = sum(n.quiz_total for n in today_nodes)

    if record:
        record.correct_count = max(record.correct_count, correct_count)
        record.total_count = max(record.total_count, total_count)
    else:
        record = DailyCheckIn(
            user_id=current_user.id,
            date=today,
            correct_count=correct_count,
            total_count=total_count,
        )
        db.add(record)
    db.commit()

    return {
        "date": today,
        "correct_count": max(record.correct_count, correct_count),
        "total_count": max(record.total_count, total_count),
        "level": "dark" if max(record.correct_count, correct_count) >= 6 else "light",
    }


@router.get("/check-in-calendar")
def get_check_in_calendar(
    days: int = 90,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取最近 N 天的打卡日历"""
    from datetime import date as date_mod, timedelta
    today = date_mod.today()
    start = today - timedelta(days=days - 1)

    records = (
        db.query(DailyCheckIn)
        .filter(
            DailyCheckIn.user_id == current_user.id,
            DailyCheckIn.date >= start.isoformat(),
        )
        .all()
    )
    record_map = {r.date: r for r in records}

    calendar = []
    for i in range(days):
        d = start + timedelta(days=i)
        d_str = d.isoformat()
        rec = record_map.get(d_str)
        if rec:
            level = "dark" if rec.correct_count >= 6 else "light"
        else:
            level = "none"
        calendar.append({
            "date": d_str,
            "level": level,
            "correct_count": rec.correct_count if rec else 0,
            "total_count": rec.total_count if rec else 0,
        })

    # 统计
    active_days = sum(1 for c in calendar if c["level"] != "none")
    streak = 0
    for c in reversed(calendar):
        if c["level"] != "none":
            streak += 1
        else:
            break

    return {
        "calendar": calendar,
        "active_days": active_days,
        "streak": streak,
        "total_days": days,
    }
