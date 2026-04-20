from __future__ import annotations

import os
import logging
from functools import lru_cache
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

try:
    # Langfuse v4.x primary import path.
    from langfuse import get_client, observe
    _HAS_LANGFUSE = True
except ImportError:
    _HAS_LANGFUSE = False
    get_client = None

    def observe(*args: Any, **kwargs: Any):
        def decorator(func: F) -> F:
            return func
        return decorator


@lru_cache(maxsize=1)
def _get_langfuse_client() -> Any:
    if callable(get_client):
        return get_client()
    return None


class _LangfuseContextAdapter:
    """Compatibility adapter with small automation helpers for Langfuse v4.x."""

    @property
    def _client(self) -> Any:
        return _get_langfuse_client()

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

    def auto_trace(
        self,
        *,
        user_id_hash: str,
        session_id: str,
        feature: str,
        model: str,
        env: str,
        extra_metadata: dict[str, Any] | None = None,
    ) -> None:
        """Automation helper: attach standard trace attributes in one call."""
        metadata: dict[str, Any] = {"feature_type": feature, "model": model, "env": env}
        if extra_metadata:
            metadata.update(extra_metadata)
        self.update_current_trace(
            user_id=user_id_hash,
            session_id=session_id,
            tags=["lab", feature, model, env],
            metadata=metadata,
        )

    def auto_observation(
        self,
        *,
        query_preview: str,
        answer_preview: str | None,
        doc_count: int | None,
        quality_score: float | None,
        tokens_in: int | None,
        tokens_out: int | None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> None:
        """Automation helper: normalize observation payload across endpoints."""
        metadata: dict[str, Any] = {"query_preview": query_preview}
        if doc_count is not None:
            metadata["doc_count"] = doc_count
        if quality_score is not None:
            metadata["quality_score"] = quality_score
        if extra_metadata:
            metadata.update(extra_metadata)

        payload: dict[str, Any] = {
            "input": query_preview,
            "metadata": metadata,
        }
        if answer_preview is not None:
            payload["output"] = answer_preview
        if tokens_in is not None and tokens_out is not None:
            payload["usage_details"] = {"input": tokens_in, "output": tokens_out}
        self.update_current_observation(**payload)


langfuse_context = _LangfuseContextAdapter()


def tracing_enabled() -> bool:
    has_keys = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
    if not _HAS_LANGFUSE and has_keys:
        logger.warning("Langfuse keys found but 'langfuse' library is not installed.")
    return _HAS_LANGFUSE and has_keys


def flush_tracing() -> None:
    """Manual flush for short-lived scripts to avoid losing buffered traces."""
    langfuse_context.flush()