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
from app.schemas.common import ResponseModel
from app.schemas.student import (
    StudentHomeData,
    StudentHomeProgressItem,
    StudentHomeResponseModel,
    StudentHomeScoreDimension,
)

router = APIRouter(prefix="/teacher", tags=["teacher"])


def build_home_data(target_user: AuthUser, db: Session) -> StudentHomeData:
    user_no = (
        target_user.teacher_profile.teacher_no
        if target_user.role == "teacher" and target_user.teacher_profile
        else target_user.student_profile.student_no
        if target_user.role == "student" and target_user.student_profile
        else ""
    )

    categories = (
        db.query(ResourceCategory)
        .filter(ResourceCategory.is_enabled == True)
        .order_by(ResourceCategory.sort_order.asc(), ResourceCategory.id.asc())
        .all()
    )

    study_progress_list = []
    for category in categories:
        total_count = (
            db.query(func.count(LearningResource.id))
            .filter(
                LearningResource.category_id == category.id,
                LearningResource.is_visible == True,
            )
            .scalar()
            or 0
        )

        completed_count = (
            db.query(func.count(UserResourceRecord.id))
            .join(LearningResource, LearningResource.id == UserResourceRecord.resource_id)
            .filter(
                UserResourceRecord.user_id == target_user.id,
                UserResourceRecord.is_completed == True,
                LearningResource.category_id == category.id,
                LearningResource.is_visible == True,
            )
            .scalar()
            or 0
        )

        progress = round(completed_count * 100 / total_count, 1) if total_count > 0 else 0.0

        study_progress_list.append(
            StudentHomeProgressItem(
                id=category.id,
                name=category.name,
                progress=progress,
                leftCount=max(total_count - completed_count, 0),
            )
        )

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

    teacher_item = {
        "id": current_user.id,
        "role": "teacher",
        "real_name": current_user.real_name,
        "teacher_no": current_user.teacher_profile.teacher_no if current_user.teacher_profile else "",
        "label": f"{current_user.teacher_profile.teacher_no if current_user.teacher_profile else current_user.phone} {current_user.real_name}",
    }

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

    return ResponseModel(data=[teacher_item, *student_items])


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