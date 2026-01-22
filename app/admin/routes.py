"""
Admin routes - all admin panel endpoints
"""
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .auth import check_auth

try:
    from ..config import settings
    from ..data import (
        get_all_posts_for_admin,
        get_post,
        create_post,
        update_post,
        delete_post,
        generate_slug,
        get_all_reference_types,
        get_reference_items,
        get_reference_meta,
        create_reference_item,
        update_reference_item,
        delete_reference_item,
        get_active_categories,
        get_active_tags
    )
except ImportError:
    from config import settings
    from data import (
        get_all_posts_for_admin,
        get_post,
        create_post,
        update_post,
        delete_post,
        generate_slug,
        get_all_reference_types,
        get_reference_items,
        get_reference_meta,
        create_reference_item,
        update_reference_item,
        delete_reference_item,
        get_active_categories,
        get_active_tags
    )

router = APIRouter(prefix="/admin", tags=["admin"])

# Templates - use admin templates from main templates folder
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# =============================================================================
# AUTH ROUTES
# =============================================================================

@router.get("", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Admin login page"""
    if request.session.get("authenticated"):
        return RedirectResponse(url="/admin/dashboard")
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login")
async def admin_login_post(request: Request, password: str = Form(...)):
    """Process admin login"""
    if password == settings.ADMIN_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": "Невірний пароль"}
    )


@router.get("/logout")
async def admin_logout(request: Request):
    """Admin logout"""
    request.session.clear()
    return RedirectResponse(url="/admin")


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, _: bool = Depends(check_auth)):
    """Admin dashboard"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


# =============================================================================
# BLOG ROUTES
# =============================================================================

@router.get("/blog", response_class=HTMLResponse)
async def admin_blog_list(request: Request, _: bool = Depends(check_auth)):
    """Blog posts list"""
    posts = get_all_posts_for_admin()
    return templates.TemplateResponse(
        "admin/blog_list.html",
        {"request": request, "posts": posts}
    )


@router.get("/blog/new", response_class=HTMLResponse)
async def admin_blog_new(request: Request, _: bool = Depends(check_auth)):
    """New blog post form"""
    categories = get_active_categories()
    tags = get_active_tags()
    return templates.TemplateResponse(
        "admin/blog_form.html",
        {
            "request": request,
            "post": None,
            "slug": None,
            "action": "create",
            "categories": categories,
            "tags": tags
        }
    )


@router.get("/blog/{slug}/edit", response_class=HTMLResponse)
async def admin_blog_edit(request: Request, slug: str, _: bool = Depends(check_auth)):
    """Edit blog post form"""
    post_data = get_post(slug)
    if not post_data:
        return RedirectResponse(url="/admin/blog", status_code=303)

    categories = get_active_categories()
    tags = get_active_tags()
    return templates.TemplateResponse(
        "admin/blog_form.html",
        {
            "request": request,
            "post": post_data,
            "slug": slug,
            "action": "update",
            "categories": categories,
            "tags": tags
        }
    )


@router.post("/blog")
async def admin_blog_create(
    request: Request,
    _: bool = Depends(check_auth),
    slug: str = Form(None),
    title_uk: str = Form(...),
    title_en: str = Form(...),
    excerpt_uk: str = Form(...),
    excerpt_en: str = Form(...),
    category_uk: str = Form(...),
    category_en: str = Form(...),
    date_uk: str = Form(...),
    date_en: str = Form(...),
    read_time: str = Form(...),
    emoji: str = Form(...),
    color: str = Form("orange"),
    tags_uk: str = Form(""),
    tags_en: str = Form(""),
    content_uk: str = Form(...),
    content_en: str = Form(...)
):
    """Create new blog post"""
    if not slug:
        slug = generate_slug(title_uk)

    uk_data = {
        "title": title_uk,
        "excerpt": excerpt_uk,
        "category": category_uk,
        "date": date_uk,
        "read_time": read_time,
        "emoji": emoji,
        "color": color,
        "tags": [t.strip() for t in tags_uk.split(",") if t.strip()],
        "content": content_uk
    }

    en_data = {
        "title": title_en,
        "excerpt": excerpt_en,
        "category": category_en,
        "date": date_en,
        "read_time": read_time,
        "emoji": emoji,
        "color": color,
        "tags": [t.strip() for t in tags_en.split(",") if t.strip()],
        "content": content_en
    }

    success = create_post(slug, uk_data, en_data)
    if not success:
        return templates.TemplateResponse(
            "admin/blog_form.html",
            {"request": request, "post": None, "slug": None, "action": "create", "error": "Стаття з таким slug вже існує"}
        )

    return RedirectResponse(url="/admin/blog", status_code=303)


@router.post("/blog/{slug}/update")
async def admin_blog_update_post(
    request: Request,
    slug: str,
    _: bool = Depends(check_auth),
    title_uk: str = Form(...),
    title_en: str = Form(...),
    excerpt_uk: str = Form(...),
    excerpt_en: str = Form(...),
    category_uk: str = Form(...),
    category_en: str = Form(...),
    date_uk: str = Form(...),
    date_en: str = Form(...),
    read_time: str = Form(...),
    emoji: str = Form(...),
    color: str = Form("orange"),
    tags_uk: str = Form(""),
    tags_en: str = Form(""),
    content_uk: str = Form(...),
    content_en: str = Form(...)
):
    """Update blog post"""
    uk_data = {
        "title": title_uk,
        "excerpt": excerpt_uk,
        "category": category_uk,
        "date": date_uk,
        "read_time": read_time,
        "emoji": emoji,
        "color": color,
        "tags": [t.strip() for t in tags_uk.split(",") if t.strip()],
        "content": content_uk
    }

    en_data = {
        "title": title_en,
        "excerpt": excerpt_en,
        "category": category_en,
        "date": date_en,
        "read_time": read_time,
        "emoji": emoji,
        "color": color,
        "tags": [t.strip() for t in tags_en.split(",") if t.strip()],
        "content": content_en
    }

    update_post(slug, uk_data, en_data)
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.post("/blog/{slug}/delete")
async def admin_blog_delete_post(request: Request, slug: str, _: bool = Depends(check_auth)):
    """Delete blog post (form submission)"""
    delete_post(slug)
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.delete("/blog/{slug}")
async def admin_blog_delete_api(request: Request, slug: str, _: bool = Depends(check_auth)):
    """Delete blog post (API)"""
    success = delete_post(slug)
    return JSONResponse({"success": success})


# =============================================================================
# REFERENCES ROUTES
# =============================================================================

@router.get("/references", response_class=HTMLResponse)
async def admin_references_list(request: Request, _: bool = Depends(check_auth)):
    """References list"""
    references = get_all_reference_types()
    return templates.TemplateResponse(
        "admin/references_list.html",
        {"request": request, "references": references}
    )


@router.get("/references/{reference_type}", response_class=HTMLResponse)
async def admin_reference_items(request: Request, reference_type: str, _: bool = Depends(check_auth)):
    """Reference items list"""
    items = get_reference_items(reference_type)
    meta = get_reference_meta(reference_type)
    return templates.TemplateResponse(
        "admin/reference_items.html",
        {
            "request": request,
            "reference_type": reference_type,
            "reference_name": meta["name_uk"],
            "items": items
        }
    )


@router.post("/references/{reference_type}")
async def admin_reference_create(
    request: Request,
    reference_type: str,
    _: bool = Depends(check_auth),
    code: str = Form(...),
    name_uk: str = Form(...),
    name_en: str = Form(...),
    active: str = Form(None)
):
    """Create new reference item"""
    is_active = active == "true" or active == "on"
    create_reference_item(reference_type, code, name_uk, name_en, is_active)
    return RedirectResponse(url=f"/admin/references/{reference_type}", status_code=303)


@router.post("/references/{reference_type}/{item_id}/update")
async def admin_reference_update(
    request: Request,
    reference_type: str,
    item_id: int,
    _: bool = Depends(check_auth),
    code: str = Form(...),
    name_uk: str = Form(...),
    name_en: str = Form(...),
    active: str = Form(None)
):
    """Update reference item"""
    is_active = active == "true" or active == "on"
    update_reference_item(reference_type, item_id, code, name_uk, name_en, is_active)
    return RedirectResponse(url=f"/admin/references/{reference_type}", status_code=303)


@router.post("/references/{reference_type}/{item_id}/delete")
async def admin_reference_delete(
    request: Request,
    reference_type: str,
    item_id: int,
    _: bool = Depends(check_auth)
):
    """Delete reference item"""
    success, error = delete_reference_item(reference_type, item_id)
    if not success and error:
        # Return to page with error message
        items = get_reference_items(reference_type)
        meta = get_reference_meta(reference_type)
        return templates.TemplateResponse(
            "admin/reference_items.html",
            {
                "request": request,
                "reference_type": reference_type,
                "reference_name": meta["name_uk"],
                "items": items,
                "error": error
            }
        )
    return RedirectResponse(url=f"/admin/references/{reference_type}", status_code=303)
