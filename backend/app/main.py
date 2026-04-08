from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.redis import redis_client
from app.models.auth_user import AuthUser  # noqa: F401
from app.models.student_user import StudentUser  # noqa: F401
from app.models.teacher_user import TeacherUser  # noqa: F401
from app.models.student_roster import StudentRoster  # noqa: F401
from app.models.teacher_roster import TeacherRoster  # noqa: F401
from app.models.teacher_invite import TeacherInvite  # noqa: F401

from app.models.resource_category import ResourceCategory  # noqa: F401
from app.models.learning_resource import LearningResource  # noqa: F401
from app.models.user_resource_record import UserResourceRecord  # noqa: F401

from app.models.assessment_paper import AssessmentPaper  # noqa: F401
from app.models.assessment_question import AssessmentQuestion  # noqa: F401
from app.models.assessment_paper_question import AssessmentPaperQuestion  # noqa: F401
from app.models.assessment_attempt import AssessmentAttempt  # noqa: F401
from app.models.assessment_answer import AssessmentAnswer  # noqa: F401
from app.models.assessment_ai_report import AssessmentAIReport  # noqa: F401

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 联调阶段先放开，正式环境再收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    try:
        redis_client.ping()
        print("Redis connected.")
    except Exception as exc:
        print(f"Redis connection failed: {exc}")


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} is running"}
