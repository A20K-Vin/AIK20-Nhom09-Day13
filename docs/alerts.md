# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- Impact: tail latency breaches SLO
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries
  - fallback retrieval source
  - lower prompt size

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Impact: users receive failed responses
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - rollback latest change
  - disable failing tool
  - retry with fallback model

## 3. Cost budget spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Impact: burn rate exceeds budget
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache

## 4. SLO breach latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 30m`
- Impact: latency SLO is violated and users experience slow answers
- First checks:
  1. Confirm the P95 panel on the dashboard crosses the SLO line
  2. Open the slowest trace waterfall and compare RAG vs LLM spans
  3. Check whether `rag_slow` is enabled
- Mitigation:
  - disable the incident toggle if it is active
  - add timeout and fallback retrieval for RAG
  - reduce prompt/context size for slow requests

## 5. SLO breach error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Impact: the service is failing more often than the agreed SLO
- First checks:
  1. Check `/metrics` error breakdown
  2. Inspect recent `request_failed` logs by `correlation_id`
  3. Verify whether `tool_fail` is enabled
- Mitigation:
  - disable the failing incident toggle
  - retry failed tool calls with a short timeout
  - return a fallback answer when retrieval is unavailable

## 6. SLO breach daily cost
- Severity: P2
- Trigger: `daily_cost_usd > 2.5 for 1h`
- Impact: daily budget is at risk
- First checks:
  1. Compare cost panel against the normal baseline
  2. Split high-cost traces by feature and model
  3. Check whether `cost_spike` is enabled
- Mitigation:
  - cap maximum output tokens
  - route simple requests to a cheaper model
  - shorten prompts and cache repeated context
