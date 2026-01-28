"""
Blog API - JSON endpoints for blog functionality
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..data import get_all_posts

router = APIRouter(prefix="/blog", tags=["blog"])

# Category mapping for filter keys
CATEGORY_MAP = {
    # Ukrainian
    "Новини": "news",
    "Гіди": "guides",
    "Технології": "tech",
    "Оновлення": "updates",
    # English
    "News": "news",
    "Guides": "guides",
    "Technology": "tech",
    "Updates": "updates"
}


@router.get("/posts")
async def get_blog_posts(lang: str = "uk"):
    """
    Get all blog posts for client-side filtering

    Returns list of posts with:
    - slug, title, excerpt, category, category_key
    - date, read_time, emoji, color
    """
    posts = get_all_posts(lang)

    result = []
    for post in posts:
        result.append({
            "slug": post.get("slug", ""),
            "title": post.get("title", ""),
            "excerpt": post.get("excerpt", ""),
            "category": post.get("category", ""),
            "category_key": CATEGORY_MAP.get(post.get("category", ""), "news"),
            "date": post.get("date", ""),
            "read_time": post.get("read_time", "5"),
            "emoji": post.get("emoji", ""),
            "color": post.get("color", "orange")
        })

    return JSONResponse(content=result)
