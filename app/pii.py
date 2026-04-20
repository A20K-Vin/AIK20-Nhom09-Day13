from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}", # Matches 090 123 4567, 090.123.4567, etc.
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",

    "address": r"(?i)\b(?:số|ngõ|ngách|đường|thôn|xóm|xã|phường|quận|huyện|tỉnh|thành phố)\s+[^,.]+[^,.]+",

    # Số tài khoản ngân hàng (Thường từ 9-15 chữ số tùy bank)
    "bank_account": r"\b\d{9,16}\b",

    # Mã số thuế (MST) cá nhân/doanh nghiệp: 10 số hoặc 13 số (nếu có chi nhánh)
    "tax_id": r"\b\d{10}(?:-\d{3})?\b",
    
    # Ngày sinh (Dạng dd/mm/yyyy hoặc dd-mm-yyyy)
    "dob": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{4})\b"

    "passport": r"\b[A-Z]\d{7}\b",

    "license_plate": r"\b\d{2}[A-Z]{1,2}[- ]?\d{3,4}[\.]?\d{2}\b"
}


# Compile tất cả patterns một lần duy nhất để tăng tốc
COMPILED_PATTERNS = {name: re.compile(pattern) for name, pattern in PII_PATTERNS.items()}

def scrub_text(text: str) -> str:
    safe = text
    for name, compiled_re in COMPILED_PATTERNS.items():
        safe = compiled_re.sub(f"[REDACTED_{name.upper()}]", safe)
    return safe

def summarize_text(text: str, max_len: int = 500) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
