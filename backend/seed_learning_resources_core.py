"""
学习资源种子导入的共享逻辑。
"""

from sqlalchemy.orm import Session

from app.data.learning_resources import CATEGORY_DATA, REAL_RESOURCE_DATA
from app.models.learning_resource import LearningResource
from app.models.resource_category import ResourceCategory


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
    return result
