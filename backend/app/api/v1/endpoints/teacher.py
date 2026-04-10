from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.auth_user import AuthUser
from app.models.student_user import StudentUser
from app.models.teacher_user import TeacherUser
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
    build_ai_payload,
    clear_exam_session,
    dispatch_ai_analysis,
    ensure_exam_session,
    finalize_exam_session,
    heartbeat_exam_session,
    release_submit_lock,
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
}


def format_datetime(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


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

    selected_paper = get_fixed_paper_for_user(db, current_user.id, exam_type)

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
    if paper.id != selected_paper.id:
        raise HTTPException(status_code=409, detail="当前考试应按固定试卷规则进行")

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

    selected_paper = get_fixed_paper_for_user(db, current_user.id, payload.examType)

    paper = (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.id == exam_id,
            AssessmentPaper.paper_type == payload.examType,
            AssessmentPaper.is_active == True,
        )
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.id != selected_paper.id:
        raise HTTPException(status_code=409, detail="当前考试应按固定试卷规则进行")

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

    selected_paper = get_fixed_paper_for_user(db, current_user.id, payload.examType)

    paper = (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.id == exam_id,
            AssessmentPaper.paper_type == payload.examType,
            AssessmentPaper.is_active == True,
        )
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.id != selected_paper.id:
        raise HTTPException(status_code=409, detail="当前考试应按固定试卷规则进行")

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

        answer_rows = []
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
            answer_rows.append(answer)

        report = AssessmentAIReport(
            attempt_id=attempt.id,
            status="processing",
            summary="AI 分析中",
            raw_response_json={"status": "processing"},
        )
        db.add(report)
        db.commit()
        clear_exam_session(current_user.id, paper.id)

        payload_json = build_ai_payload(
            attempt=attempt,
            paper=paper,
            user=current_user,
            questions=questions,
            answers=answer_rows,
        )
        success, error_message = dispatch_ai_analysis(payload_json)
        if not success:
            report.status = "failed"
            report.summary = "AI 分析任务发送失败"
            report.raw_response_json = {
                "status": "failed",
                "message": error_message,
            }
            attempt.status = "submitted"
            db.commit()

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
            submitTime=format_datetime(attempt.submitted_at),
            durationMinutes=max(int((attempt.duration_seconds or 0) / 60), 0),
            analysisReady=bool(report and report.status == "completed"),
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
