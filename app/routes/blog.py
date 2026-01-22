"""
Blog routes - blog pages and related functionality
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

try:
    from ..data import get_post, get_related_posts
except ImportError:
    from data import get_post, get_related_posts

router = APIRouter()
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/blog", response_class=HTMLResponse)
async def blog_list(request: Request, lang: str = "uk"):
    """Blog listing page"""
    return templates.TemplateResponse(
        "pages/blog.html",
        {"request": request, "language": lang}
    )


@router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str, lang: str = "uk"):
    """Individual blog post page"""
    post_data = get_post(slug)
    if not post_data:
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "language": lang},
            status_code=404
        )

    lang_key = "uk" if lang == "uk" else "en"
    post = post_data.get(lang_key, post_data.get("en"))

    return templates.TemplateResponse(
        "pages/blog_post.html",
        {
            "request": request,
            "language": lang,
            "post": post,
            "related_posts": get_related_posts(slug, lang)
        }
    )
