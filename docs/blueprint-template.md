# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 9
- [REPO_URL]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13.git
- [MEMBERS]:
  - Member A: Nguyễn Hoàng Khải Minh - 2A202600159 | Role: Logging & PII
  - Member B: Nguyễn Thùy Linh - 2A202600216 | Role: Tracing & Enrichment
  - Member C: Nguyễn Thị Diệu Linh - 2A202600209 | Role: SLO & Alerts
  - Member D: Nguyễn Hoàng Duy - 2A202600158 | Role: Load Test & Incident Injection
  - Member E: Nguyễn Triệu Gia Khánh - 2A202600225 | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- \[VALIDATE_LOGS_FINAL_SCORE]: 100/100
- \[TOTAL_TRACES_COUNT]: 10
- \[PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- \[EVIDENCE_CORRELATION_ID_SCREENSHOT]: screenshot/EVIDENCE_JSON_LOG.png
- \[EVIDENCE_PII_REDACTION_SCREENSHOT]: screenshot/EVIDENCE_PII.png
- \[EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: screenshot/EVIDENCE_LANGFUSE_TRACE_LIST.png
- \[TRACE_WATERFALL_EXPLANATION]: Span `retrieve_documents` trong trace chiếm phần lớn thời gian khi bật incident `rag_slow` (khoảng 2500ms), trong khi các span khác gần như ổn định; điều này xác nhận bottleneck nằm ở bước RAG retrieval.

### 3.2 Dashboard & SLOs
- \[DASHBOARD_6_PANELS_SCREENSHOT]: 
screenshot\EVIDENCE_DASHBOARD.png
screenshot\EVIDENCE_DASHBOARD_COST.png
- \[SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 163.55ms|
| Error Rate | < 2% | 28d | 40.00%|
| Cost Budget | < $2.5/day | 1d | $0.098685|

### 3.3 Alerts & Runbook
- \[ALERT_RULES_SCREENSHOT]: screenshot\ALERT_RULES_SCREENSHOT.png
- \[SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

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

### Nguyễn Hoàng Khải Minh
- \[TASKS_COMPLETED]: Logging & PII
- \[EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/495c7a580189fa6e1ff301040327ec3395e47f48 

### Nguyễn Thùy Linh
- \[TASKS_COMPLETED]: Tracing instrumentation, log enrichment và hoàn thiện report nhóm theo template
- \[EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/9b8a98bb1e46f7c4581b5f5caf733b1f7cc3b445

### Nguyễn Thị Diệu Linh
- \[TASKS_COMPLETED]: SLO + alerts
- \[EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/a081278cb6f8c06f933dd15fdb93d090db7fa07d
https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/10ac7f3baf60a3021515735df279fbe25a3ace7b

### Nguyễn Hoàng Duy
- \[TASKS_COMPLETED]: Load test (concurrency 1 & 5), inject 3 incidents (rag_slow / cost_spike / tool_fail), ghi nhận kết quả và viết incident response report
- \[EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/ee7fe48

### Nguyễn Triệu Gia Khánh
- \[TASKS_COMPLETED]: Tổng hợp bằng chứng, chuẩn hóa blueprint report theo rubric, dẫn dắt phần demo flow Metrics -> Traces -> Logs và đối chiếu tiêu chí pass; bổ sung 3 màn hình bonus để chụp trực tiếp trên web gồm Incident before/after fix, Cost comparison before/after optimization và Auto-instrumentation proof.

- \[EVIDENCE_LINK]: https://github.com/A20K-Vin/AIK20-Nhom09-Day13/commit/c2f0b43

- \[EVIDENCE_SCREENSHOTS]:
  - Incident before evidence: screenshot/EVIDENCE_INCIDENT_RAG_SLOW.png

  - Incident after fix: screenshot/INCIDENT_AFTER.png

  - Cost comparison before/after optimization: screenshot/COST_COMPARISON_BEFORE-AFTER.png

  - Auto-instrumentation proof: screenshot/AUTO_INSTRUMENTATION_PROOF.png
  
- \[DEMO_ROUTES_ADDED]:
  - `/demo/incident-after`
  - `/demo/cost-comparison`
  - `/demo/auto-instrumentation`

---

## 6. Bonus Items (Optional)
- \[BONUS_INCIDENT_BEFORE_AFTER]: Demonstrated incident recovery from `rag_slow` by comparing slow RAG latency before fix with the post-fix healthy state where all incident toggles are disabled. Evidence: screenshot/EVIDENCE_INCIDENT_RAG_SLOW.png and screenshot/INCIDENT_AFTER.png

- \[BONUS_COST_OPTIMIZATION]: Demonstrated cost optimization by comparing the cost spike request (`output_tokens=664`, cost_usd around $0.010059) with the optimized baseline (`output_tokens=164`, cost_usd around $0.002571), showing about 74% per-request cost reduction. Evidence: screenshot/EVIDENCE_INCIDENT_COST_SPIKE.png and screenshot/COST_COMPARISON_BEFORE-AFTER.png

- \[BONUS_AUTO_INSTRUMENTATION]: Proved auto-instrumentation through the `@observe(name="LabAgent.run")` decorator, Langfuse context hooks, correlation ID middleware, structured JSON logs, token usage capture and PII scrubber. Evidence: screenshot/AUTO_INSTRUMENTATION_PROOF.png

- \[BONUS_AUDIT_LOGS]: Not claimed as a separate bonus item; focus was placed on incident recovery, cost optimization and auto-instrumentation proof.

- \[BONUS_CUSTOM_METRIC]: Quality proxy, token totals, cost totals and latency percentiles are exposed in `/metrics` and summarized in the demo pages. Evidence: screenshot/COST_COMPARISON_BEFORE-AFTER.png and screenshot/AUTO_INSTRUMENTATION_PROOF.png
