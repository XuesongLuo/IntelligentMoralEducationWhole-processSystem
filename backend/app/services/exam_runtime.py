import json
import time
import urllib.error
import urllib.request

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.redis import get_redis
from app.models.assessment_ai_report import AssessmentAIReport
from app.models.assessment_answer import AssessmentAnswer
from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment_paper import AssessmentPaper
from app.models.assessment_question import AssessmentQuestion
from app.models.auth_user import AuthUser


settings = get_settings()
redis_client = get_redis()


DIMENSION_FIELDS = [
    "score_research_integrity",
    "score_communication_anxiety",
    "score_career_identity",
    "score_humanistic_care",
    "score_comprehensive_balance",
]


def session_key(user_id: int, paper_id: int) -> str:
    return f"exam:session:{user_id}:{paper_id}"


def submit_lock_key(user_id: int, paper_id: int) -> str:
    return f"exam:submit-lock:{user_id}:{paper_id}"


def _write_exam_session(
    key: str,
    paper_id: int,
    exam_type: str,
    duration_seconds: int,
    client_session_id: str | None = None,
) -> None:
    now = int(time.time())
    redis_client.hset(
        key,
        mapping={
            "paper_id": paper_id,
            "exam_type": exam_type,
            "started_at": now,
            "deadline_at": now + max(duration_seconds, 1),
            "last_heartbeat_at": now,
            "active_seconds": 0,
            "submitted": 0,
            "client_session_id": client_session_id or "",
        },
    )
    redis_client.expire(key, max(duration_seconds + 86400, 86400))


def ensure_exam_session(
    user_id: int,
    paper_id: int,
    exam_type: str,
    duration_seconds: int,
    client_session_id: str | None = None,
) -> dict:
    key = session_key(user_id, paper_id)
    if not redis_client.exists(key):
        _write_exam_session(key, paper_id, exam_type, duration_seconds, client_session_id)
        data = redis_client.hgetall(key)
        return _build_session_state(data, int(time.time()), False)

    data = redis_client.hgetall(key)
    submitted = str(data.get("submitted", "0")) == "1"
    cached_exam_type = str(data.get("exam_type", ""))
    cached_client_session_id = str(data.get("client_session_id", ""))
    session_mismatch = bool(client_session_id and cached_client_session_id and cached_client_session_id != client_session_id)

    # Re-opening a paper after it was already submitted should create a fresh session.
    if submitted or cached_exam_type != exam_type:
        _write_exam_session(key, paper_id, exam_type, duration_seconds, client_session_id)
        data = redis_client.hgetall(key)
        return _build_session_state(data, int(time.time()), False)

    if client_session_id and cached_client_session_id != client_session_id:
        redis_client.hset(key, "client_session_id", client_session_id)
        data["client_session_id"] = client_session_id

    redis_client.expire(key, max(duration_seconds + 86400, 86400))
    return _build_session_state(data, int(time.time()), session_mismatch)


def _build_session_state(data: dict, now: int, session_mismatch: bool) -> dict:
    deadline_at = int(data.get("deadline_at", now))
    remaining_seconds = max(0, deadline_at - now)
    return {
        "active_seconds": int(data.get("active_seconds", 0)),
        "last_heartbeat_at": int(data.get("last_heartbeat_at", now)),
        "submitted": str(data.get("submitted", "0")) == "1",
        "remaining_seconds": remaining_seconds,
        "deadline_at": deadline_at,
        "client_session_id": str(data.get("client_session_id", "")),
        "session_mismatch": session_mismatch,
    }


def heartbeat_exam_session(
    user_id: int,
    paper_id: int,
    exam_type: str,
    duration_seconds: int,
    client_session_id: str | None = None,
) -> dict:
    ensure_exam_session(user_id, paper_id, exam_type, duration_seconds, client_session_id)
    key = session_key(user_id, paper_id)
    now = int(time.time())
    data = redis_client.hgetall(key)

    if str(data.get("submitted", "0")) == "1":
        return _build_session_state(data, now, False)

    last_heartbeat_at = int(data.get("last_heartbeat_at", now))
    active_seconds = int(data.get("active_seconds", 0))
    delta = max(0, min(now - last_heartbeat_at, 30))
    active_seconds += delta

    redis_client.hset(
        key,
        mapping={
            "last_heartbeat_at": now,
            "active_seconds": active_seconds,
        },
    )
    redis_client.expire(key, max(duration_seconds + 86400, 86400))
    data["active_seconds"] = active_seconds
    data["last_heartbeat_at"] = now
    return _build_session_state(data, now, False)


