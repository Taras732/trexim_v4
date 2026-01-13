from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from config import settings

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

# Simple authentication check
def check_auth(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return True

@router.get("", response_class=HTMLResponse)
async def admin_login(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/admin/dashboard")
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request}
    )

@router.post("/login")
async def admin_login_post(request: Request, password: str = Form(...)):
    if password == settings.ADMIN_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": "Невірний пароль"}
    )

@router.get("/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin")

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, _: bool = Depends(check_auth)):
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request}
    )

# Blog routes
@router.get("/blog", response_class=HTMLResponse)
async def admin_blog_list(request: Request, _: bool = Depends(check_auth)):
    # Mock blog posts data
    posts = [
        {"id": 1, "title": "Тестовий пост", "category": "Новини", "status": "Опубліковано", "date": "2026-01-13", "language": "uk"},
    ]
    return templates.TemplateResponse(
        "admin/blog_list.html",
        {"request": request, "posts": posts}
    )

@router.get("/blog/new", response_class=HTMLResponse)
async def admin_blog_new(request: Request, _: bool = Depends(check_auth)):
    return templates.TemplateResponse(
        "admin/blog_form.html",
        {"request": request, "post": None, "action": "create"}
    )

@router.get("/blog/{post_id}/edit", response_class=HTMLResponse)
async def admin_blog_edit(request: Request, post_id: int, _: bool = Depends(check_auth)):
    # Mock post data
    post = {"id": post_id, "title": "Тестовий пост", "slug": "test-post", "content": "Контент посту..."}
    return templates.TemplateResponse(
        "admin/blog_form.html",
        {"request": request, "post": post, "action": "update"}
    )

@router.post("/blog")
async def admin_blog_create(request: Request, _: bool = Depends(check_auth)):
    # TODO: Implement blog post creation
    return RedirectResponse(url="/admin/blog", status_code=303)

@router.post("/blog/{post_id}")
async def admin_blog_update(request: Request, post_id: int, _: bool = Depends(check_auth)):
    # TODO: Implement blog post update
    return RedirectResponse(url="/admin/blog", status_code=303)

@router.delete("/blog/{post_id}")
async def admin_blog_delete(request: Request, post_id: int, _: bool = Depends(check_auth)):
    # TODO: Implement blog post deletion
    return {"success": True}

# References routes
@router.get("/references", response_class=HTMLResponse)
async def admin_references_list(request: Request, _: bool = Depends(check_auth)):
    references = {
        "blog_categories": {"count": 5, "name_uk": "Категорії блогу", "name_en": "Blog Categories"},
        "post_statuses": {"count": 3, "name_uk": "Статуси постів", "name_en": "Post Statuses"},
        "cities": {"count": 10, "name_uk": "Міста", "name_en": "Cities"},
        "cargo_types": {"count": 8, "name_uk": "Типи вантажу", "name_en": "Cargo Types"},
        "order_statuses": {"count": 6, "name_uk": "Статуси замовлень", "name_en": "Order Statuses"},
        "languages": {"count": 2, "name_uk": "Мови", "name_en": "Languages"},
    }
    return templates.TemplateResponse(
        "admin/references_list.html",
        {"request": request, "references": references}
    )

@router.get("/references/{reference_type}", response_class=HTMLResponse)
async def admin_reference_items(request: Request, reference_type: str, _: bool = Depends(check_auth)):
    # Mock reference items
    items = []
    if reference_type == "blog_categories":
        items = [
            {"id": 1, "code": "news", "name_uk": "Новини", "name_en": "News", "description_uk": "Новини компанії", "description_en": "Company news", "active": True},
            {"id": 2, "code": "guides", "name_uk": "Гіди", "name_en": "Guides", "description_uk": "Корисні гіди", "description_en": "Useful guides", "active": True},
        ]
    elif reference_type == "cities":
        items = [
            {"id": 1, "code": "kyiv", "name_uk": "Київ", "name_en": "Kyiv", "active": True},
            {"id": 2, "code": "odesa", "name_uk": "Одеса", "name_en": "Odesa", "active": True},
            {"id": 3, "code": "lviv", "name_uk": "Львів", "name_en": "Lviv", "active": True},
        ]

    return templates.TemplateResponse(
        "admin/reference_items.html",
        {"request": request, "reference_type": reference_type, "items": items}
    )

@router.post("/references/{reference_type}")
async def admin_reference_create(request: Request, reference_type: str, _: bool = Depends(check_auth)):
    # TODO: Implement reference item creation
    return {"success": True}

@router.put("/references/{reference_type}/{item_id}")
async def admin_reference_update(request: Request, reference_type: str, item_id: int, _: bool = Depends(check_auth)):
    # TODO: Implement reference item update
    return {"success": True}

@router.delete("/references/{reference_type}/{item_id}")
async def admin_reference_delete(request: Request, reference_type: str, item_id: int, _: bool = Depends(check_auth)):
    # TODO: Implement reference item deletion
    return {"success": True}
