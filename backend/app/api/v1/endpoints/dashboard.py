from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=ResponseModel)
def get_dashboard_overview(current_user: User = Depends(get_current_user)):
    """
    先返回占位数据，确保前端能联调。
    后续再替换成真实统计逻辑：
    - MySQL 统计正式业务数据
    - Redis 读取草稿/会话/缓存
    """
    data = {
        "user": {
            "id": current_user.id,
            "real_name": current_user.real_name,
            "student_no": current_user.student_profile.student_no if current_user.student_profile else None,
            "teacher_no": current_user.teacher_profile.teacher_no if current_user.teacher_profile else None,
            "role": current_user.role,
        },
        "level": {
            "level_value": 0,
            "level_display": "无等级",
            "level_icon_type": "star",
            "ai_usage_seconds": 0,
            "ai_usage_text": "00:00:00",
        },
        "learning_stats": {
            "simulation_completion_rate": 0.0,
            "remaining_resources": 0,
            "categories": [
                {
                    "category_code": "doctor_patient_dispute",
                    "category_name": "医患纠纷处理",
                    "completed_count": 0,
                    "total_count": 0,
                    "completion_rate": 0.0,
                },
                {
                    "category_code": "research_fraud",
                    "category_name": "科研数据造假诱惑",
                    "completed_count": 0,
                    "total_count": 0,
                    "completion_rate": 0.0,
                },
                {
                    "category_code": "medical_fairness",
                    "category_name": "医疗资源分配公平性",
                    "completed_count": 0,
                    "total_count": 0,
                    "completion_rate": 0.0,
                },
                {
                    "category_code": "privacy_protection",
                    "category_name": "隐私保护困境",
                    "completed_count": 0,
                    "total_count": 0,
                    "completion_rate": 0.0,
                },
                {
                    "category_code": "teamwork_conflict",
                    "category_name": "团队协作冲突",
                    "completed_count": 0,
                    "total_count": 0,
                    "completion_rate": 0.0,
                },
                {
                    "category_code": "public_health_response",
                    "category_name": "公共卫生事件应对",
                    "completed_count": 0,
                    "total_count": 0,
                    "completion_rate": 0.0,
                },
            ],
        },
        "score_comparison": {
            "best_result": None,
            "worst_result": None,
        },
    }
    return ResponseModel(data=data)