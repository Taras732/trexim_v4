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

from .config import settings
from .routes import pages, blog
from .api import router as api_router
from .admin import router as admin_router
from .analytics import AnalyticsMiddleware
from .logger import logger
from .data import get_homepage_posts

# Initialize app
app = FastAPI(title=settings.APP_NAME)

# Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)
app.add_middleware(AnalyticsMiddleware)

# WWW redirect middleware
@app.middleware("http")
async def redirect_www_to_non_www(request: Request, call_next):
    host = request.headers.get("host", "")
    if host.startswith("www."):
        non_www_host = host.replace("www.", "", 1)
        url = request.url.replace(scheme="https", netloc=non_www_host)
        return HTMLResponse(
            content="",
            status_code=301,
            headers={"Location": str(url)}
        )
    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info(f"Starting {settings.APP_NAME} (env: {settings.APP_ENV})")
    logger.info(f"Debug mode: {settings.DEBUG}")

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
    try:
        blog_posts = get_homepage_posts(lang, limit=6)
    except Exception as e:
        logger.error(f"Failed to load homepage posts: {e}")
    return templates.TemplateResponse(        "pages/home.html",
        {"request": request, "language": lang, "blog_posts": blog_posts}
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
    """Custom error pages with logging"""
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code}: {request.method} {request.url.path} - {exc.detail}")
    elif exc.status_code >= 400:
        logger.warning(f"HTTP {exc.status_code}: {request.method} {request.url.path}")

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
