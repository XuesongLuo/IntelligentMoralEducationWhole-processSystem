"""
真实学习资源导入脚本，执行方式：
python seed_learning_resources.py
"""

from app.core.database import SessionLocal
from app.data.learning_resources import REAL_RESOURCE_DATA
from seed_learning_resources_core import seed_categories, seed_resources


def main() -> None:
    db = SessionLocal()
    try:
        print("开始写入真实学习资源...")
        categories = seed_categories(db)
        resource_map = seed_resources(db, teacher_user_id=None, categories=categories)
        db.commit()

        total = sum(len(items) for items in resource_map.values())
        expected_total = sum(len(items) for items in REAL_RESOURCE_DATA.values())
        print(f"真实学习资源写入完成：{total}/{expected_total} 条。")
    except Exception as exc:
        db.rollback()
        print("真实学习资源写入失败，已回滚：", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
