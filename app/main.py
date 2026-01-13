from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

try:
    from .config import settings
    from .routes import pages, admin
except ImportError:
    from config import settings
    from routes import pages, admin

app = FastAPI(title=settings.APP_NAME)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key="trexim-secret-key-2026")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(pages.router)
app.include_router(admin.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, lang: str = "uk"):
    return templates.TemplateResponse(
        "pages/home.html",
        {"request": request, "language": lang}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
