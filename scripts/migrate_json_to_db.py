"""
Script to migrate data from JSON files to PostgreSQL database
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.connection import db_session
from app.database.models import BlogCategory, BlogTag, BlogPost


def migrate_references():
    """Migrate categories and tags from references.json"""
    json_file = Path(__file__).parent.parent / "app" / "data" / "references.json"

    if not json_file.exists():
        print("references.json not found")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with db_session() as session:
        # Migrate categories
        categories = data.get("blog_categories", {}).get("items", [])
        for cat in categories:
            existing = session.query(BlogCategory).filter_by(code=cat["code"]).first()
            if not existing:
                new_cat = BlogCategory(
                    code=cat["code"],
                    name_uk=cat["name_uk"],
                    name_en=cat["name_en"],
                    is_active=cat.get("active", True),
                    created_at=datetime.utcnow()
                )
                session.add(new_cat)
                print(f"Added category: {cat['name_uk']}")
            else:
                print(f"Category exists: {cat['name_uk']}")

        # Migrate tags
        tags = data.get("blog_tags", {}).get("items", [])
        for tag in tags:
            existing = session.query(BlogTag).filter_by(code=tag["code"]).first()
            if not existing:
                new_tag = BlogTag(
                    code=tag["code"],
                    name_uk=tag["name_uk"],
                    name_en=tag["name_en"],
                    is_active=tag.get("active", True),
                    created_at=datetime.utcnow()
                )
                session.add(new_tag)
                print(f"Added tag: {tag['name_uk']}")
            else:
                print(f"Tag exists: {tag['name_uk']}")

    print("\nReferences migration completed!")


def migrate_posts():
    """Migrate blog posts from blog_posts.json"""
    json_file = Path(__file__).parent.parent / "app" / "data" / "blog_posts.json"

    if not json_file.exists():
        print("blog_posts.json not found")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    with db_session() as session:
        for slug, post_data in posts_data.items():
            # Check if post exists
            existing = session.query(BlogPost).filter_by(slug=slug).first()
            if existing:
                print(f"Post exists: {slug}")
                continue

            uk = post_data.get("uk", {})
            en = post_data.get("en", {})

            # Find category
            category_id = None
            if uk.get("category"):
                category = session.query(BlogCategory).filter_by(name_uk=uk["category"]).first()
                if category:
                    category_id = category.id

            # Create post
            new_post = BlogPost(
                slug=slug,
                title_uk=uk.get("title", ""),
                excerpt_uk=uk.get("excerpt", ""),
                content_uk=uk.get("content", ""),
                date_uk=uk.get("date", ""),
                title_en=en.get("title", ""),
                excerpt_en=en.get("excerpt", ""),
                content_en=en.get("content", ""),
                date_en=en.get("date", ""),
                category_id=category_id,
                emoji=uk.get("emoji", ""),
                color=uk.get("color", "orange"),
                read_time=int(uk.get("read_time", 5)),
                status="published",
                published_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Add tags
            for tag_name in uk.get("tags", []):
                tag = session.query(BlogTag).filter_by(name_uk=tag_name).first()
                if tag:
                    new_post.tags.append(tag)

            session.add(new_post)
            print(f"Added post: {slug}")

    print("\nPosts migration completed!")


if __name__ == "__main__":
    print("=" * 50)
    print("Migrating references...")
    print("=" * 50)
    migrate_references()

    print("\n" + "=" * 50)
    print("Migrating posts...")
    print("=" * 50)
    migrate_posts()

    print("\n" + "=" * 50)
    print("Migration completed!")
    print("=" * 50)
