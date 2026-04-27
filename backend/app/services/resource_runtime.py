from datetime import datetime
import time

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.redis import get_redis
from app.models.assessment_attempt import AssessmentAttempt
from app.models.learning_resource import LearningResource
from app.models.resource_category import ResourceCategory
from app.models.user_resource_record import UserResourceRecord
from app.schemas.resource import ResourceCategoryProgressItem, ResourceListData, ResourceListItem


redis_client = get_redis()


def resource_session_key(user_id: int) -> str:
    return f"resource:session:{user_id}"


def resource_total_key(user_id: int) -> str:
    return f"resource:active-total:{user_id}"


def format_duration(total_seconds: int | float | None) -> str:
    seconds = max(int(total_seconds or 0), 0)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remain = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remain:02d}"


def heartbeat_resource_session(user_id: int) -> dict:
    now = int(time.time())
    session_key = resource_session_key(user_id)
    total_key = resource_total_key(user_id)

    if not redis_client.exists(session_key):
        redis_client.hset(
            session_key,
            mapping={
                "started_at": now,
                "last_heartbeat_at": now,
            },
        )
        redis_client.expire(session_key, 86400 * 30)
        redis_client.setnx(total_key, 0)
        redis_client.expire(total_key, 86400 * 365)
        return {"active_seconds": int(redis_client.get(total_key) or 0)}

    session_data = redis_client.hgetall(session_key)
    last_heartbeat_at = int(session_data.get("last_heartbeat_at", now))
    delta = max(0, min(now - last_heartbeat_at, 30))

    if delta:
        redis_client.incrby(total_key, delta)

    redis_client.hset(session_key, "last_heartbeat_at", now)
    redis_client.expire(session_key, 86400 * 30)
    redis_client.expire(total_key, 86400 * 365)

    return {"active_seconds": int(redis_client.get(total_key) or 0)}


def get_resource_total_active_seconds(user_id: int) -> int:
    return int(redis_client.get(resource_total_key(user_id)) or 0)


def get_exam_total_active_seconds(db: Session, user_id: int) -> int:
    total = (
        db.query(func.coalesce(func.sum(AssessmentAttempt.duration_seconds), 0))
        .filter(
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.submitted_at.isnot(None),
        )
        .scalar()
    )
    return int(total or 0)


def get_total_ai_usage_duration(db: Session, user_id: int) -> str:
    total_seconds = get_exam_total_active_seconds(db, user_id) + get_resource_total_active_seconds(user_id)
    return format_duration(total_seconds)


def build_category_progress_list(db: Session, user_id: int) -> list[ResourceCategoryProgressItem]:
    categories = (
        db.query(ResourceCategory)
        .filter(ResourceCategory.is_enabled == True)
        .order_by(ResourceCategory.sort_order.asc(), ResourceCategory.id.asc())
        .all()
    )

    items: list[ResourceCategoryProgressItem] = []
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
                UserResourceRecord.user_id == user_id,
                UserResourceRecord.is_completed == True,
                LearningResource.category_id == category.id,
                LearningResource.is_visible == True,
            )
            .scalar()
            or 0
        )

        progress = round(completed_count * 100 / total_count, 1) if total_count else 0.0

        items.append(
            ResourceCategoryProgressItem(
                id=category.id,
                code=category.code,
                name=category.name,
                progress=progress,
                completedCount=completed_count,
                totalCount=total_count,
                remainingCount=max(total_count - completed_count, 0),
            )
        )

    return items


def build_resource_list(
    db: Session,
    *,
    user_id: int,
    category_code: str,
    page_num: int,
    page_size: int,
    include_hidden: bool = False,
) -> ResourceListData:
    category = (
        db.query(ResourceCategory)
        .filter(
            ResourceCategory.code == category_code,
            ResourceCategory.is_enabled == True,
        )
        .first()
    )
    if not category:
        raise ValueError("category not found")

    query = db.query(LearningResource).filter(LearningResource.category_id == category.id)
    if not include_hidden:
        query = query.filter(LearningResource.is_visible == True)

    query = query.order_by(LearningResource.sort_order.asc(), LearningResource.id.asc())
    total = query.count()
    resources = query.offset((page_num - 1) * page_size).limit(page_size).all()

    resource_ids = [item.id for item in resources]
    record_map: dict[int, UserResourceRecord] = {}
    if resource_ids:
        record_rows = (
            db.query(UserResourceRecord)
            .filter(
                UserResourceRecord.user_id == user_id,
                UserResourceRecord.resource_id.in_(resource_ids),
            )
            .all()
        )
        record_map = {item.resource_id: item for item in record_rows}

    records = []
    for item in resources:
        record = record_map.get(item.id)
        records.append(
            ResourceListItem(
                id=item.id,
                title=item.title,
                url=item.url,
                isVisible=item.is_visible,
                completed=bool(record and record.is_completed),
                clickCount=record.click_count if record else 0,
                lastClickedAt=record.last_clicked_at.strftime("%Y-%m-%d %H:%M:%S")
                if record and record.last_clicked_at
                else "",
            )
        )

    return ResourceListData(
        categoryId=category.id,
        categoryCode=category.code,
        categoryName=category.name,
        pageNum=page_num,
        pageSize=page_size,
        total=total,
        records=records,
    )


def mark_resource_completed(db: Session, *, user_id: int, resource: LearningResource) -> UserResourceRecord:
    record = (
        db.query(UserResourceRecord)
        .filter(
            UserResourceRecord.user_id == user_id,
            UserResourceRecord.resource_id == resource.id,
        )
        .first()
    )

    now = datetime.utcnow()
    if record:
        record.click_count += 1
        record.is_completed = True
        if not record.first_clicked_at:
            record.first_clicked_at = now
        record.last_clicked_at = now
        return record

    record = UserResourceRecord(
        user_id=user_id,
        resource_id=resource.id,
        first_clicked_at=now,
        last_clicked_at=now,
        click_count=1,
        is_completed=True,
    )
    db.add(record)
    return record
