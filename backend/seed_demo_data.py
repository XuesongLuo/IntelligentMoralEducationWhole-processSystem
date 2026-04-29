"""
重置并导入演示数据，执行方式：
python seed_demo_data.py
"""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.core.redis import get_redis
from app.core.security import get_password_hash
from app.models.auth_user import AuthUser
from app.models.teacher_roster import TeacherRoster
from app.models.teacher_user import TeacherUser
from app.services.resource_runtime import (
    LEVEL_COMPLETION_SECONDS,
    MAX_LEVEL_VALUE,
    resource_session_key,
    resource_total_key,
)
from import_assessment_bank_from_excel import DEFAULT_INPUT_DIR, import_excel_file
from seed_learning_resources_core import seed_categories, seed_resources


DEFAULT_PASSWORD = "123456"
TABLES_TO_TRUNCATE = [
    "assessment_ai_reports",
    "assessment_answers",
    "assessment_attempts",
    "assessment_paper_questions",
    "assessment_questions",
    "assessment_papers",
    "user_resource_records",
    "learning_resources",
    "resource_categories",
    "student_users",
    "teacher_users",
    "student_roster",
    "teacher_roster",
    "teacher_invites",
    "auth_users",
    "users",
]
redis_client = get_redis()

ADMIN_USER_DATA = {
    "real_name": "管理员",
    "phone": "13900000000",
    "teacher_no": "admin",
    "role": "teacher",
}


def get_or_create_teacher_roster(
    db: Session,
    teacher_no: str,
    real_name: str,
    is_enabled: bool = True,
) -> TeacherRoster:
    roster = db.query(TeacherRoster).filter(TeacherRoster.teacher_no == teacher_no).first()
    if roster:
        roster.real_name = real_name
        roster.is_enabled = is_enabled
        return roster

    roster = TeacherRoster(teacher_no=teacher_no, real_name=real_name, is_enabled=is_enabled)
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
        user.password_hash = get_password_hash(password)
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


def reset_database(db: Session) -> None:
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    try:
        existing_tables = {row[0] for row in db.execute(text("SHOW TABLES")).all()}
        for table_name in TABLES_TO_TRUNCATE:
            if table_name in existing_tables:
                db.execute(text(f"TRUNCATE TABLE `{table_name}`"))
        db.commit()
    finally:
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.commit()


def import_assessment_bank(db: Session, input_dir: Path | None = None) -> None:
    base_dir = Path(__file__).resolve().parent
    target_dir = (base_dir / (input_dir or DEFAULT_INPUT_DIR)).resolve()
    excel_files = sorted(path for path in target_dir.glob("*.xlsx") if not path.name.startswith("~$"))
    if not excel_files:
        raise FileNotFoundError(f"未找到 Excel 文件: {target_dir}")

    for path in excel_files:
        import_excel_file(db, path)
    db.commit()


def seed_admin_level(user_id: int) -> None:
    total_seconds = LEVEL_COMPLETION_SECONDS * MAX_LEVEL_VALUE
    redis_client.set(resource_total_key(user_id), total_seconds)
    redis_client.expire(resource_total_key(user_id), 86400 * 365)
    redis_client.delete(resource_session_key(user_id))


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("开始重置并写入演示数据...")

        print("正在清空数据库并重置自增 ID...")
        reset_database(db)

        print("正在重新导入题库 Excel...")
        import_assessment_bank(db)

        print("正在写入管理员账号...")
        get_or_create_teacher_roster(
            db,
            teacher_no=ADMIN_USER_DATA["teacher_no"],
            real_name=ADMIN_USER_DATA["real_name"],
            is_enabled=True,
        )

        admin_auth = get_or_create_auth_user(
            db,
            phone=ADMIN_USER_DATA["phone"],
            real_name=ADMIN_USER_DATA["real_name"],
            role=ADMIN_USER_DATA["role"],
        )
        ensure_teacher_profile(db, auth_user=admin_auth, teacher_no=ADMIN_USER_DATA["teacher_no"])
        db.commit()

        print("正在写入资源分类与真实学习资源...")
        categories = seed_categories(db)
        db.commit()

        seed_resources(db, admin_auth.id, categories)
        db.commit()

        print("正在写入管理员满级时长...")
        seed_admin_level(admin_auth.id)

        print("演示数据写入完成。")
        print("管理员：工号 admin / 手机 13900000000 / 密码 123456")
        print("管理员等级：已按满级 125 级写入")
    except Exception as exc:
        db.rollback()
        print("写入失败，已回滚：", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
