from __future__ import annotations

import os
import logging
from typing import Any, Callable, TypeVar

# Thiết lập logger để theo dõi trạng thái tracing
logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

try:
    # Langfuse v4.x primary import path.
    from langfuse import get_client, observe
    _HAS_LANGFUSE = True
except ImportError:
    _HAS_LANGFUSE = False
    get_client = None

    # Mock decorator nếu không có thư viện
    def observe(*args: Any, **kwargs: Any):
        def decorator(func: F) -> F:
            return func
        return decorator

class _LangfuseContextAdapter:
    def __init__(self) -> None:
        self._client = get_client() if callable(get_client) else None

    def update_current_trace(self, **kwargs: Any) -> None:
        if self._client and hasattr(self._client, "update_current_trace"):
            self._client.update_current_trace(**kwargs)

    def update_current_observation(self, **kwargs: Any) -> None:
        if self._client and hasattr(self._client, "update_current_observation"):
            self._client.update_current_observation(**kwargs)
            return
        if self._client and hasattr(self._client, "update_current_generation"):
            self._client.update_current_generation(**kwargs)

    def flush(self) -> None:
        if self._client and hasattr(self._client, "flush"):
            self._client.flush()


langfuse_context = _LangfuseContextAdapter()

def tracing_enabled() -> bool:
    """Kiểm tra xem Langfuse có được cấu hình đầy đủ hay không."""
    has_keys = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
    if not _HAS_LANGFUSE and has_keys:
        logger.warning("Langfuse keys found but 'langfuse' library is not installed.")
    return _HAS_LANGFUSE and has_keys