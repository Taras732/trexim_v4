"""
References service - CRUD operations for reference data
"""
import json
from pathlib import Path
from typing import Optional, Tuple, List

REFERENCES_FILE = Path(__file__).parent / "references.json"
BLOG_FILE = Path(__file__).parent / "blog_posts.json"


def load_references() -> dict:
    """Load all references from JSON file"""
    if not REFERENCES_FILE.exists():
        return {}
    with open(REFERENCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_references(data: dict) -> None:
    """Save references to JSON file"""
    with open(REFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_all_reference_types() -> dict:
    """Get all reference types with item counts"""
    refs = load_references()
    result = {}
    for key, value in refs.items():
        result[key] = {
            "name_uk": value.get("name_uk", key),
            "name_en": value.get("name_en", key),
            "count": len(value.get("items", []))
        }
    return result


def get_reference_items(reference_type: str) -> list:
    """Get all items for a reference type"""
    refs = load_references()
    if reference_type not in refs:
        return []
    return refs[reference_type].get("items", [])


def get_reference_meta(reference_type: str) -> dict:
    """Get metadata for a reference type"""
    refs = load_references()
    if reference_type not in refs:
        return {"name_uk": reference_type, "name_en": reference_type}
    return {
        "name_uk": refs[reference_type].get("name_uk", reference_type),
        "name_en": refs[reference_type].get("name_en", reference_type)
    }


def get_reference_item(reference_type: str, item_id: int) -> Optional[dict]:
    """Get a single reference item by ID"""
    items = get_reference_items(reference_type)
    for item in items:
        if item.get("id") == item_id:
            return item
    return None


def create_reference_item(reference_type: str, code: str, name_uk: str, name_en: str, active: bool = True) -> dict:
    """Create a new reference item"""
    refs = load_references()

    if reference_type not in refs:
        refs[reference_type] = {
            "name_uk": reference_type,
            "name_en": reference_type,
            "items": []
        }

    items = refs[reference_type].get("items", [])

    # Generate new ID
    max_id = max([item.get("id", 0) for item in items], default=0)
    new_id = max_id + 1

    new_item = {
        "id": new_id,
        "code": code,
        "name_uk": name_uk,
        "name_en": name_en,
        "active": active
    }

    refs[reference_type]["items"].append(new_item)
    save_references(refs)

    return new_item


def update_reference_item(reference_type: str, item_id: int, code: str, name_uk: str, name_en: str, active: bool) -> bool:
    """Update an existing reference item"""
    refs = load_references()

    if reference_type not in refs:
        return False

    items = refs[reference_type].get("items", [])
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            refs[reference_type]["items"][i] = {
                "id": item_id,
                "code": code,
                "name_uk": name_uk,
                "name_en": name_en,
                "active": active
            }
            save_references(refs)
            return True

    return False


def check_reference_usage(reference_type: str, item_id: int) -> Tuple[bool, List[str]]:
    """
    Check if a reference item is used in any blog post.
    Returns (is_used, list_of_post_slugs_using_it)
    """
    item = get_reference_item(reference_type, item_id)
    if not item:
        return False, []

    # Load blog posts
    if not BLOG_FILE.exists():
        return False, []

    with open(BLOG_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    using_posts = []

    for slug, post_data in posts.items():
        uk_data = post_data.get("uk", {})
        en_data = post_data.get("en", {})

        if reference_type == "blog_categories":
            # Check if category name matches
            if uk_data.get("category") == item.get("name_uk") or en_data.get("category") == item.get("name_en"):
                using_posts.append(slug)
        elif reference_type == "blog_tags":
            # Check if tag name is in tags array
            uk_tags = uk_data.get("tags", [])
            en_tags = en_data.get("tags", [])
            if item.get("name_uk") in uk_tags or item.get("name_en") in en_tags:
                using_posts.append(slug)

    return len(using_posts) > 0, using_posts


def delete_reference_item(reference_type: str, item_id: int) -> Tuple[bool, Optional[str]]:
    """
    Delete a reference item.
    Returns (success, error_message)
    """
    # Check if item is used in blog posts
    is_used, using_posts = check_reference_usage(reference_type, item_id)
    if is_used:
        return False, f"Не можна видалити: використовується в постах: {', '.join(using_posts)}"

    refs = load_references()

    if reference_type not in refs:
        return False, "Тип довідника не знайдено"

    items = refs[reference_type].get("items", [])
    original_length = len(items)

    refs[reference_type]["items"] = [item for item in items if item.get("id") != item_id]

    if len(refs[reference_type]["items"]) < original_length:
        save_references(refs)
        return True, None

    return False, "Запис не знайдено"


def get_active_categories() -> list:
    """Get active blog categories for dropdowns"""
    items = get_reference_items("blog_categories")
    return [item for item in items if item.get("active", True)]


def get_active_tags() -> list:
    """Get active blog tags for dropdowns"""
    items = get_reference_items("blog_tags")
    return [item for item in items if item.get("active", True)]
