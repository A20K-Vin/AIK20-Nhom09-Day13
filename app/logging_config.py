from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars

from .pii import scrub_text

LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))


class JsonlFileProcessor:
    def __call__(self, logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        rendered = structlog.processors.JSONRenderer()(logger, method_name, event_dict)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(rendered + "\n")
        return event_dict



def scrub_event(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    payload = event_dict.get("payload")
    if isinstance(payload, dict):
        event_dict["payload"] = {
            k: scrub_text(v) if isinstance(v, str) else v for k, v in payload.items()
        }
    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_dict["event"] = scrub_text(event_dict["event"])
    return event_dict



def configure_logging() -> None:
    # Thiết lập cơ bản cho thư viện logging tiêu chuẩn của Python
    logging.basicConfig(
        format="%(message)s", 
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
    )

    structlog.configure(
        processors=[
            # 1. Hợp nhất các biến ngữ cảnh (context variables)
            merge_contextvars,
            
            # 2. Thêm level (info, error,...) vào event dict
            structlog.processors.add_log_level,
            
            # 3. Thêm timestamp chuẩn ISO
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
            
            # 4. QUAN TRỌNG: Đăng ký PII scrubbing processor tại đây
            # Nó nên nằm trước các bước render để dữ liệu nhạy cảm được làm sạch sớm
            scrub_event,
            
            # 5. Các trình xử lý lỗi và stack trace
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            
            # 6. Ghi log vào file .jsonl (custom processor bạn đã viết)
            JsonlFileProcessor(),
            
            # 7. Cuối cùng, render ra JSON string để in ra console
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(), # Hoặc structlog.stdlib.LoggerFactory()
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.typing.FilteringBoundLogger:
    return structlog.get_logger()
