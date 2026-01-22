"""
Analytics service - query functions for dashboard
"""
from datetime import datetime, timedelta
from typing import Optional
from .models import get_connection


def get_visitors_count(days: int = 7) -> dict:
    """Get unique visitors count and change percentage"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    prev_cutoff = (datetime.utcnow() - timedelta(days=days * 2)).isoformat()

    # Current period
    cursor.execute("""
        SELECT COUNT(DISTINCT ip_hash) as count
        FROM page_views
        WHERE timestamp >= ?
    """, (cutoff,))
    current = cursor.fetchone()["count"]

    # Previous period
    cursor.execute("""
        SELECT COUNT(DISTINCT ip_hash) as count
        FROM page_views
        WHERE timestamp >= ? AND timestamp < ?
    """, (prev_cutoff, cutoff))
    previous = cursor.fetchone()["count"]

    conn.close()

    # Calculate change
    if previous > 0:
        change = round(((current - previous) / previous) * 100, 1)
    else:
        change = 100 if current > 0 else 0

    return {"count": current, "change": change}


def get_page_views(days: int = 7) -> dict:
    """Get total page views and change percentage"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    prev_cutoff = (datetime.utcnow() - timedelta(days=days * 2)).isoformat()

    # Current period
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM page_views
        WHERE timestamp >= ?
    """, (cutoff,))
    current = cursor.fetchone()["count"]

    # Previous period
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM page_views
        WHERE timestamp >= ? AND timestamp < ?
    """, (prev_cutoff, cutoff))
    previous = cursor.fetchone()["count"]

    conn.close()

    # Calculate change
    if previous > 0:
        change = round(((current - previous) / previous) * 100, 1)
    else:
        change = 100 if current > 0 else 0

    return {"count": current, "change": change}


def get_avg_session_time(days: int = 7) -> dict:
    """Get average session time (from events if available)"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    # Get sessions with heartbeat events - use subquery for proper aggregation
    cursor.execute("""
        SELECT AVG(duration_minutes) as avg_minutes
        FROM (
            SELECT
                session_id,
                (julianday(MAX(timestamp)) - julianday(MIN(timestamp))) * 24 * 60 as duration_minutes
            FROM events
            WHERE timestamp >= ? AND session_id IS NOT NULL
            GROUP BY session_id
            HAVING COUNT(*) > 1
        )
    """, (cutoff,))

    result = cursor.fetchone()
    avg_minutes = result["avg_minutes"] if result and result["avg_minutes"] else 0
    conn.close()

    # Format as MM:SS
    minutes = int(avg_minutes)
    seconds = int((avg_minutes - minutes) * 60)

    return {
        "formatted": f"{minutes}:{seconds:02d}",
        "minutes": avg_minutes,
        "change": 0  # Would need historical data to calculate
    }


def get_cta_clicks(days: int = 7) -> dict:
    """Get CTA button clicks"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    prev_cutoff = (datetime.utcnow() - timedelta(days=days * 2)).isoformat()

    # Current period
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM events
        WHERE timestamp >= ? AND event_type = 'cta_click'
    """, (cutoff,))
    current = cursor.fetchone()["count"]

    # Previous period
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM events
        WHERE timestamp >= ? AND timestamp < ? AND event_type = 'cta_click'
    """, (prev_cutoff, cutoff))
    previous = cursor.fetchone()["count"]

    conn.close()

    # Calculate change
    if previous > 0:
        change = round(((current - previous) / previous) * 100, 1)
    else:
        change = 100 if current > 0 else 0

    return {"count": current, "change": change}


