"""
Analytics API endpoints
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import json
import uuid

try:
    from ..admin.auth import check_auth
    from ..analytics import (
        get_dashboard_summary,
        get_visitors_count,
        get_page_views,
        get_traffic_by_day,
        get_traffic_sources,
        get_popular_pages,
        get_device_stats,
        get_browser_stats,
        get_recent_events,
        get_form_submissions,
        log_event,
        create_session
    )
except ImportError:
    from admin.auth import check_auth
    from analytics import (
        get_dashboard_summary,
        get_visitors_count,
        get_page_views,
        get_traffic_by_day,
        get_traffic_sources,
        get_popular_pages,
        get_device_stats,
        get_browser_stats,
        get_recent_events,
        get_form_submissions,
        log_event,
        create_session
    )

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ============================================================================
# ADMIN ENDPOINTS (protected)
# ============================================================================

@router.get("/summary")
async def get_summary(request: Request, days: int = 7, _: bool = Depends(check_auth)):
    """Get complete dashboard summary (admin only)"""
    return get_dashboard_summary(days)


@router.get("/visitors")
async def get_visitors(request: Request, days: int = 7, _: bool = Depends(check_auth)):
    """Get visitors count (admin only)"""
    return get_visitors_count(days)


@router.get("/views")
async def get_views(request: Request, days: int = 7, _: bool = Depends(check_auth)):
    """Get page views count (admin only)"""
    return get_page_views(days)


@router.get("/traffic")
async def get_traffic(request: Request, days: int = 7, _: bool = Depends(check_auth)):
    """Get traffic by day for charts (admin only)"""
    return get_traffic_by_day(days)


@router.get("/sources")
async def get_sources(request: Request, days: int = 7, _: bool = Depends(check_auth)):
    """Get traffic sources (admin only)"""
    return get_traffic_sources(days)


@router.get("/pages")
async def get_pages(request: Request, limit: int = 10, days: int = 7, _: bool = Depends(check_auth)):
    """Get popular pages (admin only)"""
    return get_popular_pages(limit, days)


@router.get("/devices")
async def get_devices(request: Request, days: int = 7, _: bool = Depends(check_auth)):
    """Get device stats (admin only)"""
    return get_device_stats(days)


@router.get("/browsers")
async def get_browsers(request: Request, days: int = 7, _: bool = Depends(check_auth)):
    """Get browser stats (admin only)"""
    return get_browser_stats(days)


@router.get("/events")
async def get_events(request: Request, limit: int = 10, _: bool = Depends(check_auth)):
    """Get recent events (admin only)"""
    return get_recent_events(limit)


@router.get("/forms")
async def get_forms(request: Request, days: int = 30, limit: int = 10, _: bool = Depends(check_auth)):
    """Get form submissions (admin only)"""
    return get_form_submissions(days, limit)


# ============================================================================
# PUBLIC ENDPOINTS (for client-side tracking with consent)
# ============================================================================

@router.post("/event")
async def track_event(request: Request):
    """Track an event (public, requires consent cookie)"""
    try:
        # Check for consent cookie
        consent = request.cookies.get("analytics_consent")
        if consent != "accepted":
            return JSONResponse({"status": "skipped", "reason": "no_consent"})

        body = await request.json()
        event_type = body.get("type")
        event_data = body.get("data")
        path = body.get("path")
        session_id = body.get("session_id")

        if not event_type:
            return JSONResponse({"status": "error", "message": "type required"}, status_code=400)

        log_event(
            event_type=event_type,
            event_data=json.dumps(event_data) if event_data else None,
            session_id=session_id,
            path=path
        )

        return {"status": "ok"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@router.post("/session")
async def start_session(request: Request):
    """Start a tracking session (public, requires consent)"""
    try:
        # Check for consent cookie
        consent = request.cookies.get("analytics_consent")
        if consent != "accepted":
            return JSONResponse({"status": "skipped", "reason": "no_consent"})

        body = await request.json()

        # Get IP hash
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        import hashlib
        ip_hash = hashlib.sha256(f"{client_ip}trexim-analytics-2026".encode()).hexdigest()[:16]

        # Generate session ID
        session_id = str(uuid.uuid4())[:8]

        user_agent = request.headers.get("user-agent", "")

        create_session(
            session_id=session_id,
            ip_hash=ip_hash,
            user_agent=user_agent,
            consent=True
        )

        return {"status": "ok", "session_id": session_id}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
