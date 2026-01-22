"""
Admin authentication
"""
from fastapi import Request, HTTPException


def check_auth(request: Request) -> bool:
    """
    Check if user is authenticated.
    Raises HTTPException 401 if not.
    """
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return True