def finalize_exam_session(
    user_id: int,
    paper_id: int,
    exam_type: str,
    duration_seconds: int,
    client_session_id: str | None = None,
) -> int:
    state = heartbeat_exam_session(user_id, paper_id, exam_type, duration_seconds, client_session_id)
    if state["submitted"]:
        raise ValueError("exam already submitted")
    key = session_key(user_id, paper_id)
    redis_client.hset(key, "submitted", 1)
    return int(state["active_seconds"])


def acquire_submit_lock(user_id: int, paper_id: int, expire_seconds: int = 20) -> bool:
    return bool(redis_client.set(submit_lock_key(user_id, paper_id), "1", nx=True, ex=expire_seconds))


def release_submit_lock(user_id: int, paper_id: int) -> None:
    redis_client.delete(submit_lock_key(user_id, paper_id))


def clear_exam_session(user_id: int, paper_id: int) -> None:
    redis_client.delete(session_key(user_id, paper_id))


def build_ai_payload(
    *,
    attempt: AssessmentAttempt,
    paper: AssessmentPaper,
    user: AuthUser,
    questions: list[AssessmentQuestion],
    answers: list[AssessmentAnswer],
) -> dict:
    question_map = {question.id: question for question in questions}
    answer_items = []
    for answer in answers:
        question = question_map.get(answer.question_id)
        if not question:
            continue
        answer_items.append(
            {
                "question_id": question.id,
                "question_type": question.question_type,
                "title": question.title,
                "answer": answer.answer_json,
                "score": question.score,
            }
        )

    return {
        "attempt_id": attempt.id,
        "paper": {
            "id": paper.id,
            "title": paper.title,
            "paper_type": paper.paper_type,
        },
        "user": {
            "id": user.id,
            "role": user.role,
            "real_name": user.real_name,
            "student_no": user.student_profile.student_no if user.student_profile else None,
            "teacher_no": user.teacher_profile.teacher_no if user.teacher_profile else None,
        },
        "submitted_at": attempt.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if attempt.submitted_at else "",
        "duration_seconds": attempt.duration_seconds,
        "answers": answer_items,
        "callback": {
            "url": f"{settings.BACKEND_PUBLIC_BASE_URL}{settings.API_V1_PREFIX}/exam/ai/callback",
            "method": "POST",
            "header_name": "X-AI-Callback-Token",
            "token": settings.AI_CALLBACK_TOKEN,
        },
    }


def dispatch_ai_analysis(payload: dict) -> tuple[bool, str]:
    if not settings.AI_ANALYSIS_WEBHOOK_URL:
        return False, "AI webhook is not configured"

    request = urllib.request.Request(
        settings.AI_ANALYSIS_WEBHOOK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as response:
            response.read()
        return True, ""
    except urllib.error.URLError as exc:
        return False, str(exc)


def apply_ai_callback(
    db: Session,
    *,
    attempt_id: int,
    payload: dict,
) -> AssessmentAIReport:
    attempt = db.query(AssessmentAttempt).filter(AssessmentAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError("attempt not found")

    report = db.query(AssessmentAIReport).filter(AssessmentAIReport.attempt_id == attempt_id).first()
    if not report:
        report = AssessmentAIReport(attempt_id=attempt_id, status="pending")
        db.add(report)
        db.flush()

    status = payload.get("status") or "completed"
    report.status = status

    for field in DIMENSION_FIELDS:
        value = payload.get(field)
        setattr(report, field, float(value) if value is not None else None)

    total_score = payload.get("total_score")
    report.total_score = float(total_score) if total_score is not None else None
    report.summary = payload.get("summary") or payload.get("comprehensive_advice") or ""
    report.raw_response_json = payload

    attempt.status = "completed" if status == "completed" else "ai_processing" if status == "processing" else "submitted"
    if report.total_score is not None:
        attempt.total_score = round(report.total_score)

    return report
