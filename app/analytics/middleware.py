"""
Analytics middleware for server-side tracking
"""
import hashlib
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .models import log_page_view

# Salt for IP hashing (privacy)
IP_SALT = "trexim-analytics-2026"

# Paths to exclude from tracking
EXCLUDED_PATHS = (
    "/static",
    "/admin",
    "/api",
    "/favicon",
    "/robots.txt",
    "/sitemap",
    "/_",
)

# Excluded file extensions
EXCLUDED_EXTENSIONS = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".woff", ".woff2")


def hash_ip(ip: str) -> str:
    """Hash IP address for privacy"""
    return hashlib.sha256(f"{ip}{IP_SALT}".encode()).hexdigest()[:16]


def parse_user_agent(ua: str) -> dict:
    """Parse user agent string to extract browser, device, and OS"""
    result = {
        "browser": "Unknown",
        "device": "Desktop",
        "os": "Unknown"
    }

    if not ua:
        return result

    ua_lower = ua.lower()

    # Detect device
    if "mobile" in ua_lower or "android" in ua_lower and "mobile" in ua_lower:
        result["device"] = "Mobile"
    elif "tablet" in ua_lower or "ipad" in ua_lower:
        result["device"] = "Tablet"
    elif "bot" in ua_lower or "crawler" in ua_lower or "spider" in ua_lower:
        result["device"] = "Bot"

    # Detect browser
    if "firefox" in ua_lower:
        result["browser"] = "Firefox"
    elif "edg" in ua_lower:
        result["browser"] = "Edge"
    elif "chrome" in ua_lower:
        result["browser"] = "Chrome"
    elif "safari" in ua_lower:
        result["browser"] = "Safari"
    elif "opera" in ua_lower or "opr" in ua_lower:
        result["browser"] = "Opera"

    # Detect OS
    if "windows" in ua_lower:
        result["os"] = "Windows"
    elif "mac os" in ua_lower or "macintosh" in ua_lower:
        result["os"] = "macOS"
    elif "linux" in ua_lower:
        result["os"] = "Linux"
    elif "android" in ua_lower:
        result["os"] = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        result["os"] = "iOS"

    return result


def parse_referrer(referrer: str) -> str:
    """Categorize referrer source"""
    if not referrer:
        return "Direct"

    referrer_lower = referrer.lower()

    if "google" in referrer_lower:
        return "Google"
    elif "facebook" in referrer_lower or "fb.com" in referrer_lower:
        return "Facebook"
    elif "instagram" in referrer_lower:
        return "Instagram"
    elif "linkedin" in referrer_lower:
        return "LinkedIn"
    elif "telegram" in referrer_lower or "t.me" in referrer_lower:
        return "Telegram"
    elif "twitter" in referrer_lower or "x.com" in referrer_lower:
        return "Twitter/X"
    elif "youtube" in referrer_lower:
        return "YouTube"
    elif "bing" in referrer_lower:
        return "Bing"
    elif "yahoo" in referrer_lower:
        return "Yahoo"
    elif "duckduckgo" in referrer_lower:
        return "DuckDuckGo"
    elif "trexim" in referrer_lower:
        return "Internal"

    return "Other"


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to track page views server-side"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip excluded paths
        should_track = (
            not path.startswith(EXCLUDED_PATHS) and
            not path.endswith(EXCLUDED_EXTENSIONS) and
            request.method == "GET"
        )

        # Process response first
        response = await call_next(request)

        # Track only successful page loads
        if should_track and response.status_code == 200:
            try:
                # Get client IP
                client_ip = request.client.host if request.client else "unknown"

                # Check for forwarded IP (if behind proxy)
                forwarded = request.headers.get("x-forwarded-for")
                if forwarded:
                    client_ip = forwarded.split(",")[0].strip()

                ip_hash = hash_ip(client_ip)

                # Get user agent
                user_agent = request.headers.get("user-agent", "")
                ua_info = parse_user_agent(user_agent)

                # Skip bots
                if ua_info["device"] == "Bot":
                    return response

                # Get referrer
                referrer = request.headers.get("referer", "")
                referrer_source = parse_referrer(referrer)

                # Log page view
                log_page_view(
                    path=path,
                    ip_hash=ip_hash,
                    user_agent=user_agent,
                    referrer=referrer_source,
                    browser=ua_info["browser"],
                    device=ua_info["device"],
                    os=ua_info["os"]
                )
            except Exception as e:
                # Don't let analytics errors break the app
                print(f"Analytics error: {e}")

        return response
