"""
Admin authentication with secure password verification
"""
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

try:
    from .users import authenticate_user, user_exists, create_user, get_user_by_username
    from ..config import settings
    from ..logger import log_auth, logger
except ImportError:
    from users import authenticate_user, user_exists, create_user, get_user_by_username
    from config import settings
    from logger import log_auth, logger


def check_auth(request: Request) -> bool:
    """
    Check if user is authenticated.
    Raises HTTPException 401 if not.
    """
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return True


def login_user(request: Request, username: str, password: str) -> tuple[bool, str]:
    """
    Attempt to log in a user.
    Returns (success, error_message)
    """
    # Get client IP for logging
    client_ip = request.client.host if request.client else "unknown"

    # Check if any users exist
    if not user_exists():
        # No users - check if this matches init credentials
        init_username = settings.ADMIN_INIT_USERNAME
        init_password = settings.ADMIN_INIT_PASSWORD

        if not init_password:
            log_auth("LOGIN", username, False, client_ip)
            return False, "Система не налаштована. Встановіть ADMIN_INIT_PASSWORD в .env"

        if username == init_username and password == init_password:
            # Create the first admin user
            user_id = create_user(username, password, role="admin")
            if user_id:
                request.session["authenticated"] = True
                request.session["user_id"] = user_id
                request.session["username"] = username
                logger.info(f"First admin user '{username}' created")
                log_auth("LOGIN", username, True, client_ip)
                return True, ""
            log_auth("LOGIN", username, False, client_ip)
            return False, "Помилка створення користувача"

        log_auth("LOGIN", username, False, client_ip)
        return False, "Невірний логін або пароль"

    # Normal authentication
    user = authenticate_user(username, password)
    if user:
        request.session["authenticated"] = True
        request.session["user_id"] = user["id"]
        request.session["username"] = user["username"]
        log_auth("LOGIN", username, True, client_ip)
        return True, ""

    log_auth("LOGIN", username, False, client_ip)
    return False, "Невірний логін або пароль"


def logout_user(request: Request):
    """Log out current user"""
    username = request.session.get("username", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    log_auth("LOGOUT", username, True, client_ip)
    request.session.clear()


def get_current_user(request: Request) -> dict | None:
    """Get current logged in user info"""
    if not request.session.get("authenticated"):
        return None

    username = request.session.get("username")
    if username:
        return get_user_by_username(username)
    return None


def needs_setup() -> bool:
    """Check if initial setup is needed (no users exist)"""
    return not user_exists()
