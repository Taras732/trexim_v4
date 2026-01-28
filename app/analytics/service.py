"""
Analytics service - query functions for dashboard using SQLAlchemy
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, distinct, text, case, and_
from sqlalchemy.sql import extract

from ..database.connection import db_session
from ..database.models import PageView, FormSubmission, AnalyticsSession, AnalyticsEvent


def get_visitors_count(days: int = 7) -> dict:
    """Get unique visitors count and change percentage"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    prev_cutoff = datetime.utcnow() - timedelta(days=days * 2)

    with db_session() as session:
        # Current period
        current = session.execute(
            select(func.count(distinct(PageView.ip_hash)))
            .where(PageView.timestamp >= cutoff)
        ).scalar() or 0

        # Previous period
        previous = session.execute(
            select(func.count(distinct(PageView.ip_hash)))
            .where(and_(
                PageView.timestamp >= prev_cutoff,
                PageView.timestamp < cutoff
            ))
        ).scalar() or 0

    # Calculate change
    if previous > 0:
        change = round(((current - previous) / previous) * 100, 1)
    else:
        change = 100 if current > 0 else 0

    return {"count": current, "change": change}


def get_page_views(days: int = 7) -> dict:
    """Get total page views and change percentage"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    prev_cutoff = datetime.utcnow() - timedelta(days=days * 2)

    with db_session() as session:
        # Current period
        current = session.execute(
            select(func.count())
            .select_from(PageView)
            .where(PageView.timestamp >= cutoff)
        ).scalar() or 0

        # Previous period
        previous = session.execute(
            select(func.count())
            .select_from(PageView)
            .where(and_(
                PageView.timestamp >= prev_cutoff,
                PageView.timestamp < cutoff
            ))
        ).scalar() or 0

    # Calculate change
    if previous > 0:
        change = round(((current - previous) / previous) * 100, 1)
    else:
        change = 100 if current > 0 else 0

    return {"count": current, "change": change}


def get_avg_session_time(days: int = 7) -> dict:
    """Get average session time (from events if available)"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db_session() as session:
        # Get sessions with multiple events to calculate duration
        # Using subquery to get min/max timestamps per session
        subquery = (
            select(
                AnalyticsEvent.session_id,
                func.min(AnalyticsEvent.timestamp).label('min_ts'),
                func.max(AnalyticsEvent.timestamp).label('max_ts'),
                func.count().label('event_count')
            )
            .where(and_(
                AnalyticsEvent.timestamp >= cutoff,
                AnalyticsEvent.session_id.isnot(None)
            ))
            .group_by(AnalyticsEvent.session_id)
            .having(func.count() > 1)
            .subquery()
        )

        # Calculate average duration in minutes
        # Duration = (max_ts - min_ts) in minutes
        result = session.execute(
            select(func.avg(
                extract('epoch', subquery.c.max_ts - subquery.c.min_ts) / 60
            ))
        ).scalar()

        avg_minutes = result if result else 0

    # Format as MM:SS
    minutes = int(avg_minutes)
    seconds = int((avg_minutes - minutes) * 60)

    return {
        "formatted": f"{minutes}:{seconds:02d}",
        "minutes": avg_minutes,
        "change": 0
    }


def get_cta_clicks(days: int = 7) -> dict:
    """Get CTA button clicks"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    prev_cutoff = datetime.utcnow() - timedelta(days=days * 2)

    with db_session() as session:
        # Current period
        current = session.execute(
            select(func.count())
            .select_from(AnalyticsEvent)
            .where(and_(
                AnalyticsEvent.timestamp >= cutoff,
                AnalyticsEvent.event_type == 'cta_click'
            ))
        ).scalar() or 0

        # Previous period
        previous = session.execute(
            select(func.count())
            .select_from(AnalyticsEvent)
            .where(and_(
                AnalyticsEvent.timestamp >= prev_cutoff,
                AnalyticsEvent.timestamp < cutoff,
                AnalyticsEvent.event_type == 'cta_click'
            ))
        ).scalar() or 0

    # Calculate change
    if previous > 0:
        change = round(((current - previous) / previous) * 100, 1)
    else:
        change = 100 if current > 0 else 0

    return {"count": current, "change": change}


def get_traffic_by_day(days: int = 7) -> dict:
    """Get traffic data grouped by day for charts"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db_session() as session:
        # Group by date (using func.date for cross-db compatibility)
        results = session.execute(
            select(
                func.date(PageView.timestamp).label('date'),
                func.count().label('views'),
                func.count(distinct(PageView.ip_hash)).label('visitors')
            )
            .where(PageView.timestamp >= cutoff)
            .group_by(func.date(PageView.timestamp))
            .order_by(func.date(PageView.timestamp))
        ).all()

    # Build daily data map
    data_map = {str(row.date): {"views": row.views, "visitors": row.visitors} for row in results}

    # Fill in all days
    labels = []
    visitors_data = []
    views_data = []

    day_names_uk = {
        "Mon": "Пн", "Tue": "Вт", "Wed": "Ср",
        "Thu": "Чт", "Fri": "Пт", "Sat": "Сб", "Sun": "Нд"
    }

    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - 1 - i)
        date_str = date.strftime("%Y-%m-%d")
        day_name = date.strftime("%a")

        labels.append(day_names_uk.get(day_name, day_name))

        if date_str in data_map:
            visitors_data.append(data_map[date_str]["visitors"])
            views_data.append(data_map[date_str]["views"])
        else:
            visitors_data.append(0)
            views_data.append(0)

    return {
        "labels": labels,
        "visitors": visitors_data,
        "views": views_data
    }


