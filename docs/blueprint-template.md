# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
<<<<<<< HEAD
- [GROUP_NAME]: 9
- [REPO_URL]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13.git
- [MEMBERS]:
=======
- \[GROUP_NAME]: 
- \[REPO_URL]: 
- \[MEMBERS]:
>>>>>>> c2f0b43f598250cf190c7fb99ced72279cb9fcfb
  - Member A: Nguyen Hoang Khai Minh | Role: Logging & PII
  - Member B: Nguyen Thuy Linh | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alerts
  - Member D: Nguyễn Hoàng Duy | Role: Load Test & Incident Injection
  - Member E: [Name] | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- \[VALIDATE_LOGS_FINAL_SCORE]: 100/100
- \[TOTAL_TRACES_COUNT]: 
- \[PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- \[EVIDENCE_CORRELATION_ID_SCREENSHOT]: screenshot/EVIDENCE_CORRELATION_ID_SCREENSHOT.PNG
- \[EVIDENCE_PII_REDACTION_SCREENSHOT]: screenshot/EVIDENCE_PII_REDACTION_SCREENSHOT.png
- \[EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- \[TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- \[DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- \[SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 163.55ms|
| Error Rate | < 2% | 28d | 40.00%|
| Cost Budget | < $2.5/day | 1d | $0.098685|

### 3.3 Alerts & Runbook
- \[ALERT_RULES_SCREENSHOT]: [Path to image]
- \[SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)
- \[SCENARIO_NAME]: rag_slow | cost_spike | tool_fail

**Scenario 1 — rag_slow**
- \[SYMPTOMS_OBSERVED]: Latency tăng đột biến từ ~150ms lên ~5000–8000ms. Toàn bộ request vượt SLO latency P95 < 3000ms.
- \[ROOT_CAUSE_PROVED_BY]: `mock_rag.py` gọi `time.sleep(2.5)` khi `STATE["rag_slow"] = True`, làm RAG span delay 2500ms mỗi request. Evidence: screenshot/EVIDENCE_INCIDENT_RAG_SLOW.png
- \[FIX_ACTION]: `python scripts/inject_incident.py --scenario rag_slow --disable` — latency trở về ~150–800ms ngay lập tức.
- \[PREVENTIVE_MEASURE]: Alert `high_latency_p95` trigger trước khi SLO breach. Thêm timeout cho RAG call và fallback retrieval khi RAG chậm > 1s.

**Scenario 2 — cost_spike**
- \[SYMPTOMS_OBSERVED]: `output_tokens` tăng gấp 4 lần, cost_usd tăng vọt so với baseline. Metrics `/metrics` cho thấy `avg_cost_usd` bất thường.
- \[ROOT_CAUSE_PROVED_BY]: `mock_llm.py` nhân `output_tokens *= 4` khi `STATE["cost_spike"] = True`. Evidence: screenshot/EVIDENCE_INCIDENT_COST_SPIKE.png
- \[FIX_ACTION]: `python scripts/inject_incident.py --scenario cost_spike --disable`.
- \[PREVENTIVE_MEASURE]: Alert `cost_budget_spike` trigger khi `hourly_cost_usd > 2x_baseline for 15m`. Route request đơn giản sang model rẻ hơn.

**Scenario 3 — tool_fail**
- \[SYMPTOMS_OBSERVED]: Toàn bộ request trả về HTTP 500, correlation_id = None.
- \[ROOT_CAUSE_PROVED_BY]: `mock_rag.py` raise `RuntimeError("Vector store timeout")` khi `STATE["tool_fail"] = True`. Evidence: screenshot/EVIDENCE_INCIDENT_TOOL_FAIL.png
- \[FIX_ACTION]: `python scripts/inject_incident.py --scenario tool_fail --disable`.
- \[PREVENTIVE_MEASURE]: Alert `high_error_rate` (P1, trigger > 5% for 5m). Thêm retry logic và fallback answer khi RAG tool fail.

---

## 5. Individual Contributions & Evidence

### Nguyen Hoang Khai Minh
- \[TASKS_COMPLETED]: Logging & PII
- \[EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/495c7a580189fa6e1ff301040327ec3395e47f48 

<<<<<<< HEAD
### Nguyen Thuy Linh
- [TASKS_COMPLETED]: Tracing & Enrichment
- [EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/9b8a98bb1e46f7c4581b5f5caf733b1f7cc3b445
=======
### [MEMBER_B_NAME]
- \[TASKS_COMPLETED]: 
- \[EVIDENCE_LINK]: 
>>>>>>> c2f0b43f598250cf190c7fb99ced72279cb9fcfb

### [MEMBER_C_NAME]
- \[TASKS_COMPLETED]: 
- \[EVIDENCE_LINK]: 

### Nguyễn Hoàng Duy
- \[TASKS_COMPLETED]: Load test (concurrency 1 & 5), inject 3 incidents (rag_slow / cost_spike / tool_fail), ghi nhận kết quả và viết incident response report
- \[EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/ee7fe48

### [MEMBER_E_NAME]
- \[TASKS_COMPLETED]: 
- \[EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- \[BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- \[BONUS_AUDIT_LOGS]: (Description + Evidence)
- \[BONUS_CUSTOM_METRIC]: (Description + Evidence)
