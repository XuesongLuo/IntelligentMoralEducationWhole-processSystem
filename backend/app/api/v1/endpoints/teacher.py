from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.auth_user import AuthUser
from app.models.student_user import StudentUser
from app.models.teacher_user import TeacherUser
from app.models.student_roster import StudentRoster
from app.models.teacher_roster import TeacherRoster
from app.models.resource_category import ResourceCategory
from app.models.learning_resource import LearningResource
from app.models.user_resource_record import UserResourceRecord
from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment_ai_report import AssessmentAIReport
from app.models.assessment_answer import AssessmentAnswer
from app.models.assessment_paper import AssessmentPaper
from app.models.assessment_paper_question import AssessmentPaperQuestion
from app.models.assessment_question import AssessmentQuestion
from app.schemas.common import ResponseModel
from app.schemas.exam import (
    ExamHeartbeatData,
    ExamHeartbeatRequest,
    ExamHeartbeatResponseModel,
    ExamInfoData,
    ExamInfoResponseModel,
    ExamNoticeData,
    ExamNoticeResponseModel,
    ExamPaperData,
    ExamPaperResponseModel,
    ExamQuestionItem,
    ExamQuestionOption,
    ExamResultAnalysis,
    ExamResultAnalysisDimension,
    ExamResultAnswerItem,
    ExamResultDetailData,
    ExamResultDetailResponseModel,
    ExamResultListData,
    ExamResultListItem,
    ExamResultListResponseModel,
    SubmitExamRequest,
    SubmitExamResponseData,
    SubmitExamResponseModel,
)
from app.schemas.resource import (
    ResourceCategoryListData,
    ResourceCategoryListResponseModel,
    ResourceHeartbeatData,
    ResourceHeartbeatRequest,
    ResourceHeartbeatResponseModel,
    ResourceItemResponseModel,
    ResourceListItem,
    ResourceListResponseModel,
    ResourceUpsertRequest,
    ResourceVisibilityRequest,
    ResourceVisitData,
    ResourceVisitResponseModel,
)
from app.services.exam_runtime import (
    acquire_submit_lock,
    clear_exam_session,
    ensure_exam_session,
    finalize_exam_session,
    heartbeat_exam_session,
    release_submit_lock,
    trigger_ai_analysis_async,
)
from app.services.resource_runtime import (
    build_category_progress_list,
    build_resource_list,
    get_total_ai_usage_duration,
    heartbeat_resource_session,
    mark_resource_completed,
)
from app.schemas.student import (
    StudentHomeData,
    StudentHomeProgressItem,
    StudentHomeResponseModel,
    StudentHomeScoreDimension,
)

router = APIRouter(prefix="/teacher", tags=["teacher"])


class StudentRosterUpsertRequest(BaseModel):
    student_no: str
    real_name: str
    is_enabled: bool = True


class TeacherRosterUpsertRequest(BaseModel):
    teacher_no: str
    real_name: str
    is_enabled: bool = True


class TeacherFilterExportRequest(BaseModel):
    accountScope: str
    paperIds: list[int]


DIMENSION_CONFIG = [
    ("research_integrity", "科研诚信脆弱型", "score_research_integrity"),
    ("communication_anxiety", "医患沟通焦虑型", "score_communication_anxiety"),
    ("career_identity", "职业认同模糊型", "score_career_identity"),
    ("humanistic_care", "人文关怀缺失型", "score_humanistic_care"),
    ("comprehensive_balance", "综合发展均衡型", "score_comprehensive_balance"),
]

EXAM_NOTICE_MAP = {
    "survey": [
        "所有题目均为必答题。",
        "考试开始后请勿刷新或关闭浏览器。",
        "请根据真实想法独立作答。",
        "提交后答案将无法修改。",
    ],
    "integrity": [
        "所有题目均为必答题。",
        "请独立完成，不得切换账号代答。",
        "倒计时结束后系统会自动提交。",
        "请认真核对后再提交试卷。",
    ],
    "ideology": [
        "所有题目均为必答题。",
        "请结合题目情境独立完成作答。",
        "考试过程中请勿离开页面或切换账号。",
        "倒计时结束后系统会自动提交试卷。",
    ],
}

EXPORT_DIMENSION_COLUMNS = [
    ("score_research_integrity", "科研诚信"),
    ("score_communication_anxiety", "医患沟通"),
    ("score_career_identity", "职业认同"),
    ("score_humanistic_care", "人文关怀"),
    ("score_comprehensive_balance", "综合发展"),
]


SURVEY_MASK_PHONE_KEYWORDS = ("联系电话", "手机", "手机号")
SURVEY_MASK_EMAIL_KEYWORDS = ("电子邮箱", "邮箱", "email", "e-mail")
SURVEY_MASK_FULL_HIDE_KEYWORDS = ("姓名", "导师姓名", "德育导师姓名")
SURVEY_KEEP_VISIBLE_KEYWORDS = (
    "性别",
    "出生年月",
    "学号",
    "政治面貌",
    "年级",
    "培养类型",
    "专业",
    "所在轮转",
)


def map_paper_type_label(paper_type: str) -> str:
    return {
        "survey": "问卷",
        "integrity": "科研诚信试卷",
        "ideology": "思政试卷",
    }.get(paper_type, paper_type)


def format_answer_for_export(answer: list | dict | str | bool | int | float | None) -> str:
    if answer is None or answer == "":
        return ""
    if isinstance(answer, bool):
        return "正确" if answer else "错误"
    if isinstance(answer, list):
        return "；".join(str(item) for item in answer if item not in (None, ""))
    if isinstance(answer, dict):
        selected = answer.get("selected")
        extras = answer.get("extras", {}) if isinstance(answer.get("extras"), dict) else {}
        selected_items = selected if isinstance(selected, list) else ([selected] if selected else [])
        if selected_items:
            parts = []
            for item in selected_items:
                item_str = str(item)
                extra_value = extras.get(item)
                if isinstance(extra_value, list):
                    extra_text = "、".join(str(v) for v in extra_value if str(v).strip())
                elif extra_value is None:
                    extra_text = ""
                else:
                    extra_text = str(extra_value).strip()
                if extra_text:
                    parts.append(f"{item_str}（补充：{extra_text}）")
                else:
                    parts.append(item_str)
            return "；".join(parts)
        return str(answer)
    return str(answer)


