from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/about.html",
        {"request": request, "language": lang}
    )

@router.get("/partners", response_class=HTMLResponse)
async def partners(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/partners.html",
        {"request": request, "language": lang}
    )

@router.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/pricing.html",
        {"request": request, "language": lang}
    )

@router.get("/services", response_class=HTMLResponse)
async def services(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/services.html",
        {"request": request, "language": lang}
    )

@router.get("/tools", response_class=HTMLResponse)
async def tools(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/tools.html",
        {"request": request, "language": lang}
    )

@router.get("/blog", response_class=HTMLResponse)
async def blog(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/blog.html",
        {"request": request, "language": lang}
    )

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/contact.html",
        {"request": request, "language": lang}
    )
