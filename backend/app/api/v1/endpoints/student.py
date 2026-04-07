from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.auth_user import AuthUser
from app.models.resource_category import ResourceCategory
from app.models.learning_resource import LearningResource
from app.models.user_resource_record import UserResourceRecord
from app.schemas.student import (
    StudentHomeData,
    StudentHomeProgressItem,
    StudentHomeResponseModel,
)

from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment_ai_report import AssessmentAIReport
from app.schemas.student import StudentHomeScoreDimension

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/home", response_model=StudentHomeResponseModel)
def get_student_home(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="只有学生可以访问学生首页")

    student_no = (
        current_user.student_profile.student_no
        if current_user.student_profile
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
            .join(
                LearningResource,
                LearningResource.id == UserResourceRecord.resource_id,
            )
            .filter(
                UserResourceRecord.user_id == current_user.id,
                UserResourceRecord.is_completed == True,
                LearningResource.category_id == category.id,
                LearningResource.is_visible == True,
            )
            .scalar()
            or 0
        )

        progress = 0.0
        if total_count > 0:
            progress = round(completed_count * 100 / total_count, 1)

        study_progress_list.append(
            StudentHomeProgressItem(
                id=category.id,
                name=category.name,
                progress=progress,
                leftCount=max(total_count - completed_count, 0),
            )
        )

    if study_progress_list:
        simulation_completion = round(
            sum(item.progress for item in study_progress_list) / len(study_progress_list),
            1,
        )
    else:
        simulation_completion = 0.0
    
    score_dimensions = []
    completed_reports = (
        db.query(AssessmentAIReport)
        .join(
            AssessmentAttempt,
            AssessmentAttempt.id == AssessmentAIReport.attempt_id,
        )
        .filter(
            AssessmentAttempt.user_id == current_user.id,
            AssessmentAttempt.status == "completed",
            AssessmentAIReport.status == "completed",
        )
        .all()
    )
    if completed_reports:
        research_scores = [
            item.score_research_integrity
            for item in completed_reports
            if item.score_research_integrity is not None
        ]

        if research_scores:
            score_dimensions.append(
                StudentHomeScoreDimension(
                    key="research_integrity",
                    name="科研诚信薄弱型",
                    best=max(research_scores),
                    worst=min(research_scores),
                )
            )

    communication_scores = [
        item.score_communication_anxiety
        for item in completed_reports
        if item.score_communication_anxiety is not None
    ]

    if communication_scores:
        score_dimensions.append(
            StudentHomeScoreDimension(
                key="communication_anxiety",
                name="医患沟通焦虑型",
                best=max(communication_scores),
                worst=min(communication_scores),
            )
        )
    
    career_identity_scores = [
        item.score_career_identity
        for item in completed_reports
        if item.score_career_identity is not None
    ]

    if career_identity_scores:
        score_dimensions.append(
            StudentHomeScoreDimension(
                key="career_identity",
                name="职业认同模糊型",
                best=max(career_identity_scores),
                worst=min(career_identity_scores),
            )
        )
    
    humanistic_care_scores = [
        item.score_humanistic_care
        for item in completed_reports
        if item.score_humanistic_care is not None
    ]

    if humanistic_care_scores:
        score_dimensions.append(
            StudentHomeScoreDimension(
                key="humanistic_care",
                name="人文关怀缺失型",
                best=max(humanistic_care_scores),
                worst=min(humanistic_care_scores),
            )
        )
    
    comprehensive_balance_scores = [
        item.score_comprehensive_balance
        for item in completed_reports
        if item.score_comprehensive_balance is not None
    ]

    if comprehensive_balance_scores:
        score_dimensions.append(
            StudentHomeScoreDimension(
                key="comprehensive_balance",
                name="综合发展均衡型",
                best=max(comprehensive_balance_scores),
                worst=min(comprehensive_balance_scores),
            )
        )


    data = StudentHomeData(
        studentId=student_no,
        studentName=current_user.real_name,
        phone=current_user.phone,
        simulationCompletion=simulation_completion,
        studyProgressList=study_progress_list,
        scoreDimensions=score_dimensions,
    )

    return StudentHomeResponseModel(data=data)