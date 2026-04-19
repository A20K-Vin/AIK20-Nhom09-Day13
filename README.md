# Day 13 Observability Lab Template

Template repo for a 4-hour hands-on lab on Monitoring, Logging, and Observability.

## What students will build

A small FastAPI "agent" instrumented with:
- structured JSON logging
- correlation ID propagation
- PII scrubbing
- Langfuse tracing
- minimal metrics aggregation
- SLOs, alerts, and a blueprint report

This template is intentionally incomplete. Teams are expected to finish TODOs during the lab.

## Suggested lab flow (Gapped Template)

1. **Run the starter app**: Observe that logs are basic and correlation IDs are missing.
2. **Implement Correlation IDs**: Fix `app/middleware.py` so every request has a unique `x-request-id`.
3. **Enrich Logs**: Update `app/main.py` to bind user, session, and feature context to every log.
4. **Sanitize Data**: Implement the PII scrubber in `app/logging_config.py`.
5. **Verify with Script**: Run `python scripts/validate_logs.py` to check your progress.
6. **Tracing**: Send 10-20 requests and verify traces in Langfuse (ensure `observe` decorator is used).
7. **Dashboards**: Build your 6-panel dashboard from exported metrics.
8. **Alerting**: Configure alert rules in `config/alert_rules.yaml` and test them.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Tooling

```bash
# Generate requests (use --concurrency 5 to test parallel bottlenecks)
python scripts/load_test.py --concurrency 5

# Inject failures live
python scripts/inject_incident.py --scenario rag_slow

# Check your implementation progress
python scripts/validate_logs.py
```

## Repo map

```text
app/
  main.py                FastAPI app
  agent.py               core agent pipeline
  logging_config.py      structlog config
  middleware.py          correlation ID middleware
  pii.py                 scrubbing helpers
  tracing.py             Langfuse helpers
  schemas.py             request/response/log models
  metrics.py             in-memory metrics helpers
  incidents.py           toggles for injected failures
  mock_llm.py            deterministic fake LLM
  mock_rag.py            deterministic fake retrieval
config/
  slo.yaml               starter SLOs
  alert_rules.yaml       starter alerts
  logging_schema.json    expected log schema
scripts/
  load_test.py           generate requests
  inject_incident.py     flip incident toggles
  validate_logs.py       schema checks for logs
data/
  sample_queries.jsonl   requests for testing
  expected_answers.jsonl starter quality checks
  incidents.json         scenario descriptions
  logs.jsonl             app output target
  audit.jsonl            optional audit log output

docs/
  blueprint-template.md  team submission template
  alerts.md              runbook + alert worksheet
  dashboard-spec.md      6-panel dashboard checklist
  grading-evidence.md    evidence collection sheet
  mock-debug-qa.md       oral/written debugging questions
```

## Team role suggestion

- Member A: logging + PII
- Member B: tracing + tags
- Member C: SLO + alerts
- Member D: load test + incident injection
- Member E: dashboard + evidence
- Member F: blueprint + demo lead

## Grading policy (60/40 Split)

Your final grade is calculated as follows:

1. **Group Score (60%)**: 
   - **Technical Implementation (30 pts)**: Verified by `validate_logs.py` and live system state.
   - **Incident Response (10 pts)**: Accuracy of your root cause analysis in the report.
   - **Live Demo (20 pts)**: Team presentation and system demonstration.
2. **Individual Score (40%)**:
   - **Individual Report (20 pts)**: Quality of your specific contributions in `docs/blueprint-template.md`.
   - **Git Evidence (20 pts)**: Traceable work via commits and code ownership.

**Passing Criteria**: 
- All `TODO` blocks must be completed.
- Minimum of 10 traces must be visible in Langfuse.
- Dashboard must show all 6 required panels.


### NOTE
Để validate, chạy các curl sau (lấy o sample_queries.jsonl)

```
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u01\",\"session_id\":\"s01\",\"feature\":\"qa\",\"message\":\"What is your refund policy? My email is student@vinuni.edu.vn\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u02\",\"session_id\":\"s02\",\"feature\":\"qa\",\"message\":\"Explain why metrics traces and logs work together\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u03\",\"session_id\":\"s03\",\"feature\":\"summary\",\"message\":\"Summarize the monitoring policy for production logging\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u04\",\"session_id\":\"s04\",\"feature\":\"qa\",\"message\":\"Can I get help with policy and monitoring?\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u05\",\"session_id\":\"s05\",\"feature\":\"qa\",\"message\":\"Here is my phone 0987654321, what should be logged?\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u06\",\"session_id\":\"s06\",\"feature\":\"summary\",\"message\":\"Give me a short summary of the observability workflow\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u07\",\"session_id\":\"s07\",\"feature\":\"qa\",\"message\":\"What should not appear in app logs?\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u08\",\"session_id\":\"s08\",\"feature\":\"qa\",\"message\":\"How do I debug tail latency?\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u09\",\"session_id\":\"s09\",\"feature\":\"qa\",\"message\":\"What is the policy for PII and credit card 4111 1111 1111 1111?\"}"

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u10\",\"session_id\":\"s10\",\"feature\":\"qa\",\"message\":\"How should alerts be designed?\"}"
```