def build_export_workbook(rows: list[list[str]], question_count: int) -> BytesIO:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "结果导出"

    headers = [
        "学号",
        "姓名",
        "类型",
        "考试名称",
        "开始时间",
        "持续时长",
    ]
    headers.extend([f"题目{i}" for i in range(1, question_count + 1)])
    for _, dimension_label in EXPORT_DIMENSION_COLUMNS:
        headers.extend([f"{dimension_label}评分", f"{dimension_label}评语"])
    sheet.append(headers)

    for row in rows:
        sheet.append(row)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def build_export_workbook_by_mode(
    rows: list[list[str]],
    question_count: int,
    export_mode: str,
) -> BytesIO:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "结果导出"

    if export_mode == "survey":
        type_header = "类型(问卷、思政试卷或科研诚信试卷)"
        name_header = "问卷名称"
    else:
        type_header = "类型(问卷、试卷)"
        name_header = "考试名称"

    headers = [
        "学号",
        "姓名",
        type_header,
        name_header,
        "开始时间",
        "持续时长",
    ]
    headers.extend([f"题目{i}" for i in range(1, question_count + 1)])
    for _, dimension_label in EXPORT_DIMENSION_COLUMNS:
        headers.extend([f"{dimension_label}评分", f"{dimension_label}评语"])
    sheet.append(headers)

    for row in rows:
        sheet.append(row)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def fetch_attempt_export_data(db: Session, attempt_id: int, user_id: int):
    row = (
        db.query(AssessmentAttempt, AssessmentPaper, AssessmentAIReport, AuthUser)
        .join(AssessmentPaper, AssessmentPaper.id == AssessmentAttempt.paper_id)
        .outerjoin(AssessmentAIReport, AssessmentAIReport.attempt_id == AssessmentAttempt.id)
        .join(AuthUser, AuthUser.id == AssessmentAttempt.user_id)
        .filter(
            AssessmentAttempt.id == attempt_id,
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.submitted_at.isnot(None),
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="考试结果不存在")
    return row


def get_user_no(user: AuthUser) -> str:
    if user.role == "teacher" and user.teacher_profile:
        return user.teacher_profile.teacher_no
    if user.role == "student" and user.student_profile:
        return user.student_profile.student_no
    return ""


def mask_full_hidden(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    star_count = max(2, min(len(text), 8))
    return "*" * star_count


def mask_phone(value: str) -> str:
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if not digits:
        return ""
    length = len(digits)
    if length >= 11:
        return f"{digits[:3]}{'*' * max(length - 7, 4)}{digits[-4:]}"
    if length <= 2:
        return digits[0] + "*"
    if length <= 4:
        return f"{digits[0]}{'*' * (length - 2)}{digits[-1]}"
    return f"{digits[:2]}{'*' * max(length - 4, 1)}{digits[-2:]}"


def mask_email(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if "@" not in text:
        return mask_full_hidden(text)
    local, domain = text.split("@", 1)
    if not domain:
        return mask_full_hidden(text)
    return f"{'*' * max(len(local), 3)}@{domain}"


def apply_survey_mask_by_title(question_title: str, answer_text: str) -> str:
    title = (question_title or "").strip().lower()
    if not title:
        return answer_text

    for keyword in SURVEY_MASK_PHONE_KEYWORDS:
        if keyword.lower() in title:
            return mask_phone(answer_text)
    for keyword in SURVEY_MASK_EMAIL_KEYWORDS:
        if keyword.lower() in title:
            return mask_email(answer_text)
    for keyword in SURVEY_MASK_FULL_HIDE_KEYWORDS:
        if keyword.lower() in title:
            return mask_full_hidden(answer_text)
    for keyword in SURVEY_KEEP_VISIBLE_KEYWORDS:
        if keyword.lower() in title:
            return answer_text
    return answer_text


def fetch_attempt_answers_by_order(
    db: Session,
    attempt_id: int,
    paper_id: int,
    survey_masking: bool = False,
) -> list[str]:
    answer_rows = (
        db.query(
            AssessmentPaperQuestion.sort_order,
            AssessmentQuestion.title,
            AssessmentAnswer.answer_json,
        )
        .join(
            AssessmentQuestion,
            AssessmentQuestion.id == AssessmentPaperQuestion.question_id,
        )
        .outerjoin(
            AssessmentAnswer,
            (AssessmentAnswer.question_id == AssessmentQuestion.id)
            & (AssessmentAnswer.attempt_id == attempt_id),
        )
        .filter(AssessmentPaperQuestion.paper_id == paper_id)
        .order_by(AssessmentPaperQuestion.sort_order.asc())
        .all()
    )
    result = []
    for _, title, answer in answer_rows:
        answer_text = format_answer_for_export(answer)
        if survey_masking:
            answer_text = apply_survey_mask_by_title(title or "", answer_text)
        result.append(answer_text)
    return result


def build_export_row(
    attempt: AssessmentAttempt,
    paper: AssessmentPaper,
    report: AssessmentAIReport | None,
    user: AuthUser,
    answers: list[str],
    export_mode: str | None = None,
) -> list[str]:
    display_name = user.real_name
    if paper.paper_type == "survey":
        display_name = mask_full_hidden(display_name)

    if export_mode == "exam":
        type_label = "问卷" if paper.paper_type == "survey" else "试卷"
    else:
        type_label = map_paper_type_label(paper.paper_type)

    row = [
        get_user_no(user),
        display_name,
        type_label,
        paper.title,
        format_datetime(attempt.started_at),
        f"{max(int((attempt.duration_seconds or 0) / 60), 0)} min",
    ]
    row.extend(answers)
    for attr, label in EXPORT_DIMENSION_COLUMNS:
        score = getattr(report, attr, None) if report else None
        score_text = "" if score is None else str(round(float(score), 1))
        reason_text = build_dimension_reason(float(score), label) if score is not None else ""
        row.extend([score_text, reason_text])
    return row


def format_datetime(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def build_export_rows_and_question_count(
    db: Session,
    rows: list[tuple[AssessmentAttempt, AssessmentPaper, AssessmentAIReport | None, AuthUser]],
    export_mode: str | None = None,
) -> tuple[list[list[str]], int]:
    export_rows: list[list[str]] = []
    max_question_count = 0
    for attempt, paper, report, user in rows:
        answers = fetch_attempt_answers_by_order(
            db,
            attempt.id,
            paper.id,
            survey_masking=(paper.paper_type == "survey"),
        )
        max_question_count = max(max_question_count, len(answers))
        export_rows.append(
            build_export_row(
                attempt=attempt,
                paper=paper,
                report=report,
                user=user,
                answers=answers,
                export_mode=export_mode,
            )
        )

    for row in export_rows:
        answer_count = len(row) - 6 - (2 * len(EXPORT_DIMENSION_COLUMNS))
        if answer_count < max_question_count:
            insert_index = 6 + answer_count
            row[insert_index:insert_index] = [""] * (max_question_count - answer_count)

    return export_rows, max_question_count


def build_dimension_reason(score: float, dimension_name: str) -> str:
    if score >= 85:
        level_text = "表现稳定"
    elif score >= 70:
        level_text = "具备一定基础"
    else:
        level_text = "仍有提升空间"
    return f"{dimension_name}{level_text}，建议结合训练内容持续复盘。"


def build_result_analysis(report: AssessmentAIReport | None) -> ExamResultAnalysis:
    if not report:
        return ExamResultAnalysis(dimensions=[], summary="")
    if report.status != "completed":
        return ExamResultAnalysis(dimensions=[], summary=report.summary or "")

    dimensions = []
    for _, name, attr in DIMENSION_CONFIG:
        score = getattr(report, attr)
        if score is None:
            continue
        dimensions.append(
            ExamResultAnalysisDimension(
                dimension=name,
                score=round(float(score), 1),
                reason=build_dimension_reason(float(score), name),
            )
        )

    return ExamResultAnalysis(
        dimensions=dimensions,
        summary=report.summary or "",
    )


def map_question_type(question_type: str) -> str:
    mapping = {
        "boolean": "judge",
        "fill_blank": "blank",
    }
    return mapping.get(question_type, question_type)


def build_question_options(question: AssessmentQuestion) -> list[ExamQuestionOption]:
    options = question.options_json if isinstance(question.options_json, list) else []
    result = []
    for item in options:
        if isinstance(item, dict):
            label = item.get("text") or item.get("label") or ""
            value = item.get("label")
            if value is None:
                value = item.get("value")
            result.append(ExamQuestionOption(label=str(label), value=value))
    return result


def get_active_paper(db: Session, exam_type: str) -> AssessmentPaper | None:
    return (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.paper_type == exam_type,
            AssessmentPaper.is_active == True,
        )
        .order_by(AssessmentPaper.version_no.desc(), AssessmentPaper.id.desc())
        .first()
    )


def get_fixed_paper_for_user(db: Session, user_id: int, exam_type: str) -> AssessmentPaper:
    if exam_type in {"integrity", "ideology"}:
        completed_count = (
            db.query(func.count(AssessmentAttempt.id))
            .filter(
                AssessmentAttempt.user_id == user_id,
                AssessmentAttempt.paper_type == exam_type,
                AssessmentAttempt.submitted_at.isnot(None),
            )
            .scalar()
            or 0
        )
        paper_query = (
            db.query(AssessmentPaper)
            .filter(
                AssessmentPaper.paper_type == exam_type,
                AssessmentPaper.is_active == True,
            )
        )
        paper = (
            paper_query.order_by(AssessmentPaper.version_no.asc(), AssessmentPaper.id.asc()).first()
            if completed_count == 0
            else paper_query.order_by(func.rand()).first()
        )
        if paper:
            return paper
        raise HTTPException(status_code=404, detail="缺少试卷1")

    completed_count = (
        db.query(func.count(AssessmentAttempt.id))
        .filter(
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.paper_type == exam_type,
            AssessmentAttempt.submitted_at.isnot(None),
        )
        .scalar()
        or 0
    )
    target_version = 1 if completed_count == 0 else 2
    active_count = (
        db.query(func.count(AssessmentPaper.id))
        .filter(
            AssessmentPaper.paper_type == exam_type,
            AssessmentPaper.is_active == True,
        )
        .scalar()
        or 0
    )
    paper = (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.paper_type == exam_type,
            AssessmentPaper.version_no == target_version,
            AssessmentPaper.is_active == True,
        )
        .order_by(AssessmentPaper.id.asc())
        .first()
    )
    if paper:
        return paper
    missing_version = 1 if active_count == 0 else target_version
    raise HTTPException(status_code=404, detail=f"缺少试卷{missing_version}")


def resolve_allowed_paper_for_user(
    db: Session,
    user_id: int,
    exam_type: str,
    exam_id: int,
) -> AssessmentPaper:
    paper = (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.id == exam_id,
            AssessmentPaper.paper_type == exam_type,
            AssessmentPaper.is_active == True,
        )
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    if exam_type == "survey":
        selected_paper = get_fixed_paper_for_user(db, user_id, exam_type)
        if paper.id != selected_paper.id:
            raise HTTPException(status_code=409, detail="当前考试应按固定试卷规则进行")
    return paper


def build_paper_response(db: Session, paper: AssessmentPaper, session_state: dict | None = None) -> ExamPaperData:
    questions = (
        db.query(AssessmentQuestion, AssessmentPaperQuestion.sort_order)
        .join(AssessmentPaperQuestion, AssessmentPaperQuestion.question_id == AssessmentQuestion.id)
        .filter(AssessmentPaperQuestion.paper_id == paper.id)
        .order_by(AssessmentPaperQuestion.sort_order.asc(), AssessmentQuestion.id.asc())
        .all()
    )

    return ExamPaperData(
        examId=paper.id,
        paperName=paper.title,
        durationSeconds=paper.duration_seconds,
        remainingSeconds=session_state.get("remaining_seconds") if session_state else paper.duration_seconds,
        sessionMismatch=session_state.get("session_mismatch", False) if session_state else False,
        questions=[
            ExamQuestionItem(
                id=question.id,
                type=map_question_type(question.question_type),
                sectionTitle=question.section_title or "",
                title=question.title,
                options=build_question_options(question),
            )
            for question, _ in questions
        ],
    )


def normalize_answer_for_storage(question: AssessmentQuestion, answer):
    question_type = map_question_type(question.question_type)
    if question_type == "multiple":
        if isinstance(answer, list):
            return answer
        if answer in (None, ""):
            return []
        return [answer]
    if question_type == "judge":
        if isinstance(answer, bool):
            return answer
        if str(answer).lower() == "true":
            return True
        if str(answer).lower() == "false":
            return False
        return answer
    return answer


def normalize_standard_answer(question: AssessmentQuestion):
    return normalize_answer_for_storage(question, question.answer_json)


def build_home_data(target_user: AuthUser, db: Session) -> StudentHomeData:
    user_no = (
        target_user.teacher_profile.teacher_no
        if target_user.role == "teacher" and target_user.teacher_profile
        else target_user.student_profile.student_no
        if target_user.role == "student" and target_user.student_profile
        else ""
    )

    category_progress_items = build_category_progress_list(db, target_user.id)
    study_progress_list = [
        StudentHomeProgressItem(
            id=item.id,
            name=item.name,
            progress=item.progress,
            leftCount=item.remainingCount,
        )
        for item in category_progress_items
    ]

    simulation_completion = (
        round(sum(item.progress for item in study_progress_list) / len(study_progress_list), 1)
        if study_progress_list else 0.0
    )

    completed_reports = (
        db.query(AssessmentAIReport)
        .join(AssessmentAttempt, AssessmentAttempt.id == AssessmentAIReport.attempt_id)
        .filter(
            AssessmentAttempt.user_id == target_user.id,
            AssessmentAttempt.status == "completed",
            AssessmentAIReport.status == "completed",
        )
        .all()
    )

    score_dimensions = []

    def append_dimension(key, name, attr):
        scores = [getattr(item, attr) for item in completed_reports if getattr(item, attr) is not None]
        if scores:
            score_dimensions.append(
                StudentHomeScoreDimension(
                    key=key,
                    name=name,
                    best=max(scores),
                    worst=min(scores),
                )
            )

    append_dimension("research_integrity", "科研诚信薄弱型", "score_research_integrity")
    append_dimension("communication_anxiety", "医患沟通焦虑型", "score_communication_anxiety")
    append_dimension("career_identity", "职业认同模糊型", "score_career_identity")
    append_dimension("humanistic_care", "人文关怀缺失型", "score_humanistic_care")
    append_dimension("comprehensive_balance", "综合发展均衡型", "score_comprehensive_balance")

    return StudentHomeData(
        studentId=user_no,
        studentName=target_user.real_name,
        phone=target_user.phone,
        aiUsageDuration=get_total_ai_usage_duration(db, target_user.id),
        simulationCompletion=simulation_completion,
        studyProgressList=study_progress_list,
        scoreDimensions=score_dimensions,
    )


@router.get("/student-list", response_model=ResponseModel)
def get_teacher_student_list(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以访问")

    teachers = (
        db.query(AuthUser, TeacherUser)
        .join(TeacherUser, TeacherUser.auth_user_id == AuthUser.id)
        .filter(AuthUser.role == "teacher", AuthUser.is_active == True)
        .order_by(TeacherUser.teacher_no.asc())
        .all()
    )
    teacher_items = [
        {
            "id": user.id,
            "role": "teacher",
            "real_name": user.real_name,
            "teacher_no": teacher.teacher_no,
            "label": f"{teacher.teacher_no} {user.real_name}",
        }
        for user, teacher in teachers
    ]

    students = (
        db.query(AuthUser, StudentUser)
        .join(StudentUser, StudentUser.auth_user_id == AuthUser.id)
        .filter(AuthUser.role == "student", AuthUser.is_active == True)
        .order_by(StudentUser.student_no.asc())
        .all()
    )
    student_items = [
        {
            "id": user.id,
            "role": "student",
            "real_name": user.real_name,
            "student_no": student.student_no,
            "label": f"{student.student_no} {user.real_name}",
        }
        for user, student in students
    ]

    teacher_items.sort(key=lambda x: (0 if x["id"] == current_user.id else 1, x["teacher_no"]))

    return ResponseModel(data=[*teacher_items, *student_items])


@router.get("/roster/students", response_model=ResponseModel)
def get_student_roster_list(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can access roster")

    rows = (
        db.query(StudentRoster)
        .order_by(StudentRoster.student_no.asc(), StudentRoster.id.asc())
        .all()
    )
    return ResponseModel(
        data=[
            {
                "id": row.id,
                "student_no": row.student_no,
                "real_name": row.real_name,
                "is_enabled": row.is_enabled,
                "imported_at": format_datetime(row.imported_at),
                "updated_at": format_datetime(row.updated_at),
            }
            for row in rows
        ]
    )


@router.post("/roster/students", response_model=ResponseModel)
def create_student_roster(
    payload: StudentRosterUpsertRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage roster")

    student_no = payload.student_no.strip()
    real_name = payload.real_name.strip()
    if not student_no or not real_name:
        raise HTTPException(status_code=400, detail="学号和姓名不能为空")

    existing = db.query(StudentRoster).filter(StudentRoster.student_no == student_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="学号已存在")

    row = StudentRoster(
        student_no=student_no,
        real_name=real_name,
        is_enabled=payload.is_enabled,
    )
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="学号已存在")

    return ResponseModel(
        data={
            "id": row.id,
            "student_no": row.student_no,
            "real_name": row.real_name,
            "is_enabled": row.is_enabled,
            "imported_at": format_datetime(row.imported_at),
            "updated_at": format_datetime(row.updated_at),
        },
        message="学生名单添加成功",
    )


@router.put("/roster/students/{roster_id}", response_model=ResponseModel)
def update_student_roster(
    roster_id: int,
    payload: StudentRosterUpsertRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage roster")

    row = db.query(StudentRoster).filter(StudentRoster.id == roster_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="学生名单不存在")

    student_no = payload.student_no.strip()
    real_name = payload.real_name.strip()
    if not student_no or not real_name:
        raise HTTPException(status_code=400, detail="学号和姓名不能为空")

    duplicate = (
        db.query(StudentRoster)
        .filter(
            StudentRoster.student_no == student_no,
            StudentRoster.id != roster_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="学号已存在")

    row.student_no = student_no
    row.real_name = real_name
    row.is_enabled = payload.is_enabled
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="学号已存在")

    return ResponseModel(
        data={
            "id": row.id,
            "student_no": row.student_no,
            "real_name": row.real_name,
            "is_enabled": row.is_enabled,
            "imported_at": format_datetime(row.imported_at),
            "updated_at": format_datetime(row.updated_at),
        },
        message="学生名单更新成功",
    )


@router.delete("/roster/students/{roster_id}", response_model=ResponseModel)
def delete_student_roster(
    roster_id: int,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage roster")

    row = db.query(StudentRoster).filter(StudentRoster.id == roster_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="学生名单不存在")

    db.delete(row)
    db.commit()
    return ResponseModel(message="学生名单删除成功")


@router.get("/roster/teachers", response_model=ResponseModel)
def get_teacher_roster_list(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can access roster")

    rows = (
        db.query(TeacherRoster)
        .order_by(TeacherRoster.teacher_no.asc(), TeacherRoster.id.asc())
        .all()
    )
    return ResponseModel(
        data=[
            {
                "id": row.id,
                "teacher_no": row.teacher_no,
                "real_name": row.real_name,
                "is_enabled": row.is_enabled,
                "is_current_user": bool(
                    current_user.teacher_profile
                    and row.teacher_no == current_user.teacher_profile.teacher_no
                ),
                "imported_at": format_datetime(row.imported_at),
                "updated_at": format_datetime(row.updated_at),
            }
            for row in rows
        ]
    )


@router.post("/roster/teachers", response_model=ResponseModel)
def create_teacher_roster(
    payload: TeacherRosterUpsertRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage roster")

    if current_user.teacher_profile and row.teacher_no == current_user.teacher_profile.teacher_no:
        raise HTTPException(status_code=403, detail="current teacher cannot modify own roster entry")

    teacher_no = payload.teacher_no.strip()
    real_name = payload.real_name.strip()
    if not teacher_no or not real_name:
        raise HTTPException(status_code=400, detail="工号和姓名不能为空")

    existing = db.query(TeacherRoster).filter(TeacherRoster.teacher_no == teacher_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="工号已存在")

    row = TeacherRoster(
        teacher_no=teacher_no,
        real_name=real_name,
        is_enabled=payload.is_enabled,
    )
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="工号已存在")

    return ResponseModel(
        data={
            "id": row.id,
            "teacher_no": row.teacher_no,
            "real_name": row.real_name,
            "is_enabled": row.is_enabled,
            "imported_at": format_datetime(row.imported_at),
            "updated_at": format_datetime(row.updated_at),
        },
        message="教师名单添加成功",
    )


@router.put("/roster/teachers/{roster_id}", response_model=ResponseModel)
def update_teacher_roster(
    roster_id: int,
    payload: TeacherRosterUpsertRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage roster")

    row = db.query(TeacherRoster).filter(TeacherRoster.id == roster_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="教师名单不存在")

    teacher_no = payload.teacher_no.strip()
    real_name = payload.real_name.strip()
    if not teacher_no or not real_name:
        raise HTTPException(status_code=400, detail="工号和姓名不能为空")

    duplicate = (
        db.query(TeacherRoster)
        .filter(
            TeacherRoster.teacher_no == teacher_no,
            TeacherRoster.id != roster_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="工号已存在")

    row.teacher_no = teacher_no
    row.real_name = real_name
    row.is_enabled = payload.is_enabled
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="工号已存在")

    return ResponseModel(
        data={
            "id": row.id,
            "teacher_no": row.teacher_no,
            "real_name": row.real_name,
            "is_enabled": row.is_enabled,
            "imported_at": format_datetime(row.imported_at),
            "updated_at": format_datetime(row.updated_at),
        },
        message="教师名单更新成功",
    )


@router.delete("/roster/teachers/{roster_id}", response_model=ResponseModel)
def delete_teacher_roster(
    roster_id: int,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage roster")

    row = db.query(TeacherRoster).filter(TeacherRoster.id == roster_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="教师名单不存在")

    if current_user.teacher_profile and row.teacher_no == current_user.teacher_profile.teacher_no:
        raise HTTPException(status_code=403, detail="current teacher cannot modify own roster entry")

    db.delete(row)
    db.commit()
    return ResponseModel(message="教师名单删除成功")


@router.get("/home", response_model=StudentHomeResponseModel)
def get_teacher_home(
    userId: int | None = Query(default=None),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以访问")

    if not userId or userId == current_user.id:
        target_user = current_user
    else:
        target_user = db.query(AuthUser).filter(AuthUser.id == userId).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="目标用户不存在")

    return StudentHomeResponseModel(data=build_home_data(target_user, db))


@router.get("/resources/categories", response_model=ResourceCategoryListResponseModel)
def get_teacher_resource_categories(
    userId: int | None = Query(default=None),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can access resources")

    target_user = current_user
    if userId and userId != current_user.id:
        target_user = db.query(AuthUser).filter(AuthUser.id == userId).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="target user not found")

    items = build_category_progress_list(db, target_user.id)
    return ResourceCategoryListResponseModel(data=ResourceCategoryListData(items=items))


@router.get("/resources/categories/{category_id}/items", response_model=ResourceListResponseModel)
def get_teacher_resource_items(
    category_id: int,
    userId: int | None = Query(default=None),
    pageNum: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can access resources")

    target_user = current_user
    if userId and userId != current_user.id:
        target_user = db.query(AuthUser).filter(AuthUser.id == userId).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="target user not found")

    try:
        data = build_resource_list(
            db,
            user_id=target_user.id,
            category_id=category_id,
            page_num=pageNum,
            page_size=pageSize,
            include_hidden=True,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="resource category not found")

    return ResourceListResponseModel(data=data)


@router.post("/resources/heartbeat", response_model=ResourceHeartbeatResponseModel)
def teacher_resource_heartbeat(
    payload: ResourceHeartbeatRequest,
    current_user: AuthUser = Depends(get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can access resources")

    state = heartbeat_resource_session(current_user.id)
    return ResourceHeartbeatResponseModel(data=ResourceHeartbeatData(activeSeconds=state["active_seconds"]))


@router.post("/resources/{resource_id}/visit", response_model=ResourceVisitResponseModel)
def visit_teacher_resource(
    resource_id: int,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can access resources")

    resource = (
        db.query(LearningResource)
        .join(ResourceCategory, ResourceCategory.id == LearningResource.category_id)
        .filter(
            LearningResource.id == resource_id,
            LearningResource.is_visible == True,
            ResourceCategory.is_enabled == True,
        )
        .first()
    )
    if not resource:
        raise HTTPException(status_code=404, detail="resource not found")
    if not resource.url.strip():
        raise HTTPException(status_code=400, detail="resource link is not configured")

    record = mark_resource_completed(db, user_id=current_user.id, resource=resource)
    db.commit()
    db.refresh(record)

    return ResourceVisitResponseModel(
        data=ResourceVisitData(
            resourceId=resource.id,
            clickCount=record.click_count,
            completed=record.is_completed,
            url=resource.url,
        )
    )


@router.post("/resources/categories/{category_id}/items", response_model=ResourceItemResponseModel)
def create_teacher_resource(
    category_id: int,
    payload: ResourceUpsertRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage resources")

    category = (
        db.query(ResourceCategory)
        .filter(
            ResourceCategory.id == category_id,
            ResourceCategory.is_enabled == True,
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="resource category not found")

    max_sort_order = (
        db.query(func.coalesce(func.max(LearningResource.sort_order), 0))
        .filter(LearningResource.category_id == category.id)
        .scalar()
        or 0
    )

    resource = LearningResource(
        category_id=category.id,
        title=payload.title.strip(),
        url=payload.url.strip(),
        sort_order=int(max_sort_order) + 1,
        is_visible=True,
        created_by_user_id=current_user.id,
        updated_by_user_id=current_user.id,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)

    return ResourceItemResponseModel(
        data=ResourceListItem(
            id=resource.id,
            title=resource.title,
            url=resource.url,
            isVisible=resource.is_visible,
            completed=False,
            clickCount=0,
            lastClickedAt="",
        )
    )


@router.put("/resources/{resource_id}", response_model=ResourceItemResponseModel)
def update_teacher_resource(
    resource_id: int,
    payload: ResourceUpsertRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage resources")

    resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="resource not found")

    resource.title = payload.title.strip()
    resource.url = payload.url.strip()
    resource.updated_by_user_id = current_user.id
    db.commit()
    db.refresh(resource)

    return ResourceItemResponseModel(
        data=ResourceListItem(
            id=resource.id,
            title=resource.title,
            url=resource.url,
            isVisible=resource.is_visible,
            completed=False,
            clickCount=0,
            lastClickedAt="",
        )
    )


@router.patch("/resources/{resource_id}/visibility", response_model=ResourceItemResponseModel)
def update_teacher_resource_visibility(
    resource_id: int,
    payload: ResourceVisibilityRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage resources")

    resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="resource not found")

    resource.is_visible = payload.isVisible
    resource.updated_by_user_id = current_user.id
    db.commit()
    db.refresh(resource)

    return ResourceItemResponseModel(
        data=ResourceListItem(
            id=resource.id,
            title=resource.title,
            url=resource.url,
            isVisible=resource.is_visible,
            completed=False,
            clickCount=0,
            lastClickedAt="",
        )
    )


@router.delete("/resources/{resource_id}", response_model=ResponseModel)
def delete_teacher_resource(
    resource_id: int,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can manage resources")

    resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="resource not found")

    db.delete(resource)
    db.commit()
    return ResponseModel(message="resource deleted")


@router.get("/exam/{exam_type}/notice", response_model=ExamNoticeResponseModel)
def get_teacher_exam_notice(
    exam_type: str,
    current_user: AuthUser = Depends(get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以访问考试须知")
    if exam_type not in EXAM_NOTICE_MAP:
        raise HTTPException(status_code=404, detail="考试类型不存在")
    return ExamNoticeResponseModel(data=ExamNoticeData(items=EXAM_NOTICE_MAP[exam_type]))


@router.get("/exam/{exam_type}/info", response_model=ExamInfoResponseModel)
def get_teacher_exam_info(
    exam_type: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以访问考试信息")
    paper = get_fixed_paper_for_user(db, current_user.id, exam_type)
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return ExamInfoResponseModel(
        data=ExamInfoData(
            examId=paper.id,
            paperName=paper.title,
        )
    )


@router.get("/exam/{exam_type}/paper/{exam_id}", response_model=ExamPaperResponseModel)
def get_teacher_exam_paper(
    exam_type: str,
    exam_id: int,
    clientSessionId: str | None = Query(default=None),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以访问试卷")

    paper = resolve_allowed_paper_for_user(db, current_user.id, exam_type, exam_id)

    session_state = ensure_exam_session(
        current_user.id,
        paper.id,
        paper.paper_type,
        paper.duration_seconds,
        clientSessionId,
    )
    return ExamPaperResponseModel(data=build_paper_response(db, paper, session_state))


@router.post("/exam/heartbeat", response_model=ExamHeartbeatResponseModel)
def teacher_exam_heartbeat(
    payload: ExamHeartbeatRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以发送考试心跳")

    try:
        exam_id = int(payload.examId)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="试卷编号无效")

    paper = resolve_allowed_paper_for_user(db, current_user.id, payload.examType, exam_id)

    state = heartbeat_exam_session(
        current_user.id,
        paper.id,
        paper.paper_type,
        paper.duration_seconds,
        payload.clientSessionId,
    )
    return ExamHeartbeatResponseModel(
        data=ExamHeartbeatData(
            activeSeconds=state["active_seconds"],
            submitted=state["submitted"],
            remainingSeconds=state["remaining_seconds"],
        )
    )


@router.post("/exam/submit", response_model=SubmitExamResponseModel)
def submit_teacher_exam(
    payload: SubmitExamRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以提交试卷")

    try:
        exam_id = int(payload.examId)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="试卷编号无效")

    paper = resolve_allowed_paper_for_user(db, current_user.id, payload.examType, exam_id)

    if not acquire_submit_lock(current_user.id, paper.id):
        raise HTTPException(status_code=409, detail="请勿重复提交")

    questions = (
        db.query(AssessmentQuestion)
        .join(AssessmentPaperQuestion, AssessmentPaperQuestion.question_id == AssessmentQuestion.id)
        .filter(AssessmentPaperQuestion.paper_id == paper.id)
        .all()
    )
    answer_map = {}
    for item in payload.answers:
        try:
            answer_map[int(item.questionId)] = item.answer
        except (TypeError, ValueError):
            continue

    try:
        try:
            duration_seconds = finalize_exam_session(
                current_user.id,
                paper.id,
                paper.paper_type,
                paper.duration_seconds,
                payload.clientSessionId,
            )
        except ValueError:
            raise HTTPException(status_code=409, detail="试卷已提交，请勿重复提交")
        submitted_at = datetime.utcnow()
        started_at = submitted_at

        attempt = AssessmentAttempt(
            user_id=current_user.id,
            paper_id=paper.id,
            paper_type=paper.paper_type,
            status="ai_processing",
            started_at=started_at,
            submitted_at=submitted_at,
            duration_seconds=max(duration_seconds, 1),
            total_score=None,
            force_submitted=payload.forced,
        )
        db.add(attempt)
        db.flush()

        for question in questions:
            normalized_answer = normalize_answer_for_storage(question, answer_map.get(question.id))
            answer = AssessmentAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                answer_json=normalized_answer,
                score=None,
                judged_at=None,
            )
            db.add(answer)

        report = AssessmentAIReport(
            attempt_id=attempt.id,
            status="processing",
            summary="AI 分析中",
            raw_response_json={"status": "processing"},
        )
        db.add(report)
        db.commit()
        clear_exam_session(current_user.id, paper.id)

        trigger_ai_analysis_async(attempt.id)

        return SubmitExamResponseModel(
            data=SubmitExamResponseData(
                success=True,
                resultId=attempt.id,
            )
        )
    finally:
        release_submit_lock(current_user.id, paper.id)


@router.get("/exam/results", response_model=ExamResultListResponseModel)
def get_teacher_exam_results(
    userId: int = Query(...),
    pageNum: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以访问考试结果")

    target_user = db.query(AuthUser).filter(AuthUser.id == userId).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")

    query = (
        db.query(AssessmentAttempt, AssessmentPaper, AssessmentAIReport)
        .join(AssessmentPaper, AssessmentPaper.id == AssessmentAttempt.paper_id)
        .outerjoin(AssessmentAIReport, AssessmentAIReport.attempt_id == AssessmentAttempt.id)
        .filter(
            AssessmentAttempt.user_id == userId,
            AssessmentAttempt.submitted_at.isnot(None),
        )
        .order_by(AssessmentAttempt.submitted_at.desc(), AssessmentAttempt.id.desc())
    )

    total = query.count()
    rows = query.offset((pageNum - 1) * pageSize).limit(pageSize).all()

    records = [
        ExamResultListItem(
            id=attempt.id,
            title=paper.title,
            paperType=paper.paper_type,
            submitTime=format_datetime(attempt.submitted_at),
            durationMinutes=max(int((attempt.duration_seconds or 0) / 60), 0),
            analysisReady=bool(report and report.status == "completed"),
            analysisStatus=(report.status if report else ""),
            analysisMessage=(report.summary if report and report.status == "failed" else ""),
        )
        for attempt, paper, report in rows
    ]

    return ExamResultListResponseModel(
        data=ExamResultListData(records=records, total=total)
    )


@router.get("/exam/results/{result_id}", response_model=ExamResultDetailResponseModel)
def get_teacher_exam_result_detail(
    result_id: int,
    userId: int = Query(...),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以访问考试结果详情")

    target_user = db.query(AuthUser).filter(AuthUser.id == userId).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")

    row = (
        db.query(AssessmentAttempt, AssessmentPaper, AssessmentAIReport)
        .join(AssessmentPaper, AssessmentPaper.id == AssessmentAttempt.paper_id)
        .outerjoin(AssessmentAIReport, AssessmentAIReport.attempt_id == AssessmentAttempt.id)
        .filter(
            AssessmentAttempt.id == result_id,
            AssessmentAttempt.user_id == userId,
            AssessmentAttempt.submitted_at.isnot(None),
        )
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="考试结果不存在")

    attempt, paper, report = row

    answer_rows = (
        db.query(AssessmentAnswer, AssessmentQuestion)
        .join(AssessmentQuestion, AssessmentQuestion.id == AssessmentAnswer.question_id)
        .filter(AssessmentAnswer.attempt_id == attempt.id)
        .order_by(AssessmentAnswer.id.asc())
        .all()
    )

    answer_list = [
        ExamResultAnswerItem(
            questionId=question.id,
            questionTitle=question.title,
            answer=answer.answer_json,
        )
        for answer, question in answer_rows
    ]

    user_no = (
        target_user.teacher_profile.teacher_no
        if target_user.role == "teacher" and target_user.teacher_profile
        else target_user.student_profile.student_no
        if target_user.role == "student" and target_user.student_profile
        else ""
    )

    return ExamResultDetailResponseModel(
        data=ExamResultDetailData(
            paperName=paper.title,
            studentNo=user_no,
            realName=target_user.real_name,
            submitTime=format_datetime(attempt.submitted_at),
            durationMinutes=max(int((attempt.duration_seconds or 0) / 60), 0),
            answerList=answer_list,
            aiAnalysis=build_result_analysis(report),
        )
    )


@router.post("/exam/results/{result_id}/retry-analysis", response_model=ResponseModel)
def retry_teacher_exam_result_analysis(
    result_id: int,
    userId: int = Query(...),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以重试分析")

    row = (
        db.query(AssessmentAttempt, AssessmentAIReport)
        .outerjoin(AssessmentAIReport, AssessmentAIReport.attempt_id == AssessmentAttempt.id)
        .filter(
            AssessmentAttempt.id == result_id,
            AssessmentAttempt.user_id == userId,
            AssessmentAttempt.submitted_at.isnot(None),
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="考试结果不存在")

    attempt, report = row
    if report and report.status == "processing":
        raise HTTPException(status_code=409, detail="模型分析进行中，请稍后")
    if report and report.status == "completed":
        raise HTTPException(status_code=409, detail="模型分析已完成，无需重试")

    if not report:
        report = AssessmentAIReport(attempt_id=attempt.id)
        db.add(report)

    report.status = "processing"
    report.summary = "AI 分析中"
    report.raw_response_json = {"status": "processing", "retry": True}
    attempt.status = "ai_processing"
    db.commit()

    trigger_ai_analysis_async(attempt.id)
    return ResponseModel(data={"success": True, "resultId": result_id})


@router.get("/exam/results/{result_id}/export")
def export_teacher_exam_result(
    result_id: int,
    userId: int = Query(...),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以导出结果")

    attempt, paper, report, user = fetch_attempt_export_data(db, result_id, userId)
    answers = fetch_attempt_answers_by_order(
        db,
        attempt.id,
        paper.id,
        survey_masking=(paper.paper_type == "survey"),
    )
    rows = [build_export_row(attempt, paper, report, user, answers)]
    workbook_stream = build_export_workbook(rows, len(answers))

    file_name = f"exam_result_{result_id}.xlsx"
    return StreamingResponse(
        workbook_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/exam/results/export/by-type")
def export_teacher_exam_results_by_type(
    userId: int = Query(...),
    paperType: str = Query(...),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以导出结果")
    if paperType not in {"survey", "integrity", "ideology"}:
        raise HTTPException(status_code=400, detail="导出类型不支持")

    target_user = db.query(AuthUser).filter(AuthUser.id == userId).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")

    rows = (
        db.query(AssessmentAttempt, AssessmentPaper, AssessmentAIReport, AuthUser)
        .join(AssessmentPaper, AssessmentPaper.id == AssessmentAttempt.paper_id)
        .outerjoin(AssessmentAIReport, AssessmentAIReport.attempt_id == AssessmentAttempt.id)
        .join(AuthUser, AuthUser.id == AssessmentAttempt.user_id)
        .filter(
            AssessmentAttempt.user_id == userId,
            AssessmentAttempt.paper_type == paperType,
            AssessmentAttempt.submitted_at.isnot(None),
        )
        .order_by(AssessmentAttempt.submitted_at.asc(), AssessmentAttempt.id.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="未找到可导出的结果")

    export_rows, max_question_count = build_export_rows_and_question_count(db, rows)

    workbook_stream = build_export_workbook(export_rows, max_question_count)
    file_name = f"{paperType}_all_results_user_{userId}.xlsx"
    return StreamingResponse(
        workbook_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/exam/results/export/options", response_model=ResponseModel)
def get_teacher_export_filter_options(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以获取导出筛选项")

    papers = (
        db.query(AssessmentPaper)
        .filter(AssessmentPaper.is_active == True)
        .order_by(
            AssessmentPaper.paper_type.asc(),
            AssessmentPaper.version_no.asc(),
            AssessmentPaper.id.asc(),
        )
        .all()
    )

    survey_options = []
    exam_options = []
    for paper in papers:
        item = {
            "id": paper.id,
            "paperType": paper.paper_type,
            "versionNo": paper.version_no,
            "title": paper.title,
            "label": f"{paper.title}（第{paper.version_no}套）",
        }
        if paper.paper_type == "survey":
            survey_options.append(item)
        elif paper.paper_type in {"integrity", "ideology"}:
            exam_options.append(item)

    return ResponseModel(
        data={
            "survey": survey_options,
            "exam": exam_options,
        }
    )


@router.post("/exam/results/export/filter")
def export_teacher_exam_results_by_filter(
    payload: TeacherFilterExportRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有老师可以导出结果")

    account_scope = (payload.accountScope or "").strip().lower()
    if account_scope not in {"teacher", "student", "all"}:
        raise HTTPException(status_code=400, detail="账号类型参数错误")
    if not payload.paperIds:
        raise HTTPException(status_code=400, detail="请至少选择一套问卷或试卷")

    try:
        paper_ids = sorted(set(int(item) for item in payload.paperIds))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="试卷参数错误")
    papers = (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.id.in_(paper_ids),
            AssessmentPaper.is_active == True,
        )
        .all()
    )
    if len(papers) != len(paper_ids):
        raise HTTPException(status_code=400, detail="部分试卷不存在或未启用")

    selected_types = {paper.paper_type for paper in papers}
    contains_survey = "survey" in selected_types
    contains_exam = any(item in {"integrity", "ideology"} for item in selected_types)
    if contains_survey and contains_exam:
        raise HTTPException(status_code=400, detail="问卷与试卷不能同时导出，请分开导出")

    export_mode = "survey" if contains_survey else "exam"

    query = (
        db.query(AssessmentAttempt, AssessmentPaper, AssessmentAIReport, AuthUser)
        .join(AssessmentPaper, AssessmentPaper.id == AssessmentAttempt.paper_id)
        .outerjoin(AssessmentAIReport, AssessmentAIReport.attempt_id == AssessmentAttempt.id)
        .join(AuthUser, AuthUser.id == AssessmentAttempt.user_id)
        .filter(
            AssessmentAttempt.paper_id.in_(paper_ids),
            AssessmentAttempt.submitted_at.isnot(None),
        )
    )

    if account_scope == "teacher":
        query = query.filter(AuthUser.role == "teacher")
    elif account_scope == "student":
        query = query.filter(AuthUser.role == "student")

    rows = query.order_by(AssessmentAttempt.submitted_at.asc(), AssessmentAttempt.id.asc()).all()
    if not rows:
        raise HTTPException(status_code=404, detail="未找到可导出的结果")

    export_rows, max_question_count = build_export_rows_and_question_count(
        db=db,
        rows=rows,
        export_mode=export_mode,
    )
    workbook_stream = build_export_workbook_by_mode(
        rows=export_rows,
        question_count=max_question_count,
        export_mode=export_mode,
    )

    file_name = f"{export_mode}_results_{account_scope}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        workbook_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
