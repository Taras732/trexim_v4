"""
SQLAlchemy models for Trexim
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Table, JSON, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# Many-to-many relationship table for posts and tags
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('blog_posts.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('blog_tags.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """Admin users"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(20), default='admin')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class BlogCategory(Base):
    """Blog categories"""
    __tablename__ = 'blog_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_uk = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    posts = relationship("BlogPost", back_populates="category")

    def __repr__(self):
        return f"<BlogCategory(code='{self.code}')>"


class BlogTag(Base):
    """Blog tags"""
    __tablename__ = 'blog_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_uk = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    posts = relationship("BlogPost", secondary=post_tags, back_populates="tags")

    def __repr__(self):
        return f"<BlogTag(code='{self.code}')>"


class BlogPost(Base):
    """Blog posts with bilingual content"""
    __tablename__ = 'blog_posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)

    # Ukrainian content
    title_uk = Column(String(255), nullable=False)
    excerpt_uk = Column(Text, nullable=True)
    content_uk = Column(Text, nullable=True)
    date_uk = Column(String(50), nullable=True)

    # English content
    title_en = Column(String(255), nullable=False)
    excerpt_en = Column(Text, nullable=True)
    content_en = Column(Text, nullable=True)
    date_en = Column(String(50), nullable=True)

    # Common fields
    category_id = Column(Integer, ForeignKey('blog_categories.id'), nullable=True)
    emoji = Column(String(10), nullable=True)
    color = Column(String(20), default='orange')
    read_time = Column(Integer, default=5)
    image_url = Column(String(500), nullable=True)

    # Status
    status = Column(String(20), default='draft')  # draft, scheduled, published
    published_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationships
    category = relationship("BlogCategory", back_populates="posts")
    tags = relationship("BlogTag", secondary=post_tags, back_populates="posts")
    author = relationship("User")

    # Indexes
    __table_args__ = (
        Index('idx_posts_status', 'status'),
        Index('idx_posts_published_at', 'published_at'),
    )

    def __repr__(self):
        return f"<BlogPost(slug='{self.slug}', status='{self.status}')>"


class PageView(Base):
    """Analytics - page views"""
    __tablename__ = 'page_views'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    path = Column(String(500), nullable=False, index=True)
    ip_hash = Column(String(64), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    browser = Column(String(50), nullable=True)
    device = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    country = Column(String(2), nullable=True)

    def __repr__(self):
        return f"<PageView(path='{self.path}', timestamp='{self.timestamp}')>"


class FormSubmission(Base):
    """Form submissions tracking"""
    __tablename__ = 'form_submissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    form_type = Column(String(50), nullable=False)
    company = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    message = Column(Text, nullable=True)
    request_type = Column(String(50), nullable=True)
    ip_hash = Column(String(64), nullable=True)
    status = Column(String(20), default='new')  # new, processed, spam

    def __repr__(self):
        return f"<FormSubmission(form_type='{self.form_type}', status='{self.status}')>"


class Setting(Base):
    """Application settings stored in database"""
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(String(20), default='string')  # string, int, bool, json
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Setting(key='{self.key}')>"


class AnalyticsSession(Base):
    """Analytics - user sessions"""
    __tablename__ = 'analytics_sessions'

    id = Column(String(64), primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)
    ip_hash = Column(String(64), nullable=False, index=True)
    pages_visited = Column(Integer, default=1)
    consent_given = Column(Boolean, default=False)
    user_agent = Column(Text, nullable=True)

    # Relationships
    events = relationship("AnalyticsEvent", back_populates="session")

    def __repr__(self):
        return f"<AnalyticsSession(id='{self.id}')>"


class AnalyticsEvent(Base):
    """Analytics - events (clicks, scroll, etc.)"""
    __tablename__ = 'analytics_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    session_id = Column(String(64), ForeignKey('analytics_sessions.id'), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(Text, nullable=True)
    path = Column(String(500), nullable=True)

    # Relationships
    session = relationship("AnalyticsSession", back_populates="events")

    def __repr__(self):
        return f"<AnalyticsEvent(type='{self.event_type}')>"
