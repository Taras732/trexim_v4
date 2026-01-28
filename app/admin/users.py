"""
User management with secure password hashing - SQLAlchemy version
"""
import bcrypt
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from ..database.connection import db_session, SessionLocal
from ..database.models import User


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False


def create_user(username: str, password: str, email: str = None, role: str = "admin") -> Optional[int]:
    """Create a new user with hashed password"""
    try:
        with db_session() as session:
            # Check if user already exists
            existing = session.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

            if existing:
                return None

            user = User(
                username=username,
                password_hash=hash_password(password),
                email=email,
                role=role,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            session.flush()
            return user.id
    except Exception:
        return None


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    with db_session() as session:
        user = session.execute(
            select(User).where(User.username == username, User.is_active == True)
        ).scalar_one_or_none()

        if user:
            return {
                "id": user.id,
                "username": user.username,
                "password_hash": user.password_hash,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        return None


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user by username and password"""
    user = get_user_by_username(username)
    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    # Update last login
    with db_session() as session:
        db_user = session.execute(
            select(User).where(User.id == user["id"])
        ).scalar_one_or_none()

        if db_user:
            db_user.last_login = datetime.utcnow()

    return user


def update_password(username: str, new_password: str) -> bool:
    """Update user password"""
    try:
        with db_session() as session:
            user = session.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

            if user:
                user.password_hash = hash_password(new_password)
                user.updated_at = datetime.utcnow()
                return True
            return False
    except Exception:
        return False


def get_all_users() -> list:
    """Get all users (without password hashes)"""
    with db_session() as session:
        users = session.execute(
            select(User).order_by(User.created_at.desc())
        ).scalars().all()

        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ]


def user_exists() -> bool:
    """Check if any user exists in the database"""
    with db_session() as session:
        count = session.execute(
            select(func.count()).select_from(User)
        ).scalar()
        return count > 0


def delete_user(username: str) -> bool:
    """Delete user (soft delete - set is_active = False)"""
    try:
        with db_session() as session:
            user = session.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

            if user:
                user.is_active = False
                return True
            return False
    except Exception:
        return False
