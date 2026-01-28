"""
Analytics database operations using SQLAlchemy
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from ..database.connection import db_session
from ..database.models import PageView, FormSubmission, AnalyticsSession, AnalyticsEvent


def log_page_view(path: str, ip_hash: str, user_agent: str = None,
                  referrer: str = None, browser: str = None,
                  device: str = None, os: str = None, country: str = None):
    """Log a page view"""
    try:
        with db_session() as session:
            page_view = PageView(
                timestamp=datetime.utcnow(),
                path=path,
                ip_hash=ip_hash,
                user_agent=user_agent,
                referrer=referrer,
                browser=browser,
                device=device,
                os=os,
                country=country
            )
            session.add(page_view)
    except Exception as e:
        print(f"Error logging page view: {e}")


def create_session(session_id: str, ip_hash: str, user_agent: str = None, consent: bool = False):
    """Create a new analytics session"""
    try:
        with db_session() as session:
            # Check if session exists
            existing = session.execute(
                select(AnalyticsSession).where(AnalyticsSession.id == session_id)
            ).scalar_one_or_none()

            if existing:
                # Update existing session
                existing.ip_hash = ip_hash
                existing.user_agent = user_agent
                existing.consent_given = consent
            else:
                # Create new session
                analytics_session = AnalyticsSession(
                    id=session_id,
                    started_at=datetime.utcnow(),
                    ip_hash=ip_hash,
                    user_agent=user_agent,
                    consent_given=consent
                )
                session.add(analytics_session)
    except Exception as e:
        print(f"Error creating session: {e}")


def update_session(session_id: str, pages_visited: int = None, ended_at: datetime = None):
    """Update session data"""
    try:
        with db_session() as session:
            analytics_session = session.execute(
                select(AnalyticsSession).where(AnalyticsSession.id == session_id)
            ).scalar_one_or_none()

            if analytics_session:
                if pages_visited is not None:
                    analytics_session.pages_visited = pages_visited
                if ended_at is not None:
                    analytics_session.ended_at = ended_at
    except Exception as e:
        print(f"Error updating session: {e}")


def log_event(event_type: str, event_data: str = None, session_id: str = None, path: str = None):
    """Log an analytics event (click, scroll, etc.)"""
    try:
        with db_session() as session:
            event = AnalyticsEvent(
                timestamp=datetime.utcnow(),
                session_id=session_id,
                event_type=event_type,
                event_data=event_data,
                path=path
            )
            session.add(event)
    except Exception as e:
        print(f"Error logging event: {e}")


def log_form_submission(form_type: str, company: str = None, email: str = None,
                        request_type: str = None, ip_hash: str = None):
    """Log a form submission"""
    try:
        with db_session() as session:
            submission = FormSubmission(
                timestamp=datetime.utcnow(),
                form_type=form_type,
                company=company,
                email=email,
                request_type=request_type,
                ip_hash=ip_hash,
                status='new'
            )
            session.add(submission)
    except Exception as e:
        print(f"Error logging form submission: {e}")


def get_connection():
    """
    Deprecated: Use db_session() context manager instead.
    Kept for backward compatibility during migration.
    """
    raise DeprecationWarning(
        "get_connection() is deprecated. Use db_session() from database.connection instead."
    )


def init_db():
    """
    Deprecated: Database initialization is handled by Alembic migrations.
    """
    pass
