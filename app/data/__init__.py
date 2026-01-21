from .blog_service import (
    load_posts,
    save_posts,
    get_post,
    create_post,
    update_post,
    delete_post,
    get_all_posts_for_admin,
    get_related_posts,
    generate_slug
)

__all__ = [
    'load_posts',
    'save_posts',
    'get_post',
    'create_post',
    'update_post',
    'delete_post',
    'get_all_posts_for_admin',
    'get_related_posts',
    'generate_slug'
]
