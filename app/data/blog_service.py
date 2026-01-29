"""
Blog service - CRUD operations using SQLAlchemy
"""
import re
from typing import Dict, Optional, List
from datetime import datetime

from sqlalchemy import select
from ..database.connection import db_session
from ..database.models import BlogPost, BlogCategory, BlogTag


def get_post(slug: str) -> Optional[Dict]:
    """Get a single post by slug"""
    with db_session() as session:
        post = session.execute(
            select(BlogPost).where(BlogPost.slug == slug)
        ).scalar_one_or_none()

        if not post:
            return None

        # Get category name
        category_uk = ""
        category_en = ""
        if post.category:
            category_uk = post.category.name_uk
            category_en = post.category.name_en

        # Get tags
        tags_uk = [tag.name_uk for tag in post.tags]
        tags_en = [tag.name_en for tag in post.tags]

        return {
            "uk": {
                "title": post.title_uk,
                "excerpt": post.excerpt_uk,
                "content": post.content_uk,
                "category": category_uk,
                "date": post.date_uk,
                "read_time": str(post.read_time) if post.read_time else "5",
                "emoji": post.emoji,
                "color": post.color,
                "tags": tags_uk,
                "image": post.image_url
            },
            "en": {
                "title": post.title_en,
                "excerpt": post.excerpt_en,
                "content": post.content_en,
                "category": category_en,
                "date": post.date_en,
                "read_time": str(post.read_time) if post.read_time else "5",
                "emoji": post.emoji,
                "color": post.color,
                "tags": tags_en,
                "image": post.image_url
            }
        }