def get_traffic_by_day(days: int = 7) -> dict:
    """Get traffic data grouped by day for charts"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    # Page views by day
    cursor.execute("""
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as views,
            COUNT(DISTINCT ip_hash) as visitors
        FROM page_views
        WHERE timestamp >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    """, (cutoff,))

    rows = cursor.fetchall()
    conn.close()

    # Build daily data
    labels = []
    visitors_data = []
    views_data = []

    # Create a map for existing data
    data_map = {row["date"]: {"views": row["views"], "visitors": row["visitors"]} for row in rows}

    # Fill in all days
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        day_name = (datetime.utcnow() - timedelta(days=days - 1 - i)).strftime("%a")

        # Ukrainian day names
        day_names_uk = {
            "Mon": "Пн", "Tue": "Вт", "Wed": "Ср",
            "Thu": "Чт", "Fri": "Пт", "Sat": "Сб", "Sun": "Нд"
        }
        labels.append(day_names_uk.get(day_name, day_name))

        if date in data_map:
            visitors_data.append(data_map[date]["visitors"])
            views_data.append(data_map[date]["views"])
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
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT
            referrer,
            COUNT(*) as count
        FROM page_views
        WHERE timestamp >= ?
        GROUP BY referrer
        ORDER BY count DESC
    """, (cutoff,))

    rows = cursor.fetchall()
    total = sum(row["count"] for row in rows) if rows else 1

    conn.close()

    sources = []
    for row in rows:
        sources.append({
            "name": row["referrer"] or "Direct",
            "count": row["count"],
            "percentage": round((row["count"] / total) * 100, 1)
        })

    return sources


def get_popular_pages(limit: int = 10, days: int = 7) -> list:
    """Get most popular pages"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT
            path,
            COUNT(*) as views,
            COUNT(DISTINCT ip_hash) as visitors
        FROM page_views
        WHERE timestamp >= ?
        GROUP BY path
        ORDER BY views DESC
        LIMIT ?
    """, (cutoff, limit))

    rows = cursor.fetchall()
    conn.close()

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
    for row in rows:
        path = row["path"]
        name = page_names.get(path)
        if not name:
            if path.startswith("/blog/"):
                name = "Стаття блогу"
            else:
                name = path.strip("/").title() if path != "/" else "Головна"

        pages.append({
            "path": path,
            "name": name,
            "views": row["views"],
            "visitors": row["visitors"]
        })

    return pages


def get_device_stats(days: int = 7) -> list:
    """Get device breakdown"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT
            device,
            COUNT(*) as count
        FROM page_views
        WHERE timestamp >= ?
        GROUP BY device
        ORDER BY count DESC
    """, (cutoff,))

    rows = cursor.fetchall()
    total = sum(row["count"] for row in rows) if rows else 1

    conn.close()

    devices = []
    for row in rows:
        devices.append({
            "name": row["device"] or "Unknown",
            "count": row["count"],
            "percentage": round((row["count"] / total) * 100, 1)
        })

    return devices


def get_browser_stats(days: int = 7) -> list:
    """Get browser breakdown"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT
            browser,
            COUNT(*) as count
        FROM page_views
        WHERE timestamp >= ?
        GROUP BY browser
        ORDER BY count DESC
    """, (cutoff,))

    rows = cursor.fetchall()
    total = sum(row["count"] for row in rows) if rows else 1

    conn.close()

    browsers = []
    for row in rows:
        browsers.append({
            "name": row["browser"] or "Unknown",
            "count": row["count"],
            "percentage": round((row["count"] / total) * 100, 1)
        })

    return browsers


def get_recent_events(limit: int = 10) -> list:
    """Get recent events for activity feed"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            timestamp,
            event_type,
            event_data,
            path
        FROM events
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "timestamp": row["timestamp"],
            "type": row["event_type"],
            "data": row["event_data"],
            "path": row["path"]
        })

    return events


def get_form_submissions(days: int = 30, limit: int = 10) -> list:
    """Get recent form submissions"""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT *
        FROM form_submissions
        WHERE timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (cutoff, limit))

    rows = cursor.fetchall()
    conn.close()

    submissions = []
    for row in rows:
        submissions.append({
            "timestamp": row["timestamp"],
            "form_type": row["form_type"],
            "company": row["company"],
            "request_type": row["request_type"]
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
