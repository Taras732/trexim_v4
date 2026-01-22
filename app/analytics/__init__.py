"""
Analytics module for Trexim
"""
from .middleware import AnalyticsMiddleware
from .models import log_page_view, log_event, log_form_submission, create_session
from .service import (
    get_dashboard_summary,
    get_visitors_count,
    get_page_views,
    get_traffic_by_day,
    get_traffic_sources,
    get_popular_pages,
    get_device_stats,
    get_browser_stats,
    get_recent_events,
    get_form_submissions
)

__all__ = [
    "AnalyticsMiddleware",
    "log_page_view",
    "log_event",
    "log_form_submission",
    "create_session",
    "get_dashboard_summary",
    "get_visitors_count",
    "get_page_views",
    "get_traffic_by_day",
    "get_traffic_sources",
    "get_popular_pages",
    "get_device_stats",
    "get_browser_stats",
    "get_recent_events",
    "get_form_submissions"
]
