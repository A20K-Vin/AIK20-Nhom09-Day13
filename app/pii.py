from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}", # Matches 090 123 4567, 090.123.4567, etc.
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # TODO: Add more patterns (e.g., Passport, Vietnamese address keywords)

    # Passport Việt Nam:
    # - \b: word boundary (tránh match dính ký tự khác)
    # - [A-Z]: 1 chữ cái in hoa
    # - \d{7}: 7 chữ số phía sau
    # Ví dụ match: B1234567
    "passport": r"\b[A-Z]\d{7}\b",

    # Biển số xe Việt Nam:
    # - \b: word boundary
    # - \d{2}: mã tỉnh (VD: 30, 51,...)
    # - [A-Z]{1,2}: series chữ cái (A, F, AB,...)
    # - [- ]?: có thể có dấu '-' hoặc khoảng trắng
    # - \d{3,4}: 3–4 chữ số đầu
    # - [\.]?: có thể có dấu chấm phân cách
    # - \d{2}: 2 chữ số cuối
    # Ví dụ match:
    #   51F-12345
    #   30A-123.45
    #   29AB 12345
    "license_plate": r"\b\d{2}[A-Z]{1,2}[- ]?\d{3,4}[\.]?\d{2}\b"
}



def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 500) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
