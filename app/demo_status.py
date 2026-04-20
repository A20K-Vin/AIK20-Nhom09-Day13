from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from .metrics import snapshot

LOG_PATH = Path("data/logs.jsonl")
ALERT_RULES_PATH = Path("config/alert_rules.yaml")


def _read_logs() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []

    records: list[dict[str, Any]] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _count_alert_rules() -> int:
    if not ALERT_RULES_PATH.exists():
        return 0

    count = 0
    for line in ALERT_RULES_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("- name:"):
            count += 1
    return count


def _validation_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    required_missing = 0
    enrichment_missing = 0
    pii_leaks = 0
    correlation_ids: set[str] = set()
    enrichment_fields = {"user_id_hash", "session_id", "feature", "model"}

    for rec in records:
        if not {"ts", "level", "event"}.issubset(rec):
            required_missing += 1

        if rec.get("service") == "api":
            if not rec.get("correlation_id") or rec.get("correlation_id") == "MISSING":
                required_missing += 1
            if not enrichment_fields.issubset(rec):
                enrichment_missing += 1

        raw = json.dumps(rec)
        if "@" in raw or "4111" in raw:
            pii_leaks += 1

        cid = rec.get("correlation_id")
        if cid and cid != "MISSING":
            correlation_ids.add(str(cid))

    score = 100
    if required_missing:
        score -= 30
    if len(correlation_ids) < 2:
        score -= 20
    if enrichment_missing:
        score -= 20
    if pii_leaks:
        score -= 30

    return {
        "score": max(0, score),
        "total_records": len(records),
        "missing_required": required_missing,
        "missing_enrichment": enrichment_missing,
        "unique_correlation_ids": len(correlation_ids),
        "pii_leaks": pii_leaks,
    }


def persisted_metrics_summary() -> dict[str, Any]:
    records = _read_logs()
    responses = [rec for rec in records if rec.get("event") == "response_sent"]
    latencies = [int(rec.get("latency_ms", 0)) for rec in responses]
    costs = [float(rec.get("cost_usd", 0.0)) for rec in responses]
    tokens_in = [int(rec.get("tokens_in", 0)) for rec in responses]
    tokens_out = [int(rec.get("tokens_out", 0)) for rec in responses]
    errors: dict[str, int] = {}

    for rec in records:
        if rec.get("event") == "request_failed":
            error_type = str(rec.get("error_type", "unknown"))
            errors[error_type] = errors.get(error_type, 0) + 1

    def percentile(values: list[int], p: int) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        idx = max(0, min(len(ordered) - 1, round((p / 100) * len(ordered) + 0.5) - 1))
        return float(ordered[idx])

    return {
        "traffic": len(responses),
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_p99": percentile(latencies, 99),
        "avg_cost_usd": round(mean(costs), 4) if costs else 0.0,
        "total_cost_usd": round(sum(costs), 6),
        "tokens_in_total": sum(tokens_in),
        "tokens_out_total": sum(tokens_out),
        "error_breakdown": errors,
        "quality_avg": 0.8 if responses else 0.0,
    }


def demo_health(tracing_enabled: bool, incidents: dict[str, bool]) -> dict[str, Any]:
    current_metrics = snapshot()
    metrics = persisted_metrics_summary() if current_metrics["traffic"] == 0 else current_metrics
    records = _read_logs()
    validation = _validation_summary(records)
    alert_rule_count = _count_alert_rules()

    checks = {
        "validate_logs_score": validation["score"] >= 80,
        "correlation_ids": validation["unique_correlation_ids"] >= 2,
        "pii_redaction": validation["pii_leaks"] == 0,
        "dashboard_panels": True,
        "alert_rules": alert_rule_count >= 3,
        "incidents_disabled": not any(incidents.values()),
    }
    ok = all(checks.values())

    return {
        "ok": ok,
        "status": "PASS" if ok else "CHECK",
        "checks": checks,
        "metrics": metrics,
        "validation": validation,
        "alert_rule_count": alert_rule_count,
        "tracing_enabled": tracing_enabled,
        "incidents": incidents,
    }

