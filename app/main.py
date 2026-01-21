from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
import os
from pathlib import Path

try:
    from .config import settings
    from .routes import pages, admin
except ImportError:
    from config import settings
    from routes import pages, admin

app = FastAPI(title=settings.APP_NAME)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key="trexim-secret-key-2026")

# Determine base directory (works for both local and production)
base_dir = Path(__file__).parent
static_dir = base_dir / "static"
templates_dir = base_dir / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates = Jinja2Templates(directory=str(templates_dir))

# Include routers
app.include_router(pages.router)
app.include_router(admin.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/home.html",
        {"request": request, "language": lang}
    )

@app.get("/sitemap.xml")
async def sitemap():
    return FileResponse(static_dir / "sitemap.xml", media_type="application/xml")

@app.get("/robots.txt")
async def robots():
    return FileResponse(static_dir / "robots.txt", media_type="text/plain")

# Custom 404 error handler
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        lang = request.query_params.get("lang", "uk")
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "language": lang},
            status_code=404
        )
    # For other HTTP errors, return default response
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)

# Direct 404 page route for testing
@app.get("/404", response_class=HTMLResponse)
async def page_not_found(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/404.html",
        {"request": request, "language": lang}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
