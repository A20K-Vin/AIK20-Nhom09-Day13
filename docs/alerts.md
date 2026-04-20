# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- Type: symptom-based
- Impact: tail latency spikes and users experience slow responses
- First checks:
  1. Open the slowest traces in the last hour
  2. Compare RAG span latency versus LLM span latency
  3. Check if the `rag_slow` incident toggle is enabled
- Mitigation:
  - truncate or simplify long queries
  - fallback to a faster retrieval source
  - lower prompt size or response generation complexity

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Type: symptom-based
- Impact: an increasing fraction of requests fail and users receive HTTP 500 errors
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces for root-cause spans
  3. Determine whether failures are caused by LLM, tool, or schema/validation issues
- Mitigation:
  - rollback the latest code change if it caused the failure
  - disable the failing tool or retrieval path
  - retry with a fallback model or default answer

## 3. Cost budget spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Type: symptom-based
- Impact: the application is burning cost too quickly and may exceed budget
- First checks:
  1. Split traces by feature and model to identify high-cost requests
  2. Compare tokens_in and tokens_out across traces
  3. Check if the `cost_spike` incident toggle was enabled
- Mitigation:
  - shorten prompts and reduce token usage
  - route low-effort requests to a cheaper model
  - enable caching for repeated or similar prompts

## 4. SLO breach: latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 30m`
- Type: slo-based
- Impact: the latency SLO is breached and user experience is degraded
- First checks:
  1. Review latency trends in the dashboard and traces
  2. Find whether a specific feature or model is causing the spike
  3. Confirm whether `rag_slow` or load-related incident toggles are active
- Mitigation:
  - scale down request concurrency if needed
  - apply timeouts or circuit-breakers to slow components
  - optimize the slowest spans or disable the problematic model

## 5. SLO breach: error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Type: slo-based
- Impact: the error rate SLO is violated, indicating reliability issues
- First checks:
  1. Verify error events in logs and trace metadata
  2. Check whether errors are concentrated in a single feature or endpoint
  3. Inspect recent deployment or incident changes
- Mitigation:
  - remove the faulty component from the request path
  - add retry/fallback logic for transient errors
  - fix the underlying exception and redeploy

## 6. SLO breach: daily cost
- Severity: P2
- Trigger: `daily_cost_usd > 2.5 for 1h`
- Type: slo-based
- Impact: daily cost budget is exceeded, leading to potential financial risk
- First checks:
  1. Compare daily cost against the baseline and high-cost traces
  2. Review tokens_in/out and per-request cost trends
  3. Confirm whether `cost_spike` or high-usage incidents were active
- Mitigation:
  - throttle or reject expensive requests
  - switch to cheaper model behavior for non-critical requests
  - enforce prompt and response size limits
