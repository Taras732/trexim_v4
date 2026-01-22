"""
API module - REST endpoints for frontend
"""
from fastapi import APIRouter

from .blog import router as blog_router
from .media import router as media_router
from .analytics import router as analytics_router

router = APIRouter(prefix="/api", tags=["api"])
router.include_router(blog_router)
router.include_router(media_router)
router.include_router(analytics_router)