def create_post(slug: str, uk_data: Dict, en_data: Dict) -> bool:
    """Create a new blog post"""
    try:
        with db_session() as session:
            # Check if slug exists
            existing = session.execute(
                select(BlogPost).where(BlogPost.slug == slug)
            ).scalar_one_or_none()

            if existing:
                return False

            # Find category by name
            category_id = None
            if uk_data.get("category"):
                category = session.execute(
                    select(BlogCategory).where(BlogCategory.name_uk == uk_data["category"])
                ).scalar_one_or_none()
                if category:
                    category_id = category.id

            # Create post
            post = BlogPost(
                slug=slug,
                title_uk=uk_data.get("title", ""),
                excerpt_uk=uk_data.get("excerpt", ""),
                content_uk=uk_data.get("content", ""),
                date_uk=uk_data.get("date", ""),
                title_en=en_data.get("title", ""),
                excerpt_en=en_data.get("excerpt", ""),
                content_en=en_data.get("content", ""),
                date_en=en_data.get("date", ""),
                category_id=category_id,
                emoji=uk_data.get("emoji", ""),
                color=uk_data.get("color", "orange"),
                read_time=int(uk_data.get("read_time", 5)),
                image_url=uk_data.get("image_url"),
                status="published",
                published_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Add tags
            for tag_name in uk_data.get("tags", []):
                tag = session.execute(
                    select(BlogTag).where(BlogTag.name_uk == tag_name)
                ).scalar_one_or_none()
                if tag:
                    post.tags.append(tag)

            session.add(post)
            return True
    except Exception as e:
        print(f"Error creating post: {e}")
        return False


def update_post(slug: str, uk_data: Dict, en_data: Dict) -> bool:
    """Update an existing blog post"""
    try:
        with db_session() as session:
            post = session.execute(
                select(BlogPost).where(BlogPost.slug == slug)
            ).scalar_one_or_none()

            if not post:
                return False

            # Find category by name
            if uk_data.get("category"):
                category = session.execute(
                    select(BlogCategory).where(BlogCategory.name_uk == uk_data["category"])
                ).scalar_one_or_none()
                if category:
                    post.category_id = category.id

            # Update fields
            post.title_uk = uk_data.get("title", post.title_uk)
            post.excerpt_uk = uk_data.get("excerpt", post.excerpt_uk)
            post.content_uk = uk_data.get("content", post.content_uk)
            post.date_uk = uk_data.get("date", post.date_uk)

            post.title_en = en_data.get("title", post.title_en)
            post.excerpt_en = en_data.get("excerpt", post.excerpt_en)
            post.content_en = en_data.get("content", post.content_en)
            post.date_en = en_data.get("date", post.date_en)

            post.emoji = uk_data.get("emoji", post.emoji)
            post.color = uk_data.get("color", post.color)
            post.read_time = int(uk_data.get("read_time", post.read_time or 5))
            if uk_data.get("image_url"):
                post.image_url = uk_data.get("image_url")
            post.updated_at = datetime.utcnow()

            # Update tags
            post.tags.clear()
            for tag_name in uk_data.get("tags", []):
                tag = session.execute(
                    select(BlogTag).where(BlogTag.name_uk == tag_name)
                ).scalar_one_or_none()
                if tag:
                    post.tags.append(tag)

            return True
    except Exception as e:
        print(f"Error updating post: {e}")
        return False


def delete_post(slug: str) -> bool:
    """Delete a blog post"""
    try:
        with db_session() as session:
            post = session.execute(
                select(BlogPost).where(BlogPost.slug == slug)
            ).scalar_one_or_none()

            if not post:
                return False

            session.delete(post)
            return True
    except Exception as e:
        print(f"Error deleting post: {e}")
        return False


def get_all_posts_for_admin() -> List[Dict]:
    """Get all posts formatted for admin list"""
    with db_session() as session:
        posts = session.execute(
            select(BlogPost).order_by(BlogPost.created_at.desc())
        ).scalars().all()

        result = []
        for post in posts:
            category_name = post.category.name_uk if post.category else ""
            result.append({
                "slug": post.slug,
                "title": post.title_uk,
                "category": category_name,
                "date": post.date_uk,
                "emoji": post.emoji,
                "color": post.color,
                "status": post.status,
                "language": "uk/en"
            })
        return result


def get_all_posts(lang: str = "uk") -> List[Dict]:
    """Get all published posts for public view"""
    with db_session() as session:
        posts = session.execute(
            select(BlogPost)
            .where(BlogPost.status == "published")
            .order_by(BlogPost.published_at.desc())
        ).scalars().all()

        result = []
        for post in posts:
            if lang == "uk":
                result.append({
                    "slug": post.slug,
                    "title": post.title_uk,
                    "excerpt": post.excerpt_uk,
                    "category": post.category.name_uk if post.category else "",
                    "date": post.date_uk,
                    "read_time": post.read_time,
                    "emoji": post.emoji,
                    "color": post.color,
                    "tags": [tag.name_uk for tag in post.tags]
                })
            else:
                result.append({
                    "slug": post.slug,
                    "title": post.title_en,
                    "excerpt": post.excerpt_en,
                    "category": post.category.name_en if post.category else "",
                    "date": post.date_en,
                    "read_time": post.read_time,
                    "emoji": post.emoji,
                    "color": post.color,
                    "tags": [tag.name_en for tag in post.tags]
                })
        return result


def get_post_for_view(slug: str, lang: str = "uk") -> Optional[Dict]:
    """Get a single post for public view"""
    with db_session() as session:
        post = session.execute(
            select(BlogPost).where(BlogPost.slug == slug)
        ).scalar_one_or_none()

        if not post:
            return None

        if lang == "uk":
            return {
                "slug": post.slug,
                "title": post.title_uk,
                "excerpt": post.excerpt_uk,
                "content": post.content_uk,
                "category": post.category.name_uk if post.category else "",
                "date": post.date_uk,
                "read_time": post.read_time,
                "emoji": post.emoji,
                "color": post.color,
                "tags": [tag.name_uk for tag in post.tags],
                "image": post.image_url
            }
        else:
            return {
                "slug": post.slug,
                "title": post.title_en,
                "excerpt": post.excerpt_en,
                "content": post.content_en,
                "category": post.category.name_en if post.category else "",
                "date": post.date_en,
                "read_time": post.read_time,
                "emoji": post.emoji,
                "color": post.color,
                "tags": [tag.name_en for tag in post.tags],
                "image": post.image_url
            }


def get_related_posts(current_slug: str, lang: str, limit: int = 3) -> List[Dict]:
    """Get related posts excluding current one"""
    with db_session() as session:
        posts = session.execute(
            select(BlogPost)
            .where(BlogPost.slug != current_slug, BlogPost.status == "published")
            .order_by(BlogPost.published_at.desc())
            .limit(limit)
        ).scalars().all()

        result = []
        for post in posts:
            if lang == "uk":
                result.append({
                    "slug": post.slug,
                    "title": post.title_uk,
                    "excerpt": (post.excerpt_uk or "")[:100] + "...",
                    "category": post.category.name_uk if post.category else "",
                    "date": post.date_uk,
                    "emoji": post.emoji,
                    "color": post.color
                })
            else:
                result.append({
                    "slug": post.slug,
                    "title": post.title_en,
                    "excerpt": (post.excerpt_en or "")[:100] + "...",
                    "category": post.category.name_en if post.category else "",
                    "date": post.date_en,
                    "emoji": post.emoji,
                    "color": post.color
                })
        return result


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
        'є': 'ye', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y',
        'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu', 'я': 'ya', "'": '', 'ʼ': ''
    }

    slug = title.lower()
    for ukr, lat in translit_map.items():
        slug = slug.replace(ukr, lat)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    slug = re.sub(r'-+', '-', slug)
    return slug
