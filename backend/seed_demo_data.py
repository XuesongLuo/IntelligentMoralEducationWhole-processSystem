"""
测试数据的导入，该文件单独执行，执行指令：
python seed_demo_data.py
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash

from app.models.auth_user import AuthUser
from app.models.student_user import StudentUser
from app.models.teacher_user import TeacherUser
from app.models.student_roster import StudentRoster
from app.models.teacher_roster import TeacherRoster

from app.models.resource_category import ResourceCategory
from app.models.learning_resource import LearningResource
from app.models.user_resource_record import UserResourceRecord

from app.models.assessment_paper import AssessmentPaper
from app.models.assessment_question import AssessmentQuestion
from app.models.assessment_paper_question import AssessmentPaperQuestion
from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment_answer import AssessmentAnswer
from app.models.assessment_ai_report import AssessmentAIReport


DEFAULT_PASSWORD = "123456"

CATEGORY_DATA = [
    {"code": "doctor_patient_dispute", "name": "医患纠纷处理", "sort_order": 1},
    {"code": "research_fraud", "name": "科研数据造假诱惑", "sort_order": 2},
    {"code": "medical_fairness", "name": "医疗资源分配公平性", "sort_order": 3},
    {"code": "privacy_protection", "name": "隐私保护困境", "sort_order": 4},
    {"code": "teamwork_conflict", "name": "团队协作冲突", "sort_order": 5},
    {"code": "public_health_response", "name": "公共卫生事件应对", "sort_order": 6},
]

RESOURCE_DATA = {
    "doctor_patient_dispute": [
        {"title": "医患纠纷案例分析一", "url": "https://example.com/resource/doctor-patient-1"},
        {"title": "医患沟通技巧训练", "url": "https://example.com/resource/doctor-patient-2"},
        {"title": "临床冲突处置流程", "url": "https://example.com/resource/doctor-patient-3"},
    ],
    "research_fraud": [
        {"title": "科研诚信规范导读", "url": "https://example.com/resource/research-1"},
        {"title": "数据造假典型案例", "url": "https://example.com/resource/research-2"},
        {"title": "论文署名与引用规范", "url": "https://example.com/resource/research-3"},
    ],
    "medical_fairness": [
        {"title": "医疗资源公平分配讨论", "url": "https://example.com/resource/fairness-1"},
        {"title": "稀缺床位分配案例", "url": "https://example.com/resource/fairness-2"},
        {"title": "基层与三甲医疗资源对比", "url": "https://example.com/resource/fairness-3"},
    ],
    "privacy_protection": [
        {"title": "患者隐私保护规范", "url": "https://example.com/resource/privacy-1"},
        {"title": "病例信息脱敏基础", "url": "https://example.com/resource/privacy-2"},
        {"title": "电子病历权限控制", "url": "https://example.com/resource/privacy-3"},
    ],
    "teamwork_conflict": [
        {"title": "医疗团队沟通协作", "url": "https://example.com/resource/teamwork-1"},
        {"title": "跨学科合作冲突处理", "url": "https://example.com/resource/teamwork-2"},
        {"title": "值班交接中的责任边界", "url": "https://example.com/resource/teamwork-3"},
    ],
    "public_health_response": [
        {"title": "公共卫生事件应急流程", "url": "https://example.com/resource/public-health-1"},
        {"title": "突发疫情中的职业伦理", "url": "https://example.com/resource/public-health-2"},
        {"title": "群体性事件舆情应对", "url": "https://example.com/resource/public-health-3"},
    ],
}

USER_DATA = {
    "teacher": {
        "real_name": "李老师",
        "phone": "13900000000",
        "teacher_no": "T2020007",
        "role": "teacher",
    },
    "student_zhangsan": {
        "real_name": "张三",
        "phone": "13800000000",
        "student_no": "20260001",
        "role": "student",
    },
    "student_lisi": {
        "real_name": "李四",
        "phone": "13800000001",
        "student_no": "20260002",
        "role": "student",
    },
}

def get_or_create_student_roster(db: Session, student_no: str, real_name: str) -> StudentRoster:
    roster = (
        db.query(StudentRoster)
        .filter(StudentRoster.student_no == student_no)
        .first()
    )
    if roster:
        if roster.real_name != real_name:
            roster.real_name = real_name
        roster.is_enabled = True
        return roster

    roster = StudentRoster(
        student_no=student_no,
        real_name=real_name,
        is_enabled=True,
    )
    db.add(roster)
    db.flush()
    return roster


def get_or_create_teacher_roster(db: Session, teacher_no: str, real_name: str) -> TeacherRoster:
    roster = (
        db.query(TeacherRoster)
        .filter(TeacherRoster.teacher_no == teacher_no)
        .first()
    )
    if roster:
        if roster.real_name != real_name:
            roster.real_name = real_name
        roster.is_enabled = True
        return roster

    roster = TeacherRoster(
        teacher_no=teacher_no,
        real_name=real_name,
        is_enabled=True,
    )
    db.add(roster)
    db.flush()
    return roster


def get_or_create_auth_user(
    db: Session,
    *,
    phone: str,
    real_name: str,
    role: str,
    password: str = DEFAULT_PASSWORD,
) -> AuthUser:
    user = db.query(AuthUser).filter(AuthUser.phone == phone).first()
    if user:
        user.real_name = real_name
        user.role = role
        user.is_active = True
        return user

    user = AuthUser(
        phone=phone,
        real_name=real_name,
        role=role,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def ensure_student_profile(db: Session, auth_user: AuthUser, student_no: str) -> StudentUser:
    profile = db.query(StudentUser).filter(StudentUser.auth_user_id == auth_user.id).first()
    if profile:
        profile.student_no = student_no
        return profile

    profile = StudentUser(
        auth_user_id=auth_user.id,
        student_no=student_no,
    )
    db.add(profile)
    db.flush()
    return profile


def ensure_teacher_profile(db: Session, auth_user: AuthUser, teacher_no: str) -> TeacherUser:
    profile = db.query(TeacherUser).filter(TeacherUser.auth_user_id == auth_user.id).first()
    if profile:
        profile.teacher_no = teacher_no
        profile.teacher_invite_verified = True
        return profile

    profile = TeacherUser(
        auth_user_id=auth_user.id,
        teacher_no=teacher_no,
        teacher_invite_verified=True,
    )
    db.add(profile)
    db.flush()
    return profile


def seed_categories(db: Session) -> dict[str, ResourceCategory]:
    result = {}

    for item in CATEGORY_DATA:
        category = (
            db.query(ResourceCategory)
            .filter(ResourceCategory.code == item["code"])
            .first()
        )

        if category:
            category.name = item["name"]
            category.sort_order = item["sort_order"]
            category.is_enabled = True
        else:
            category = ResourceCategory(
                code=item["code"],
                name=item["name"],
                sort_order=item["sort_order"],
                is_enabled=True,
            )
            db.add(category)
            db.flush()

        result[item["code"]] = category

    return result


def seed_resources(
    db: Session,
    teacher_user_id: int,
    categories: dict[str, ResourceCategory],
) -> dict[str, list[LearningResource]]:
    result = {}

    for category_code, items in RESOURCE_DATA.items():
        category = categories[category_code]
        result[category_code] = []

        for idx, item in enumerate(items, start=1):
            resource = (
                db.query(LearningResource)
                .filter(
                    LearningResource.category_id == category.id,
                    LearningResource.title == item["title"],
                )
                .first()
            )

            if resource:
                resource.url = item["url"]
                resource.sort_order = idx
                resource.is_visible = True
                resource.updated_by_user_id = teacher_user_id
            else:
                resource = LearningResource(
                    category_id=category.id,
                    title=item["title"],
                    url=item["url"],
                    sort_order=idx,
                    is_visible=True,
                    created_by_user_id=teacher_user_id,
                    updated_by_user_id=teacher_user_id,
                )
                db.add(resource)
                db.flush()

            result[category_code].append(resource)

    return result


def ensure_user_resource_record(
    db: Session,
    *,
    user_id: int,
    resource_id: int,
    click_count: int,
    is_completed: bool,
    first_clicked_at: datetime,
    last_clicked_at: datetime,
) -> UserResourceRecord:
    record = (
        db.query(UserResourceRecord)
        .filter(
            UserResourceRecord.user_id == user_id,
            UserResourceRecord.resource_id == resource_id,
        )
        .first()
    )

    if record:
        record.click_count = click_count
        record.is_completed = is_completed
        record.first_clicked_at = first_clicked_at
        record.last_clicked_at = last_clicked_at
        return record

    record = UserResourceRecord(
        user_id=user_id,
        resource_id=resource_id,
        click_count=click_count,
        is_completed=is_completed,
        first_clicked_at=first_clicked_at,
        last_clicked_at=last_clicked_at,
    )
    db.add(record)
    db.flush()
    return record


def seed_resource_records(
    db: Session,
    *,
    zhangsan_user_id: int,
    lisi_user_id: int,
    resource_map: dict[str, list[LearningResource]],
):
    now = datetime.utcnow()

    # 张三：完成较多资源
    completed_codes_for_zhangsan = {
        "doctor_patient_dispute": [0, 1, 2],
        "research_fraud": [0, 1],
        "medical_fairness": [0, 1],
        "privacy_protection": [0],
        "teamwork_conflict": [0, 1],
        "public_health_response": [0],
    }

    for category_code, indexes in completed_codes_for_zhangsan.items():
        for idx in indexes:
            resource = resource_map[category_code][idx]
            ensure_user_resource_record(
                db,
                user_id=zhangsan_user_id,
                resource_id=resource.id,
                click_count=idx + 1,
                is_completed=True,
                first_clicked_at=now - timedelta(days=10 - idx),
                last_clicked_at=now - timedelta(days=2),
            )

    # 李四：完成较少资源
    completed_codes_for_lisi = {
        "doctor_patient_dispute": [0],
        "research_fraud": [0],
    }

    for category_code, indexes in completed_codes_for_lisi.items():
        for idx in indexes:
            resource = resource_map[category_code][idx]
            ensure_user_resource_record(
                db,
                user_id=lisi_user_id,
                resource_id=resource.id,
                click_count=1,
                is_completed=True,
                first_clicked_at=now - timedelta(days=5),
                last_clicked_at=now - timedelta(days=4),
            )



# 试卷资源创建
def get_or_create_paper(
    db: Session,
    *,
    paper_type: str,
    title: str,
    version_no: int,
    duration_seconds: int,
    created_by_user_id: int,
) -> AssessmentPaper:
    paper = (
        db.query(AssessmentPaper)
        .filter(
            AssessmentPaper.paper_type == paper_type,
            AssessmentPaper.title == title,
            AssessmentPaper.version_no == version_no,
        )
        .first()
    )

    if paper:
        paper.duration_seconds = duration_seconds
        paper.is_active = True
        return paper

    paper = AssessmentPaper(
        paper_type=paper_type,
        title=title,
        version_no=version_no,
        duration_seconds=duration_seconds,
        is_active=True,
        created_by_user_id=created_by_user_id,
    )
    db.add(paper)
    db.flush()
    return paper


def get_or_create_question(
    db: Session,
    *,
    paper_type: str,
    question_type: str,
    title: str,
    options_json,
    answer_json,
    score: int,
    created_by_user_id: int,
) -> AssessmentQuestion:
    question = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.paper_type == paper_type,
            AssessmentQuestion.question_type == question_type,
            AssessmentQuestion.title == title,
        )
        .first()
    )

    if question:
        question.options_json = options_json
        question.answer_json = answer_json
        question.score = score
        return question

    question = AssessmentQuestion(
        paper_type=paper_type,
        question_type=question_type,
        title=title,
        options_json=options_json,
        answer_json=answer_json,
        score=score,
        created_by_user_id=created_by_user_id,
    )
    db.add(question)
    db.flush()
    return question


def ensure_paper_question_link(
    db: Session,
    paper_id: int,
    question_id: int,
    sort_order: int,
):
    link = (
        db.query(AssessmentPaperQuestion)
        .filter(
            AssessmentPaperQuestion.paper_id == paper_id,
            AssessmentPaperQuestion.question_id == question_id,
        )
        .first()
    )

    if link:
        link.sort_order = sort_order
        return link

    link = AssessmentPaperQuestion(
        paper_id=paper_id,
        question_id=question_id,
        sort_order=sort_order,
    )
    db.add(link)
    db.flush()
    return link


# 创建试卷
def seed_papers_and_questions(db: Session, teacher_user_id: int) -> dict[str, AssessmentPaper]:
    survey_1 = get_or_create_paper(
        db,
        paper_type="survey",
        title="德育画像构建问卷一",
        version_no=1,
        duration_seconds=5400,
        created_by_user_id=teacher_user_id,
    )
    survey_2 = get_or_create_paper(
        db,
        paper_type="survey",
        title="德育画像构建问卷二",
        version_no=2,
        duration_seconds=5400,
        created_by_user_id=teacher_user_id,
    )
    integrity_1 = get_or_create_paper(
        db,
        paper_type="integrity",
        title="科研诚信考核试卷一",
        version_no=1,
        duration_seconds=7200,
        created_by_user_id=teacher_user_id,
    )
    integrity_2 = get_or_create_paper(
        db,
        paper_type="integrity",
        title="科研诚信考核试卷二",
        version_no=2,
        duration_seconds=7200,
        created_by_user_id=teacher_user_id,
    )

    survey_questions_1 = [
        get_or_create_question(
            db,
            paper_type="survey",
            question_type="single",
            title="当你在团队合作中遇到意见分歧时，通常会怎么做？",
            options_json=[
                {"label": "A", "text": "坚持自己观点"},
                {"label": "B", "text": "主动沟通协调"},
                {"label": "C", "text": "选择沉默"},
                {"label": "D", "text": "交给别人处理"},
            ],
            answer_json=["B"],
            score=20,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="survey",
            question_type="multiple",
            title="你认为医学生应具备哪些核心品质？",
            options_json=[
                {"label": "A", "text": "责任心"},
                {"label": "B", "text": "同理心"},
                {"label": "C", "text": "合作意识"},
                {"label": "D", "text": "诚信意识"},
            ],
            answer_json=["A", "B", "C", "D"],
            score=20,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="survey",
            question_type="essay",
            title="请简要描述一次你在学习或生活中体现责任担当的经历。",
            options_json=None,
            answer_json=None,
            score=0,
            created_by_user_id=teacher_user_id,
        ),
    ]

    survey_questions_2 = [
        get_or_create_question(
            db,
            paper_type="survey",
            question_type="boolean",
            title="在面对患者情绪激动时，先安抚情绪再解释问题是合理的做法。",
            options_json=[
                {"label": "A", "text": "对"},
                {"label": "B", "text": "错"},
            ],
            answer_json=[True],
            score=20,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="survey",
            question_type="fill_blank",
            title="请填写你认为医学职业最重要的一项价值。",
            options_json=None,
            answer_json=None,
            score=0,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="survey",
            question_type="single",
            title="面对高压任务时，你更倾向于：",
            options_json=[
                {"label": "A", "text": "独自承担"},
                {"label": "B", "text": "寻求合作"},
                {"label": "C", "text": "拖延回避"},
                {"label": "D", "text": "被动等待安排"},
            ],
            answer_json=["B"],
            score=20,
            created_by_user_id=teacher_user_id,
        ),
    ]

    integrity_questions_1 = [
        get_or_create_question(
            db,
            paper_type="integrity",
            question_type="single",
            title="发现实验数据与预期不一致时，最合适的做法是：",
            options_json=[
                {"label": "A", "text": "修改数据使其更好看"},
                {"label": "B", "text": "删除异常数据不记录"},
                {"label": "C", "text": "如实记录并分析原因"},
                {"label": "D", "text": "等待老师决定是否保留"},
            ],
            answer_json=["C"],
            score=30,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="integrity",
            question_type="multiple",
            title="以下哪些行为属于科研不端风险？",
            options_json=[
                {"label": "A", "text": "伪造数据"},
                {"label": "B", "text": "篡改实验结果"},
                {"label": "C", "text": "规范引用他人成果"},
                {"label": "D", "text": "一稿多投"},
            ],
            answer_json=["A", "B", "D"],
            score=30,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="integrity",
            question_type="essay",
            title="请简要说明你会如何处理导师要求“优化”实验结果的情况。",
            options_json=None,
            answer_json=None,
            score=0,
            created_by_user_id=teacher_user_id,
        ),
    ]

    integrity_questions_2 = [
        get_or_create_question(
            db,
            paper_type="integrity",
            question_type="boolean",
            title="只要论文结论正确，适当美化过程数据也是可以接受的。",
            options_json=[
                {"label": "A", "text": "对"},
                {"label": "B", "text": "错"},
            ],
            answer_json=[False],
            score=30,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="integrity",
            question_type="fill_blank",
            title="请填写你理解的“科研诚信”关键词。",
            options_json=None,
            answer_json=None,
            score=0,
            created_by_user_id=teacher_user_id,
        ),
        get_or_create_question(
            db,
            paper_type="integrity",
            question_type="single",
            title="以下哪项最符合学术规范？",
            options_json=[
                {"label": "A", "text": "重复投稿以提高录用率"},
                {"label": "B", "text": "未经同意使用他人数据"},
                {"label": "C", "text": "完整保留原始实验记录"},
                {"label": "D", "text": "省略不利结果"},
            ],
            answer_json=["C"],
            score=30,
            created_by_user_id=teacher_user_id,
        ),
    ]

    for idx, q in enumerate(survey_questions_1, start=1):
        ensure_paper_question_link(db, survey_1.id, q.id, idx)

    for idx, q in enumerate(survey_questions_2, start=1):
        ensure_paper_question_link(db, survey_2.id, q.id, idx)

    for idx, q in enumerate(integrity_questions_1, start=1):
        ensure_paper_question_link(db, integrity_1.id, q.id, idx)

    for idx, q in enumerate(integrity_questions_2, start=1):
        ensure_paper_question_link(db, integrity_2.id, q.id, idx)

    return {
        "survey_1": survey_1,
        "survey_2": survey_2,
        "integrity_1": integrity_1,
        "integrity_2": integrity_2,
    }

def get_or_create_attempt(
    db: Session,
    *,
    user_id: int,
    paper: AssessmentPaper,
    status: str,
    started_at: datetime,
    submitted_at: datetime | None,
    duration_seconds: int,
    total_score: int | None,
    force_submitted: bool,
) -> AssessmentAttempt:
    attempt = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.paper_id == paper.id,
            AssessmentAttempt.started_at == started_at,
        )
        .first()
    )

    if attempt:
        attempt.status = status
        attempt.submitted_at = submitted_at
        attempt.duration_seconds = duration_seconds
        attempt.total_score = total_score
        attempt.force_submitted = force_submitted
        return attempt

    attempt = AssessmentAttempt(
        user_id=user_id,
        paper_id=paper.id,
        paper_type=paper.paper_type,
        status=status,
        started_at=started_at,
        submitted_at=submitted_at,
        duration_seconds=duration_seconds,
        total_score=total_score,
        force_submitted=force_submitted,
    )
    db.add(attempt)
    db.flush()
    return attempt



def ensure_answer(
    db: Session,
    *,
    attempt_id: int,
    question_id: int,
    answer_json,
    score: int | None,
    judged_at: datetime | None,
):
    answer = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.attempt_id == attempt_id,
            AssessmentAnswer.question_id == question_id,
        )
        .first()
    )

    if answer:
        answer.answer_json = answer_json
        answer.score = score
        answer.judged_at = judged_at
        return answer

    answer = AssessmentAnswer(
        attempt_id=attempt_id,
        question_id=question_id,
        answer_json=answer_json,
        score=score,
        judged_at=judged_at,
    )
    db.add(answer)
    db.flush()
    return answer



def ensure_ai_report(
    db: Session,
    *,
    attempt_id: int,
    status: str,
    score_research_integrity: float | None,
    score_communication_anxiety: float | None,
    score_career_identity: float | None,
    score_humanistic_care: float | None,
    score_comprehensive_balance: float | None,
    total_score: float | None,
    summary: str | None,
    raw_response_json,
):
    report = (
        db.query(AssessmentAIReport)
        .filter(AssessmentAIReport.attempt_id == attempt_id)
        .first()
    )

    if report:
        report.status = status
        report.score_research_integrity = score_research_integrity
        report.score_communication_anxiety = score_communication_anxiety
        report.score_career_identity = score_career_identity
        report.score_humanistic_care = score_humanistic_care
        report.score_comprehensive_balance = score_comprehensive_balance
        report.total_score = total_score
        report.summary = summary
        report.raw_response_json = raw_response_json
        return report

    report = AssessmentAIReport(
        attempt_id=attempt_id,
        status=status,
        score_research_integrity=score_research_integrity,
        score_communication_anxiety=score_communication_anxiety,
        score_career_identity=score_career_identity,
        score_humanistic_care=score_humanistic_care,
        score_comprehensive_balance=score_comprehensive_balance,
        total_score=total_score,
        summary=summary,
        raw_response_json=raw_response_json,
    )
    db.add(report)
    db.flush()
    return report


# 按试卷拿题目
def get_paper_questions(db: Session, paper_id: int) -> list[AssessmentQuestion]:
    links = (
        db.query(AssessmentPaperQuestion)
        .filter(AssessmentPaperQuestion.paper_id == paper_id)
        .order_by(AssessmentPaperQuestion.sort_order.asc())
        .all()
    )

    question_ids = [item.question_id for item in links]
    if not question_ids:
        return []

    questions = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.id.in_(question_ids))
        .all()
    )
    question_map = {q.id: q for q in questions}

    return [question_map[qid] for qid in question_ids if qid in question_map]


def seed_attempts_and_reports(
    db: Session,
    *,
    zhangsan_user_id: int,
    lisi_user_id: int,
    paper_map: dict[str, AssessmentPaper],
):
    now = datetime.utcnow()

    # 张三：问卷一次，已完成
    survey_attempt_started = now - timedelta(days=7, hours=3)
    survey_attempt_submitted = survey_attempt_started + timedelta(minutes=18)

    survey_attempt = get_or_create_attempt(
        db,
        user_id=zhangsan_user_id,
        paper=paper_map["survey_1"],
        status="completed",
        started_at=survey_attempt_started,
        submitted_at=survey_attempt_submitted,
        duration_seconds=18 * 60,
        total_score=88,
        force_submitted=False,
    )

    for q in get_paper_questions(db, paper_map["survey_1"].id):
        if q.question_type == "single":
            answer_json = ["B"]
            score = 20
        elif q.question_type == "multiple":
            answer_json = ["A", "B", "D"]
            score = 18
        else:
            answer_json = "在一次小组任务中，我主动承担沟通协调工作并推动问题解决。"
            score = None

        ensure_answer(
            db,
            attempt_id=survey_attempt.id,
            question_id=q.id,
            answer_json=answer_json,
            score=score,
            judged_at=survey_attempt_submitted,
        )

    ensure_ai_report(
        db,
        attempt_id=survey_attempt.id,
        status="completed",
        score_research_integrity=80,
        score_communication_anxiety=76,
        score_career_identity=83,
        score_humanistic_care=85,
        score_comprehensive_balance=82,
        total_score=81.2,
        summary="建议继续加强高压场景下的沟通表达与科研规范训练。",
        raw_response_json={
            "source": "seed_demo_data",
            "paper_type": "survey",
        },
    )
    # 张三：诚信考核一次，已完成
    integrity_attempt_started = now - timedelta(days=4, hours=2)
    integrity_attempt_submitted = integrity_attempt_started + timedelta(minutes=22)

    integrity_attempt = get_or_create_attempt(
        db,
        user_id=zhangsan_user_id,
        paper=paper_map["integrity_1"],
        status="completed",
        started_at=integrity_attempt_started,
        submitted_at=integrity_attempt_submitted,
        duration_seconds=22 * 60,
        total_score=91,
        force_submitted=False,
    )

    for q in get_paper_questions(db, paper_map["integrity_1"].id):
        if q.question_type == "single":
            answer_json = ["C"]
            score = 30
        elif q.question_type == "multiple":
            answer_json = ["A", "B", "D"]
            score = 30
        else:
            answer_json = "我会坚持保留原始数据，并与导师沟通规范要求。"
            score = None

        ensure_answer(
            db,
            attempt_id=integrity_attempt.id,
            question_id=q.id,
            answer_json=answer_json,
            score=score,
            judged_at=integrity_attempt_submitted,
        )

    ensure_ai_report(
        db,
        attempt_id=integrity_attempt.id,
        status="completed",
        score_research_integrity=92,
        score_communication_anxiety=82,
        score_career_identity=85,
        score_humanistic_care=80,
        score_comprehensive_balance=86,
        total_score=85.0,
        summary="科研规范意识较强，建议继续提升复杂场景下的应对表达能力。",
        raw_response_json={
            "source": "seed_demo_data",
            "paper_type": "integrity",
        },
    )

    # 李四：一条处理中记录，用于测试“模型分析中”
    lisi_attempt_started = now - timedelta(days=2, hours=1)
    lisi_attempt_submitted = lisi_attempt_started + timedelta(minutes=20)

    lisi_attempt = get_or_create_attempt(
        db,
        user_id=lisi_user_id,
        paper=paper_map["survey_2"],
        status="ai_processing",
        started_at=lisi_attempt_started,
        submitted_at=lisi_attempt_submitted,
        duration_seconds=20 * 60,
        total_score=None,
        force_submitted=False,
    )

    for q in get_paper_questions(db, paper_map["survey_2"].id):
        if q.question_type == "boolean":
            answer_json = [True]
            score = None
        elif q.question_type == "single":
            answer_json = ["A"]
            score = None
        else:
            answer_json = "救死扶伤"
            score = None

        ensure_answer(
            db,
            attempt_id=lisi_attempt.id,
            question_id=q.id,
            answer_json=answer_json,
            score=score,
            judged_at=None,
        )

    ensure_ai_report(
        db,
        attempt_id=lisi_attempt.id,
        status="processing",
        score_research_integrity=None,
        score_communication_anxiety=None,
        score_career_identity=None,
        score_humanistic_care=None,
        score_comprehensive_balance=None,
        total_score=None,
        summary=None,
        raw_response_json={
            "source": "seed_demo_data",
            "paper_type": "survey",
            "status": "processing",
        },
    )



def main():
    db = SessionLocal()

    try:
        print("开始写入测试数据...")

        # 1. 学生名单库
        get_or_create_student_roster(
            db,
            student_no=USER_DATA["student_zhangsan"]["student_no"],
            real_name=USER_DATA["student_zhangsan"]["real_name"],
        )
        get_or_create_student_roster(
            db,
            student_no=USER_DATA["student_lisi"]["student_no"],
            real_name=USER_DATA["student_lisi"]["real_name"],
        )
        get_or_create_teacher_roster(
            db,
            teacher_no=USER_DATA["teacher"]["teacher_no"],
            real_name=USER_DATA["teacher"]["real_name"],
        )
        db.commit()

        # 2. 创建老师和学生账号
        teacher_auth = get_or_create_auth_user(
            db,
            phone=USER_DATA["teacher"]["phone"],
            real_name=USER_DATA["teacher"]["real_name"],
            role="teacher",
        )
        ensure_teacher_profile(
            db,
            auth_user=teacher_auth,
            teacher_no=USER_DATA["teacher"]["teacher_no"],
        )

        zhangsan_auth = get_or_create_auth_user(
            db,
            phone=USER_DATA["student_zhangsan"]["phone"],
            real_name=USER_DATA["student_zhangsan"]["real_name"],
            role="student",
        )
        ensure_student_profile(
            db,
            auth_user=zhangsan_auth,
            student_no=USER_DATA["student_zhangsan"]["student_no"],
        )

        lisi_auth = get_or_create_auth_user(
            db,
            phone=USER_DATA["student_lisi"]["phone"],
            real_name=USER_DATA["student_lisi"]["real_name"],
            role="student",
        )
        ensure_student_profile(
            db,
            auth_user=lisi_auth,
            student_no=USER_DATA["student_lisi"]["student_no"],
        )
        db.commit()

        # 3. 资源分类和资源
        categories = seed_categories(db)
        db.commit()

        resource_map = seed_resources(db, teacher_auth.id, categories)
        db.commit()

        # 4. 学生资源完成记录
        seed_resource_records(
            db,
            zhangsan_user_id=zhangsan_auth.id,
            lisi_user_id=lisi_auth.id,
            resource_map=resource_map,
        )
        db.commit()

        # 5. 试卷和题目
        paper_map = seed_papers_and_questions(db, teacher_auth.id)
        db.commit()

        # 6. 历史作答记录和 AI 报告
        seed_attempts_and_reports(
            db,
            zhangsan_user_id=zhangsan_auth.id,
            lisi_user_id=lisi_auth.id,
            paper_map=paper_map,
        )
        db.commit()

        print("测试数据写入完成。")
        print("老师：工号 T2020007 / 手机 13900000000 / 密码 123456")
        print("学生1：学号 20260001 / 手机 13800000000 / 密码 123456")
        print("学生2：学号 20260002 / 手机 13800000001 / 密码 123456")

    except Exception as exc:
        db.rollback()
        print("写入失败，已回滚：", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
