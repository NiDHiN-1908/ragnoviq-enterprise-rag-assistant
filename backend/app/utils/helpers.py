"""
Utility functions for the application.
Includes helpers for logging, caching, and request handling.
"""

import hashlib
import uuid
import logging
from typing import Any, Callable
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def generate_request_id() -> str:
    """Generate a request ID for tracking."""
    return f"req_{uuid.uuid4().hex[:12]}"


def hash_string(value: str) -> str:
    """Hash a string value."""
    return hashlib.sha256(value.encode()).hexdigest()


def sanitize_url(url: str) -> str:
    """Sanitize URL for logging."""
    return url.replace("?", " [QUERY] ").split("&")[0]


def get_timestamp() -> str:
    """Get current timestamp as ISO string."""
    return datetime.utcnow().isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text for logging."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.utcnow()
        try:
            result = func(*args, **kwargs)
            elapsed = (datetime.utcnow() - start).total_seconds()
            logger.info(f"{func.__name__} executed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = (datetime.utcnow() - start).total_seconds()
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}")
            raise
    return wrapper


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """Safely get value from dictionary."""
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default
