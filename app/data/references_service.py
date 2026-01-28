"""
References service - CRUD operations using SQLAlchemy
"""
from typing import Optional, Tuple, List
from datetime import datetime

from sqlalchemy import select
from ..database.connection import db_session
from ..database.models import BlogCategory, BlogTag, BlogPost


def get_all_reference_types() -> dict:
    """Get all reference types with item counts"""
    with db_session() as session:
        categories_count = len(session.execute(select(BlogCategory)).scalars().all())
        tags_count = len(session.execute(select(BlogTag)).scalars().all())

        return {
            "blog_categories": {
                "name_uk": "Категорії блогу",
                "name_en": "Blog Categories",
                "count": categories_count
            },
            "blog_tags": {
                "name_uk": "Теги блогу",
                "name_en": "Blog Tags",
                "count": tags_count
            }
        }


def get_reference_items(reference_type: str) -> list:
    """Get all items for a reference type"""
    with db_session() as session:
        if reference_type == "blog_categories":
            items = session.execute(select(BlogCategory).order_by(BlogCategory.id)).scalars().all()
            return [{"id": i.id, "code": i.code, "name_uk": i.name_uk, "name_en": i.name_en, "active": i.is_active} for i in items]
        elif reference_type == "blog_tags":
            items = session.execute(select(BlogTag).order_by(BlogTag.id)).scalars().all()
            return [{"id": i.id, "code": i.code, "name_uk": i.name_uk, "name_en": i.name_en, "active": i.is_active} for i in items]
        return []


def get_reference_meta(reference_type: str) -> dict:
    """Get metadata for a reference type"""
    meta = {
        "blog_categories": {"name_uk": "Категорії блогу", "name_en": "Blog Categories"},
        "blog_tags": {"name_uk": "Теги блогу", "name_en": "Blog Tags"}
    }
    return meta.get(reference_type, {"name_uk": reference_type, "name_en": reference_type})


def get_reference_item(reference_type: str, item_id: int) -> Optional[dict]:
    """Get a single reference item by ID"""
    with db_session() as session:
        if reference_type == "blog_categories":
            item = session.execute(select(BlogCategory).where(BlogCategory.id == item_id)).scalar_one_or_none()
        elif reference_type == "blog_tags":
            item = session.execute(select(BlogTag).where(BlogTag.id == item_id)).scalar_one_or_none()
        else:
            return None

        if item:
            return {"id": item.id, "code": item.code, "name_uk": item.name_uk, "name_en": item.name_en, "active": item.is_active}
        return None


def create_reference_item(reference_type: str, code: str, name_uk: str, name_en: str, active: bool = True) -> dict:
    """Create a new reference item"""
    try:
        with db_session() as session:
            if reference_type == "blog_categories":
                item = BlogCategory(code=code, name_uk=name_uk, name_en=name_en, is_active=active, created_at=datetime.utcnow())
            elif reference_type == "blog_tags":
                item = BlogTag(code=code, name_uk=name_uk, name_en=name_en, is_active=active, created_at=datetime.utcnow())
            else:
                return {}

            session.add(item)
            session.flush()
            return {"id": item.id, "code": item.code, "name_uk": item.name_uk, "name_en": item.name_en, "active": item.is_active}
    except Exception as e:
        print(f"Error creating reference item: {e}")
        return {}


def update_reference_item(reference_type: str, item_id: int, code: str, name_uk: str, name_en: str, active: bool) -> bool:
    """Update an existing reference item"""
    try:
        with db_session() as session:
            if reference_type == "blog_categories":
                item = session.execute(select(BlogCategory).where(BlogCategory.id == item_id)).scalar_one_or_none()
            elif reference_type == "blog_tags":
                item = session.execute(select(BlogTag).where(BlogTag.id == item_id)).scalar_one_or_none()
            else:
                return False

            if item:
                item.code = code
                item.name_uk = name_uk
                item.name_en = name_en
                item.is_active = active
                return True
            return False
    except Exception as e:
        print(f"Error updating reference item: {e}")
        return False


def check_reference_usage(reference_type: str, item_id: int) -> Tuple[bool, List[str]]:
    """Check if a reference item is used in any blog post"""
    with db_session() as session:
        if reference_type == "blog_categories":
            posts = session.execute(select(BlogPost).where(BlogPost.category_id == item_id)).scalars().all()
            return len(posts) > 0, [post.slug for post in posts]
        elif reference_type == "blog_tags":
            tag = session.execute(select(BlogTag).where(BlogTag.id == item_id)).scalar_one_or_none()
            if tag and tag.posts:
                return True, [post.slug for post in tag.posts]
        return False, []


def delete_reference_item(reference_type: str, item_id: int) -> Tuple[bool, Optional[str]]:
    """Delete a reference item"""
    is_used, using_posts = check_reference_usage(reference_type, item_id)
    if is_used:
        return False, f"Не можна видалити: використовується в постах: {', '.join(using_posts)}"

    try:
        with db_session() as session:
            if reference_type == "blog_categories":
                item = session.execute(select(BlogCategory).where(BlogCategory.id == item_id)).scalar_one_or_none()
            elif reference_type == "blog_tags":
                item = session.execute(select(BlogTag).where(BlogTag.id == item_id)).scalar_one_or_none()
            else:
                return False, "Тип довідника не знайдено"

            if item:
                session.delete(item)
                return True, None
            return False, "Запис не знайдено"
    except Exception as e:
        return False, str(e)


def get_active_categories() -> list:
    """Get active blog categories for dropdowns"""
    with db_session() as session:
        items = session.execute(select(BlogCategory).where(BlogCategory.is_active == True)).scalars().all()
        return [{"id": i.id, "code": i.code, "name_uk": i.name_uk, "name_en": i.name_en, "active": i.is_active} for i in items]


def get_active_tags() -> list:
    """Get active blog tags for dropdowns"""
    with db_session() as session:
        items = session.execute(select(BlogTag).where(BlogTag.is_active == True)).scalars().all()
        return [{"id": i.id, "code": i.code, "name_uk": i.name_uk, "name_en": i.name_en, "active": i.is_active} for i in items]
