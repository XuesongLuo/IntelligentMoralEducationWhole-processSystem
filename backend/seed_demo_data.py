"""
测试数据导入脚本，执行方式：
python seed_demo_data.py
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth_user import AuthUser
from app.models.learning_resource import LearningResource
from app.models.resource_category import ResourceCategory
from app.models.student_roster import StudentRoster
from app.models.student_user import StudentUser
from app.models.teacher_roster import TeacherRoster
from app.models.teacher_user import TeacherUser
from app.models.user_resource_record import UserResourceRecord


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
        {"title": "医患纠纷案例分析", "url": "https://www.bilibili.com/video/BV1V1cHe1EsQ?spm_id_from=333.788.videopod.episodes&p=1"},
        {"title": "医患沟通技巧训练", "url": "https://www.bilibili.com/video/BV1V1cHe1EsQ?spm_id_from=333.788.videopod.episodes&p=27"},
        {"title": "临床冲突处置流程", "url": "https://www.bilibili.com/video/BV1V1cHe1EsQ?spm_id_from=333.788.videopod.episodes&p=2"},
    ],
    "research_fraud": [
        {"title": "科研诚信规范导读", "url": "https://www.bilibili.com/video/BV1CjmEB3EAk?spm_id_from=333.788.videopod.sections"},
        {"title": "数据造假典型案例", "url": "https://www.bilibili.com/video/BV1nh4y1S7mC/?spm_id_from=333.337.videopod.sections"},
        {"title": "论文署名与引用规范", "url": "https://www.bilibili.com/video/BV1eg4y1z7kB/?spm_id_from=333.337.videopod.sections"},
    ],
    "medical_fairness": [
        {"title": "医疗资源公平分配讨论", "url": "https://www.bilibili.com/video/BV1fR4y1d7N5/?spm_id_from=333.337.videopod.sections"},
        {"title": "稀缺床位分配案例", "url": "https://www.bilibili.com/video/BV1VK411z7ec/?spm_id_from=333.337.videopod.sections"},
        {"title": "基层与三甲医疗资源对比", "url": "https://www.bilibili.com/video/BV1qp4y157sj/?spm_id_from=333.337.videopod.sections"},
    ],
    "privacy_protection": [
        {"title": "患者隐私保护规范", "url": "https://www.bilibili.com/video/BV1Y5YPzNEeQ/?spm_id_from=333.337.videopod.sections"},
        {"title": "病例信息脱敏基础", "url": "https://www.bilibili.com/video/BV1Hh4y197da/?spm_id_from=333.337.videopod.sections"},
        {"title": "电子病历权限控制", "url": "https://www.bilibili.com/video/BV1p34y1F7U2/?spm_id_from=333.337.videopod.sections"},
    ],
    "teamwork_conflict": [
        {"title": "医疗团队沟通协作", "url": "https://www.bilibili.com/video/BV1qce8eWEK2/?spm_id_from=333.337.videopod.sections"},
        {"title": "跨学科合作冲突处理", "url": "https://www.bilibili.com/video/BV1wQ4y1U7Ko/?spm_id_from=333.337.videopod.sections"},
        {"title": "值班交接中的责任边界", "url": "https://www.bilibili.com/video/BV1SzWnzSEkW/?spm_id_from=333.337.videopod.sections"},
    ],
    "public_health_response": [
        {"title": "公共卫生事件应急流程", "url": "https://www.bilibili.com/video/BV1op4y1D7BR/?spm_id_from=333.337.videopod.sections"},
        {"title": "突发疫情中的职业伦理", "url": "https://www.bilibili.com/video/BV1GE411x7Gk/?spm_id_from=333.337.videopod.sections"},
        {"title": "群体性事件舆情应对", "url": "https://www.bilibili.com/video/BV1uM4y1i7AB/?spm_id_from=333.337.videopod.sections"},
    ],
}

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
    teacher_user_id: int,
    categories: dict[str, ResourceCategory],
) -> dict[str, list[LearningResource]]:
    result: dict[str, list[LearningResource]] = {}
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
) -> None:
    now = datetime.utcnow()
    zhangsan_done = {
        "doctor_patient_dispute": [0, 1, 2],
        "research_fraud": [0, 1],
        "medical_fairness": [0, 1],
        "privacy_protection": [0],
        "teamwork_conflict": [0, 1],
        "public_health_response": [0],
    }
    for category_code, indexes in zhangsan_done.items():
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

    lisi_done = {
        "doctor_patient_dispute": [0],
        "research_fraud": [0],
    }
    for category_code, indexes in lisi_done.items():
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

        resource_map = seed_resources(db, teacher_auth.id, categories)
        db.commit()

        seed_resource_records(
            db,
            zhangsan_user_id=zhangsan_auth.id,
            lisi_user_id=lisi_auth.id,
            resource_map=resource_map,
        )
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