def get_traffic_sources(days: int = 7) -> list:
    """Get traffic sources breakdown"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db_session() as session:
        results = session.execute(
            select(
                PageView.referrer,
                func.count().label('count')
            )
            .where(PageView.timestamp >= cutoff)
            .group_by(PageView.referrer)
            .order_by(func.count().desc())
        ).all()

    total = sum(row.count for row in results) if results else 1

    sources = []
    for row in results:
        sources.append({
            "name": row.referrer or "Direct",
            "count": row.count,
            "percentage": round((row.count / total) * 100, 1)
        })

    return sources


def get_popular_pages(limit: int = 10, days: int = 7) -> list:
    """Get most popular pages"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db_session() as session:
        results = session.execute(
            select(
                PageView.path,
                func.count().label('views'),
                func.count(distinct(PageView.ip_hash)).label('visitors')
            )
            .where(PageView.timestamp >= cutoff)
            .group_by(PageView.path)
            .order_by(func.count().desc())
            .limit(limit)
        ).all()

    # Page name mapping
    page_names = {
        "/": "Головна",
        "/services": "Послуги",
        "/pricing": "Тарифи",
        "/about": "Про нас",
        "/blog": "Блог",
        "/contact": "Контакти",
        "/partners": "Партнери",
        "/faq": "FAQ"
    }

    pages = []
    for row in results:
        path = row.path
        name = page_names.get(path)
        if not name:
            if path.startswith("/blog/"):
                name = "Стаття блогу"
            else:
                name = path.strip("/").title() if path != "/" else "Головна"

        pages.append({
            "path": path,
            "name": name,
            "views": row.views,
            "visitors": row.visitors
        })

    return pages


def get_device_stats(days: int = 7) -> list:
    """Get device breakdown"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db_session() as session:
        results = session.execute(
            select(
                PageView.device,
                func.count().label('count')
            )
            .where(PageView.timestamp >= cutoff)
            .group_by(PageView.device)
            .order_by(func.count().desc())
        ).all()

    total = sum(row.count for row in results) if results else 1

    devices = []
    for row in results:
        devices.append({
            "name": row.device or "Unknown",
            "count": row.count,
            "percentage": round((row.count / total) * 100, 1)
        })

    return devices


def get_browser_stats(days: int = 7) -> list:
    """Get browser breakdown"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db_session() as session:
        results = session.execute(
            select(
                PageView.browser,
                func.count().label('count')
            )
            .where(PageView.timestamp >= cutoff)
            .group_by(PageView.browser)
            .order_by(func.count().desc())
        ).all()

    total = sum(row.count for row in results) if results else 1

    browsers = []
    for row in results:
        browsers.append({
            "name": row.browser or "Unknown",
            "count": row.count,
            "percentage": round((row.count / total) * 100, 1)
        })

    return browsers


def get_recent_events(limit: int = 10) -> list:
    """Get recent events for activity feed"""
    with db_session() as session:
        results = session.execute(
            select(AnalyticsEvent)
            .order_by(AnalyticsEvent.timestamp.desc())
            .limit(limit)
        ).scalars().all()

    events = []
    for event in results:
        events.append({
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "type": event.event_type,
            "data": event.event_data,
            "path": event.path
        })

    return events


def get_form_submissions(days: int = 30, limit: int = 10) -> list:
    """Get recent form submissions"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db_session() as session:
        results = session.execute(
            select(FormSubmission)
            .where(FormSubmission.timestamp >= cutoff)
            .order_by(FormSubmission.timestamp.desc())
            .limit(limit)
        ).scalars().all()

    submissions = []
    for sub in results:
        submissions.append({
            "timestamp": sub.timestamp.isoformat() if sub.timestamp else None,
            "form_type": sub.form_type,
            "company": sub.company,
            "request_type": sub.request_type
        })

    return submissions


def get_dashboard_summary(days: int = 7) -> dict:
    """Get all dashboard data in one call"""
    return {
        "visitors": get_visitors_count(days),
        "page_views": get_page_views(days),
        "avg_time": get_avg_session_time(days),
        "cta_clicks": get_cta_clicks(days),
        "traffic_by_day": get_traffic_by_day(days),
        "sources": get_traffic_sources(days),
        "popular_pages": get_popular_pages(5, days),
        "devices": get_device_stats(days),
        "browsers": get_browser_stats(days),
        "recent_events": get_recent_events(5),
        "form_submissions": get_form_submissions(30, 5)
    }
