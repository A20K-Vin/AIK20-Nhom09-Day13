# Evidence Collection Sheet

## Required screenshots
- Langfuse trace list with >= 10 traces
- One full trace waterfall
- JSON logs showing correlation_id
- Log line with PII redaction
- Dashboard with 6 panels
- Alert rules with runbook link

## Minimal demo screenshots
- Health PASS page: `http://127.0.0.1:8016/health`
- Metrics page: `http://127.0.0.1:8016/metrics`
- After dashboard page: `http://127.0.0.1:8016/demo/after`

The `/demo/after` page consolidates the dashboard, alert count, incident-after state, validation score, correlation IDs, and PII result into one screenshot.

## Optional screenshots
- Incident before/after fix
- Cost comparison before/after optimization
- Auto-instrumentation proof
