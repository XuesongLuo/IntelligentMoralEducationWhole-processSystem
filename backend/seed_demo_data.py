"""
测试数据导入脚本，执行方式：
python seed_demo_data.py
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.data.learning_resources import CATEGORY_DATA, LEGACY_DEMO_RESOURCE_TITLES, REAL_RESOURCE_DATA
from app.core.security import get_password_hash
from app.models.auth_user import AuthUser
from app.models.learning_resource import LearningResource
from app.models.resource_category import ResourceCategory
from app.models.student_roster import StudentRoster
from app.models.student_user import StudentUser
from app.models.teacher_roster import TeacherRoster
from app.models.teacher_user import TeacherUser


DEFAULT_PASSWORD = "123456"

USER_DATA = {
    "teacher": {
        "real_name": "李老师",
        "phone": "13900000000",
        "teacher_no": "2020007",
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

STUDENT_ROSTER_DATA = [
    {"student_no": "20260001", "real_name": "张三", "is_enabled": True},
    {"student_no": "20260002", "real_name": "李四", "is_enabled": True},
    {"student_no": "20260003", "real_name": "王五", "is_enabled": True},
    {"student_no": "20260004", "real_name": "赵六", "is_enabled": False},
]

TEACHER_ROSTER_DATA = [
    {"teacher_no": "2020007", "real_name": "李老师", "is_enabled": True},
    {"teacher_no": "2020008", "real_name": "王老师", "is_enabled": True},
    {"teacher_no": "2020009", "real_name": "赵老师", "is_enabled": True},
    {"teacher_no": "2020010", "real_name": "孙老师", "is_enabled": True},
]


def get_or_create_student_roster(
    db: Session,
    student_no: str,
    real_name: str,
    is_enabled: bool = True,
) -> StudentRoster:
    roster = db.query(StudentRoster).filter(StudentRoster.student_no == student_no).first()
    if roster:
        roster.real_name = real_name
        roster.is_enabled = is_enabled
        return roster

    roster = StudentRoster(student_no=student_no, real_name=real_name, is_enabled=is_enabled)
    db.add(roster)
    db.flush()
    return roster


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

    profile = StudentUser(auth_user_id=auth_user.id, student_no=student_no)
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
    result: dict[str, ResourceCategory] = {}
    for item in CATEGORY_DATA:
        category = db.query(ResourceCategory).filter(ResourceCategory.code == item["code"]).first()
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
    teacher_user_id: int | None,
    categories: dict[str, ResourceCategory],
) -> dict[str, list[LearningResource]]:
    result: dict[str, list[LearningResource]] = {}
    for category_code, items in REAL_RESOURCE_DATA.items():
        category = categories[category_code]
        result[category_code] = []
        for idx, item in enumerate(items, start=1):
            resource_query = db.query(LearningResource).filter(LearningResource.category_id == category.id)
            if item["url"]:
                resource_query = resource_query.filter(LearningResource.url == item["url"])
            else:
                resource_query = resource_query.filter(LearningResource.title == item["title"])
            resource = resource_query.first()
            if resource:
                resource.title = item["title"]
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

        cleanup_legacy_demo_resources(db, category.id, {item["url"] for item in items})
    return result


def cleanup_legacy_demo_resources(db: Session, category_id: int, real_urls: set[str]) -> None:
    legacy_resources = (
        db.query(LearningResource)
        .filter(
            LearningResource.category_id == category_id,
            LearningResource.title.in_(LEGACY_DEMO_RESOURCE_TITLES),
        )
        .all()
    )
    for resource in legacy_resources:
        if resource.url not in real_urls:
            db.delete(resource)


def main() -> None:
    db = SessionLocal()
    try:
        print("开始写入测试数据...")

        for item in STUDENT_ROSTER_DATA:
            get_or_create_student_roster(
                db,
                student_no=item["student_no"],
                real_name=item["real_name"],
                is_enabled=item["is_enabled"],
            )
        for item in TEACHER_ROSTER_DATA:
            get_or_create_teacher_roster(
                db,
                teacher_no=item["teacher_no"],
                real_name=item["real_name"],
                is_enabled=item["is_enabled"],
            )
        db.commit()

        teacher_auth = get_or_create_auth_user(
            db,
            phone=USER_DATA["teacher"]["phone"],
            real_name=USER_DATA["teacher"]["real_name"],
            role="teacher",
        )
        ensure_teacher_profile(db, auth_user=teacher_auth, teacher_no=USER_DATA["teacher"]["teacher_no"])

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

        categories = seed_categories(db)
        db.commit()

        seed_resources(db, teacher_auth.id, categories)
        db.commit()

        print("测试数据写入完成。")
        print("老师：工号 2020007 / 手机 13900000000 / 密码 123456")
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
