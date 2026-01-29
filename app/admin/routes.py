"""
Admin routes - all admin panel endpoints
"""
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional

from .auth import check_auth, login_user, logout_user, needs_setup

try:
    from ..config import settings
    from ..logger import log_admin_action, get_log_files, read_log_file
    from ..media import upload_image
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
    from logger import log_admin_action, get_log_files, read_log_file
    from media import upload_image
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
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "needs_setup": needs_setup()}
    )


@router.post("/login")
async def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Process admin login"""
    success, error = login_user(request, username, password)
    if success:
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": error, "needs_setup": needs_setup()}
    )


@router.get("/logout")
async def admin_logout(request: Request):
    """Admin logout"""
    logout_user(request)
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
    emoji: str = Form(""),
    color: str = Form("orange"),
    tags_uk: str = Form(""),
    tags_en: str = Form(""),
    content_uk: str = Form(...),
    content_en: str = Form(...),
    show_on_homepage: str = Form(None),
    cover_image: Optional[UploadFile] = File(None)
):
    """Create new blog post"""
    if not slug:
        slug = generate_slug(title_uk)

    # Handle image upload to Cloudinary
    image_url = None
    if cover_image and cover_image.filename:
        try:
            print(f"Uploading image: {cover_image.filename}")
            result = await upload_image(cover_image, "blog")
            image_url = result.get("optimized") or result.get("original")
            print(f"Upload success: {image_url}")
        except Exception as e:
            print(f"Upload error: {e}")

    # Parse show_on_homepage checkbox
    is_show_on_homepage = show_on_homepage == "true" or show_on_homepage == "on"

    uk_data = {
        "title": title_uk,
        "excerpt": excerpt_uk,
        "category": category_uk,
        "date": date_uk,
        "read_time": read_time,
        "emoji": emoji,
        "color": color,
        "tags": [t.strip() for t in tags_uk.split(",") if t.strip()],
        "content": content_uk,
        "image_url": image_url,
        "show_on_homepage": is_show_on_homepage
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
        "content": content_en,
        "image_url": image_url
    }

    success = create_post(slug, uk_data, en_data)
    if not success:
        categories = get_active_categories()
        tags = get_active_tags()
        return templates.TemplateResponse(
            "admin/blog_form.html",
            {"request": request, "post": None, "slug": None, "action": "create", "error": "Стаття з таким slug вже існує", "categories": categories, "tags": tags}
        )

    username = request.session.get("username", "unknown")
    log_admin_action("CREATE_POST", username, f"slug={slug}")
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
    emoji: str = Form(""),
    color: str = Form("orange"),
    tags_uk: str = Form(""),
    tags_en: str = Form(""),
    content_uk: str = Form(...),
    content_en: str = Form(...),
    show_on_homepage: str = Form(None),
    cover_image: Optional[UploadFile] = File(None)
):
    """Update blog post"""
    # Handle image upload to Cloudinary
    image_url = None
    if cover_image and cover_image.filename:
        try:
            print(f"Uploading image: {cover_image.filename}")
            result = await upload_image(cover_image, "blog")
            image_url = result.get("optimized") or result.get("original")
            print(f"Upload success: {image_url}")
        except Exception as e:
            print(f"Upload error: {e}")

    # Parse show_on_homepage checkbox
    is_show_on_homepage = show_on_homepage == "true" or show_on_homepage == "on"

    uk_data = {
        "title": title_uk,
        "excerpt": excerpt_uk,
        "category": category_uk,
        "date": date_uk,
        "read_time": read_time,
        "emoji": emoji,
        "color": color,
        "tags": [t.strip() for t in tags_uk.split(",") if t.strip()],
        "content": content_uk,
        "show_on_homepage": is_show_on_homepage
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

    # Add image URL if new image was uploaded
    if image_url:
        uk_data["image_url"] = image_url
        en_data["image_url"] = image_url

    update_post(slug, uk_data, en_data)
    username = request.session.get("username", "unknown")
    log_admin_action("UPDATE_POST", username, f"slug={slug}")
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.post("/blog/{slug}/delete")
async def admin_blog_delete_post(request: Request, slug: str, _: bool = Depends(check_auth)):
    """Delete blog post (form submission)"""
    delete_post(slug)
    username = request.session.get("username", "unknown")
    log_admin_action("DELETE_POST", username, f"slug={slug}")
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


# =============================================================================
# LOGS ROUTES
# =============================================================================

@router.get("/logs", response_class=HTMLResponse)
async def admin_logs(request: Request, _: bool = Depends(check_auth)):
    """System logs viewer"""
    files = get_log_files()
    return templates.TemplateResponse(
        "admin/logs.html",
        {"request": request, "files": files}
    )


# API endpoint for logs (used by the logs viewer page)
@router.get("/api/logs")
async def admin_logs_api(
    request: Request,
    _: bool = Depends(check_auth),
    file: str = "errors.log",
    lines: int = 200,
    level: str = None
):
    """Get log file contents"""
    log_lines = read_log_file(file, lines, level)
    return JSONResponse({"lines": log_lines})
