"""
Logging configuration for Trexim
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

try:
    from .config import settings
except ImportError:
    from config import settings

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "trexim") -> logging.Logger:
    """
    Setup and return a configured logger.

    Usage:
        from app.logger import logger
        logger.info("Something happened")
        logger.error("An error occurred", exc_info=True)
    """
    logger = logging.getLogger(name)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Set level based on environment
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Console handler (always)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    logger.addHandler(console_handler)

    # File handler (production or if logs dir exists)
    if not settings.DEBUG or LOG_DIR.exists():
        # Main log file
        log_file = LOG_DIR / f"trexim_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        # Error log file (separate)
        error_file = LOG_DIR / "errors.log"
        error_handler = logging.FileHandler(error_file, encoding="utf-8")
        error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)

    return logger


# Default logger instance
logger = setup_logger()


# Convenience functions
def log_request(method: str, path: str, status: int, duration_ms: float = None):
    """Log HTTP request"""
    duration_str = f" ({duration_ms:.0f}ms)" if duration_ms else ""
    logger.info(f"{method} {path} -> {status}{duration_str}")


def log_error(message: str, exc_info: bool = True):
    """Log error with optional exception info"""
    logger.error(message, exc_info=exc_info)


def log_auth(action: str, username: str, success: bool, ip: str = None):
    """Log authentication events"""
    status = "SUCCESS" if success else "FAILED"
    ip_str = f" from {ip}" if ip else ""
    logger.info(f"AUTH {action}: {username} - {status}{ip_str}")


def log_admin_action(action: str, username: str, details: str = None):
    """Log admin panel actions"""
    details_str = f" - {details}" if details else ""
    logger.info(f"ADMIN [{username}]: {action}{details_str}")


def get_log_files() -> list[dict]:
    """Get list of available log files"""
    if not LOG_DIR.exists():
        return []

    files = []
    for f in sorted(LOG_DIR.glob("*.log"), reverse=True):
        files.append({
            "name": f.name,
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    return files


def read_log_file(filename: str, lines: int = 200, level: str = None) -> list[str]:
    """
    Read last N lines from a log file.
    Optionally filter by log level.
    """
    log_file = LOG_DIR / filename

    # Security: prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return []

    if not log_file.exists() or not log_file.is_file():
        return []

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        # Filter by level if specified
        if level:
            level = level.upper()
            all_lines = [line for line in all_lines if f"| {level}" in line]

        # Return last N lines
        return all_lines[-lines:]
    except Exception:
        return []
