"""
Trexim - AI Logistics Platform
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path

try:
    from .config import settings
    from .routes import pages, blog
    from .api import router as api_router
    from .admin import router as admin_router
    from .analytics import AnalyticsMiddleware
except ImportError:
    from config import settings
    from routes import pages, blog
    from api import router as api_router
    from admin import router as admin_router
    from analytics import AnalyticsMiddleware

# Initialize app
app = FastAPI(title=settings.APP_NAME)

# Middleware
app.add_middleware(SessionMiddleware, secret_key="trexim-secret-key-2026")
app.add_middleware(AnalyticsMiddleware)

# Paths
base_dir = Path(__file__).parent
static_dir = base_dir / "static"
templates_dir = base_dir / "templates"
uploads_dir = base_dir.parent / "uploads"

# Static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Uploads (user-uploaded media)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Templates
templates = Jinja2Templates(directory=str(templates_dir))

# =============================================================================
# ROUTERS
# =============================================================================

# API routes (must be before page routes to avoid conflicts)
app.include_router(api_router)

# Page routes
app.include_router(pages.router)
app.include_router(blog.router)

# Admin routes
app.include_router(admin_router)

# =============================================================================
# ROOT ROUTES
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, lang: str = "uk"):
    """Home page"""
    return templates.TemplateResponse(
        "pages/home.html",
        {"request": request, "language": lang}
    )


@app.get("/sitemap.xml")
async def sitemap():
    """Sitemap for SEO"""
    return FileResponse(static_dir / "sitemap.xml", media_type="application/xml")


@app.get("/robots.txt")
async def robots():
    """Robots.txt for SEO"""
    return FileResponse(static_dir / "robots.txt", media_type="text/plain")


@app.get("/favicon.ico")
async def favicon():
    """Favicon"""
    return FileResponse(static_dir / "images" / "favicon.ico", media_type="image/x-icon")


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Custom 404 page"""
    if exc.status_code == 404:
        lang = request.query_params.get("lang", "uk")
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "language": lang},
            status_code=404
        )
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)


@app.get("/404", response_class=HTMLResponse)
async def page_not_found(request: Request, lang: str = "uk"):
    """Direct 404 page route for testing"""
    return templates.TemplateResponse(
        "pages/404.html",
        {"request": request, "language": lang}
    )


# =============================================================================
# DEV SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
