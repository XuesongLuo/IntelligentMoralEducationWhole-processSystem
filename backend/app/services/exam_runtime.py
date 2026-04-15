import json
import socket
import threading
import time
import urllib.error
import urllib.request

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
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


def _stringify_answer(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "；".join(_stringify_answer(item) for item in value if item is not None)
    if isinstance(value, dict):
        selected = value.get("selected")
        extras = value.get("extras")
        parts = []
        if isinstance(selected, list):
            for item in selected:
                item_text = _stringify_answer(item)
                extra_text = ""
                if isinstance(extras, dict):
                    extra_val = extras.get(item)
                    extra_text = _stringify_answer(extra_val).strip()
                parts.append(f"{item_text}({extra_text})" if extra_text else item_text)
            if parts:
                return "；".join(parts)
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _stringify_correct_answer(value) -> str | None:
    if value is None:
        return None
    text = _stringify_answer(value).strip()
    return text or None


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
    student_identifier = (
        user.student_profile.student_no
        if user.student_profile
        else user.teacher_profile.teacher_no
        if user.teacher_profile
        else str(user.id)
    )
    answer_items = []
    for answer in answers:
        question = question_map.get(answer.question_id)
        if not question:
            continue
        answer_items.append(
            {
                "question": question.title,
                "answer": _stringify_answer(answer.answer_json),
                "correctAnswer": _stringify_correct_answer(question.answer_json),
            }
        )

    payload = {
        "studentId": student_identifier,
        "examTime": str(attempt.duration_seconds or 0),
        "examContent": answer_items,
    }
    if settings.AI_ANALYSIS_MODEL:
        payload["model"] = settings.AI_ANALYSIS_MODEL
    return payload


def _map_evaluation_result_to_callback_payload(attempt_id: int, response_payload: dict) -> dict:
    data = response_payload.get("data") if isinstance(response_payload, dict) else None
    if not isinstance(data, dict):
        raise ValueError("missing response data")

    def dim_score(name: str):
        dim = data.get(name)
        if not isinstance(dim, dict):
            return None
        score = dim.get("score")
        return float(score) if score is not None else None

    return {
        "attempt_id": attempt_id,
        "status": "completed",
        "score_research_integrity": dim_score("scientificIntegrity"),
        "score_communication_anxiety": dim_score("communicationAnxiety"),
        "score_career_identity": dim_score("careerIdentity"),
        "score_humanistic_care": dim_score("humanisticCare"),
        "score_comprehensive_balance": dim_score("balancedDevelopment"),
        "total_score": data.get("overallScore"),
        "summary": data.get("overallComment") or "",
        "raw_provider_response": response_payload,
    }


def dispatch_ai_analysis(payload: dict, attempt_id: int | None = None) -> tuple[bool, str, dict | None]:
    if not settings.AI_ANALYSIS_WEBHOOK_URL:
        return False, "AI webhook is not configured", None

    request = urllib.request.Request(
        settings.AI_ANALYSIS_WEBHOOK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8") if response else ""
        if not body:
            if attempt_id is not None:
                return False, "AI response is empty", None
            return True, "", None

        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            if attempt_id is not None:
                return False, "AI response format is invalid", None
            return True, "", None

        if attempt_id is None:
            return True, "", None
        mapped_payload = _map_evaluation_result_to_callback_payload(attempt_id, parsed)
        return True, "", mapped_payload
    except ValueError as exc:
        return False, str(exc), None
    except json.JSONDecodeError:
        if attempt_id is not None:
            return False, "AI response is not valid JSON", None
        return True, "", None
    except (TimeoutError, socket.timeout):
        return False, "AI request timed out", None
    except urllib.error.URLError as exc:
        return False, str(exc), None
    except Exception as exc:
        return False, f"AI request failed: {exc}", None


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


def _mark_ai_failed(db: Session, attempt_id: int, error_message: str) -> None:
    attempt = db.query(AssessmentAttempt).filter(AssessmentAttempt.id == attempt_id).first()
    if not attempt:
        return
    report = db.query(AssessmentAIReport).filter(AssessmentAIReport.attempt_id == attempt_id).first()
    if not report:
        report = AssessmentAIReport(
            attempt_id=attempt_id,
            status="failed",
            summary="AI 分析任务发送失败",
            raw_response_json={"status": "failed", "message": error_message},
        )
        db.add(report)
    else:
        report.status = "failed"
        report.summary = "AI 分析任务发送失败"
        report.raw_response_json = {"status": "failed", "message": error_message}
    attempt.status = "submitted"


def _run_ai_analysis_job(attempt_id: int) -> None:
    db: Session = SessionLocal()
    try:
        attempt = db.query(AssessmentAttempt).filter(AssessmentAttempt.id == attempt_id).first()
        if not attempt:
            return
        paper = db.query(AssessmentPaper).filter(AssessmentPaper.id == attempt.paper_id).first()
        user = db.query(AuthUser).filter(AuthUser.id == attempt.user_id).first()
        if not paper or not user:
            _mark_ai_failed(db, attempt_id, "attempt context missing")
            db.commit()
            return

        questions = (
            db.query(AssessmentQuestion)
            .join(AssessmentAnswer, AssessmentAnswer.question_id == AssessmentQuestion.id)
            .filter(AssessmentAnswer.attempt_id == attempt_id)
            .all()
        )
        answers = (
            db.query(AssessmentAnswer)
            .filter(AssessmentAnswer.attempt_id == attempt_id)
            .all()
        )

        payload_json = build_ai_payload(
            attempt=attempt,
            paper=paper,
            user=user,
            questions=questions,
            answers=answers,
        )
        success, error_message, ai_result_payload = dispatch_ai_analysis(
            payload_json,
            attempt_id=attempt_id,
        )

        if not success:
            _mark_ai_failed(db, attempt_id, error_message)
            db.commit()
            return

        if ai_result_payload:
            apply_ai_callback(db, attempt_id=attempt_id, payload=ai_result_payload)
            db.commit()
            return
    except Exception as exc:
        db.rollback()
        _mark_ai_failed(db, attempt_id, f"AI async job failed: {exc}")
        db.commit()
    finally:
        db.close()


def trigger_ai_analysis_async(attempt_id: int) -> None:
    thread = threading.Thread(
        target=_run_ai_analysis_job,
        args=(attempt_id,),
        daemon=True,
        name=f"ai-analysis-{attempt_id}",
    )
    thread.start()
