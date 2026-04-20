# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: Nguyen Hoang Khai Minh | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alerts
  - Member D: Nguyễn Hoàng Duy | Role: Load Test & Incident Injection
  - Member E: [Name] | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: screenshot/EVIDENCE_CORRELATION_ID_SCREENSHOT.PNG
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: screenshot/EVIDENCE_PII_REDACTION_SCREENSHOT.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | |
| Error Rate | < 2% | 28d | |
| Cost Budget | < $2.5/day | 1d | |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency tăng đột biến từ ~150ms (bình thường) lên ~5000–8000ms sau khi inject incident. Load test với concurrency 3 cho thấy toàn bộ request vượt 5000ms, vi phạm SLO latency P95 < 3000ms.
- [ROOT_CAUSE_PROVED_BY]: Log và metrics tại `/metrics` cho thấy `latency_p95_ms` vọt lên ~8000ms. Nguyên nhân gốc: `mock_rag.py` gọi `time.sleep(2.5)` khi `STATE["rag_slow"] = True`, làm RAG span bị delay 2500ms mỗi request. Evidence: screenshot/EVIDENCE_INCIDENT_RAG_SLOW.png
- [FIX_ACTION]: Chạy `python scripts/inject_incident.py --scenario rag_slow --disable` để tắt incident. Latency trở về ~150–800ms ngay lập tức.
- [PREVENTIVE_MEASURE]: Alert `high_latency_p95` (trigger `latency_p95_ms > 5000 for 30m`) sẽ notify on-call trước khi SLO breach. Nên thêm timeout cho RAG call và fallback retrieval khi RAG chậm > 1s.

---

## 5. Individual Contributions & Evidence

### Nguyen Hoang Khai Minh
- [TASKS_COMPLETED]: Logging & PII
- [EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/495c7a580189fa6e1ff301040327ec3395e47f48 

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Nguyễn Hoàng Duy
- [TASKS_COMPLETED]: Load test (concurrency 1 & 5), inject 3 incidents (rag_slow / cost_spike / tool_fail), ghi nhận kết quả và viết incident response report
- [EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/80e831e

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
