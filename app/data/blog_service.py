import json
from pathlib import Path
from typing import Dict, Optional, List
import re

DATA_DIR = Path(__file__).parent
BLOG_FILE = DATA_DIR / "blog_posts.json"


def load_posts() -> Dict:
    """Load all blog posts from JSON file"""
    if not BLOG_FILE.exists():
        return {}
    with open(BLOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(posts: Dict) -> None:
    """Save all blog posts to JSON file"""
    with open(BLOG_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def get_post(slug: str) -> Optional[Dict]:
    """Get a single post by slug"""
    posts = load_posts()
    return posts.get(slug)


def create_post(slug: str, uk_data: Dict, en_data: Dict) -> bool:
    """Create a new blog post"""
    posts = load_posts()
    if slug in posts:
        return False
    posts[slug] = {"uk": uk_data, "en": en_data}
    save_posts(posts)
    return True


def update_post(slug: str, uk_data: Dict, en_data: Dict) -> bool:
    """Update an existing blog post"""
    posts = load_posts()
    if slug not in posts:
        return False
    posts[slug] = {"uk": uk_data, "en": en_data}
    save_posts(posts)
    return True


def delete_post(slug: str) -> bool:
    """Delete a blog post"""
    posts = load_posts()
    if slug not in posts:
        return False
    del posts[slug]
    save_posts(posts)
    return True


def get_all_posts_for_admin() -> List[Dict]:
    """Get all posts formatted for admin list"""
    posts = load_posts()
    result = []
    for slug, post_data in posts.items():
        uk_data = post_data.get("uk", {})
        result.append({
            "slug": slug,
            "title": uk_data.get("title", ""),
            "category": uk_data.get("category", ""),
            "date": uk_data.get("date", ""),
            "emoji": uk_data.get("emoji", ""),
            "color": uk_data.get("color", ""),
            "language": "uk/en"
        })
    return result


def get_related_posts(current_slug: str, lang: str, limit: int = 3) -> List[Dict]:
    """Get related posts excluding current one"""
    posts = load_posts()
    related = []
    lang_key = "uk" if lang == "uk" else "en"
    for slug, post_data in posts.items():
        if slug != current_slug and len(related) < limit:
            post = post_data.get(lang_key, post_data.get("en"))
            related.append({
                "slug": slug,
                "title": post["title"],
                "excerpt": post["excerpt"][:100] + "...",
                "category": post["category"],
                "date": post["date"],
                "emoji": post["emoji"],
                "color": post["color"]
            })
    return related


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    # Transliteration map for Ukrainian
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
        'є': 'ye', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y',
        'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu', 'я': 'ya', "'": '', 'ʼ': ''
    }

    slug = title.lower()
    # Transliterate Ukrainian
    for ukr, lat in translit_map.items():
        slug = slug.replace(ukr, lat)
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug
