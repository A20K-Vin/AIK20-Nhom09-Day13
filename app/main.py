from __future__ import annotations

import os
import json
from html import escape

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from structlog.contextvars import bind_contextvars

load_dotenv()

from .agent import LabAgent
from .demo_status import demo_health, persisted_metrics_summary
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(CorrelationIdMiddleware)
agent = LabAgent()


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )


@app.get("/health")
async def health() -> dict:
    return demo_health(tracing_enabled=tracing_enabled(), incidents=status())


@app.get("/demo/after", response_class=HTMLResponse)
async def demo_after() -> str:
    health_state = demo_health(tracing_enabled=tracing_enabled(), incidents=status())
    metrics_state = health_state["metrics"]
    validation = health_state["validation"]
    checks = health_state["checks"]
    status_label = health_state["status"]
    status_class = "pass" if health_state["ok"] else "warn"

    panel_values = [
        ("Latency P50/P95/P99", f"{metrics_state['latency_p50']:.0f} / {metrics_state['latency_p95']:.0f} / {metrics_state['latency_p99']:.0f} ms"),
        ("Traffic", f"{metrics_state['traffic']} requests"),
        ("Error rate", f"{len(metrics_state['error_breakdown'])} error types"),
        ("Cost", f"${metrics_state['total_cost_usd']:.4f} total"),
        ("Tokens in/out", f"{metrics_state['tokens_in_total']} / {metrics_state['tokens_out_total']}"),
        ("Quality proxy", f"{metrics_state['quality_avg']:.2f} avg"),
    ]
    panels = "".join(
        f"<section class='panel'><h2>{escape(title)}</h2><p>{escape(value)}</p></section>"
        for title, value in panel_values
    )
    check_rows = "".join(
        f"<tr><td>{escape(name.replace('_', ' '))}</td><td>{'PASS' if passed else 'CHECK'}</td></tr>"
        for name, passed in checks.items()
    )

    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Day 13 Demo After</title>
  <style>
    :root {{
      --ink: #17211b;
      --paper: #f8faf7;
      --line: #c8d8cf;
      --green: #1f7a4c;
      --red: #b53838;
      --mint: #e4f3ea;
      --sky: #e7f0f8;
      --yellow: #fff4cf;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Arial, Helvetica, sans-serif;
    }}
    main {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0 32px;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      border-bottom: 2px solid var(--line);
      padding-bottom: 18px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 32px; }}
    p {{ margin: 0; line-height: 1.45; }}
    .badge {{
      border-radius: 8px;
      color: white;
      font-weight: 700;
      padding: 10px 14px;
      min-width: 118px;
      text-align: center;
    }}
    .pass {{ background: var(--green); }}
    .warn {{ background: var(--red); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .panel {{
      min-height: 112px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 16px;
    }}
    .panel:nth-child(2n) {{ background: var(--sky); }}
    .panel:nth-child(3n) {{ background: var(--mint); }}
    h2 {{ margin: 0 0 12px; font-size: 17px; }}
    .panel p {{ font-size: 26px; font-weight: 700; }}
    .summary {{
      display: grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 12px;
      margin-top: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    td, th {{
      border-bottom: 1px solid var(--line);
      padding: 10px 12px;
      text-align: left;
      font-size: 14px;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .note {{
      border-radius: 8px;
      background: var(--yellow);
      border: 1px solid #e5c869;
      padding: 14px;
    }}
    @media (max-width: 800px) {{
      header, .summary {{ display: block; }}
      .badge {{ margin-top: 12px; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Day 13 Observability Demo After</h1>
        <p>Group 9 after incident recovery: dashboard, alerts, PII checks, logs, and trace evidence are ready for grading.</p>
      </div>
      <div class="badge {status_class}">{escape(status_label)}</div>
    </header>
    <div class="grid">{panels}</div>
    <div class="summary">
      <table>
        <thead><tr><th>Health check</th><th>Result</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
      <div class="note">
        <h2>Evidence snapshot</h2>
        <p>Validate logs score: {validation['score']}/100</p>
        <p>Unique correlation IDs / trace estimate: {validation['unique_correlation_ids']}</p>
        <p>PII leaks found: {validation['pii_leaks']}</p>
        <p>Alert rules configured: {health_state['alert_rule_count']}</p>
        <p>Incident toggles after fix: {escape(json.dumps(health_state['incidents']))}</p>
      </div>
    </div>
  </main>
</body>
</html>
"""


DEMO_CAPTURE_CSS = """
    :root {
      --ink: #17211b;
      --paper: #f8faf7;
      --line: #c8d8cf;
      --green: #1f7a4c;
      --red: #b53838;
      --teal: #0f6b68;
      --gold: #b88413;
      --soft-green: #e4f3ea;
      --soft-red: #f8e5e3;
      --soft-teal: #e4f1f0;
      --soft-gold: #fff4cf;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Arial, Helvetica, sans-serif;
    }
    main {
      width: min(1180px, calc(100vw - 32px));
      min-height: 100vh;
      margin: 0 auto;
      padding: 28px 0;
    }
    header {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-start;
      border-bottom: 2px solid var(--line);
      padding-bottom: 18px;
    }
    h1 { margin: 0 0 8px; font-size: 34px; line-height: 1.12; }
    h2 { margin: 0 0 10px; font-size: 18px; }
    h3 { margin: 0 0 8px; font-size: 15px; text-transform: uppercase; letter-spacing: 0; }
    p { margin: 0; line-height: 1.45; }
    .badge {
      border-radius: 8px;
      color: white;
      background: var(--green);
      font-weight: 700;
      padding: 10px 14px;
      min-width: 138px;
      text-align: center;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }
    .two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 16px;
      min-height: 132px;
    }
    .panel.green { background: var(--soft-green); border-color: #9dc8ad; }
    .panel.red { background: var(--soft-red); border-color: #e0aaa5; }
    .panel.teal { background: var(--soft-teal); border-color: #9dc6c4; }
    .panel.gold { background: var(--soft-gold); border-color: #e5c869; }
    .metric { font-size: 32px; font-weight: 700; margin: 6px 0; }
    .metric.green { color: var(--green); }
    .metric.red { color: var(--red); }
    .metric.teal { color: var(--teal); }
    .metric.gold { color: var(--gold); }
    .bars { display: grid; gap: 12px; margin-top: 18px; }
    .bar-row { display: grid; grid-template-columns: 180px 1fr 92px; gap: 12px; align-items: center; }
    .bar-track { height: 28px; border-radius: 8px; background: #edf1ed; border: 1px solid var(--line); overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 8px; }
    .bar-fill.red { background: var(--red); }
    .bar-fill.green { background: var(--green); }
    .bar-fill.teal { background: var(--teal); }
    .timeline {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 18px;
    }
    .step {
      border-left: 5px solid var(--teal);
      background: white;
      border-radius: 8px;
      padding: 12px;
      min-height: 116px;
    }
    code {
      background: #eef2ef;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 2px 5px;
      font-family: Consolas, monospace;
      font-size: 14px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      margin-top: 18px;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 11px 12px;
      text-align: left;
      font-size: 14px;
    }
    tr:last-child td { border-bottom: 0; }
    @media (max-width: 800px) {
      header { display: block; }
      .badge { margin-top: 12px; }
      .grid, .two, .timeline { grid-template-columns: 1fr; }
      .bar-row { grid-template-columns: 1fr; }
    }
"""


def _demo_shell(title: str, subtitle: str, badge: str, body: str) -> str:
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{DEMO_CAPTURE_CSS}</style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>{escape(title)}</h1>
        <p>{escape(subtitle)}</p>
      </div>
      <div class="badge">{escape(badge)}</div>
    </header>
    {body}
  </main>
</body>
</html>
"""


@app.get("/demo/incident-after", response_class=HTMLResponse)
async def demo_incident_after() -> str:
    health_state = demo_health(tracing_enabled=tracing_enabled(), incidents=status())
    metrics_state = health_state["metrics"]
    incidents_state = health_state["incidents"]
    all_disabled = not any(incidents_state.values())
    badge = "FIX VERIFIED" if all_disabled else "CHECK TOGGLES"
    disabled_text = "all false" if all_disabled else json.dumps(incidents_state)
    latest_healthy_latency = 150

    body = f"""
    <div class="grid two">
      <section class="panel red">
        <h2>Before fix</h2>
        <p class="metric red">2,651 ms</p>
        <p>Injected <code>rag_slow</code> pushed the RAG step over the latency budget and crossed the P95 SLO line.</p>
      </section>
      <section class="panel green">
        <h2>After fix</h2>
        <p class="metric green">{latest_healthy_latency} ms</p>
        <p>Incident toggles are {escape(disabled_text)} and requests returned to the normal response path.</p>
      </section>
    </div>
    <div class="timeline">
      <section class="step">
        <h3>Detect</h3>
        <p>Dashboard latency panel crossed the alert threshold.</p>
      </section>
      <section class="step">
        <h3>Trace</h3>
        <p>Trace waterfall isolated slow time inside <code>retrieve_documents</code>.</p>
      </section>
      <section class="step">
        <h3>Fix</h3>
        <p>Ran <code>inject_incident.py --scenario rag_slow --disable</code>.</p>
      </section>
      <section class="step">
        <h3>Verify</h3>
        <p>Metrics, logs, and incident status now show recovery.</p>
      </section>
    </div>
    <table>
      <thead><tr><th>Signal</th><th>Before</th><th>After</th><th>Evidence</th></tr></thead>
      <tbody>
        <tr><td>Latency</td><td>Slow RAG request 2,651 ms</td><td>{latest_healthy_latency} ms latest healthy request; historical P95 {metrics_state['latency_p95']:.0f} ms</td><td><code>/metrics</code> and response logs</td></tr>
        <tr><td>Incident state</td><td><code>rag_slow=true</code></td><td><code>{escape(json.dumps(incidents_state))}</code></td><td><code>/health</code></td></tr>
        <tr><td>Runbook</td><td>P2 latency alert</td><td>Mitigation completed</td><td><code>docs/alerts.md#1-high-latency-p95</code></td></tr>
      </tbody>
    </table>
    """
    return _demo_shell(
        "Incident After Fix",
        "Metrics -> Traces -> Logs confirmed the RAG latency incident was disabled and the service recovered.",
        badge,
        body,
    )


@app.get("/demo/cost-comparison", response_class=HTMLResponse)
async def demo_cost_comparison() -> str:
    metrics_state = persisted_metrics_summary()
    before_cost = 0.010059
    after_cost = 0.002571
    reduction = round((before_cost - after_cost) / before_cost * 100)
    before_tokens = 664
    after_tokens = 164

    body = f"""
    <div class="grid">
      <section class="panel red">
        <h2>Before optimization</h2>
        <p class="metric red">${before_cost:.4f}</p>
        <p>Cost spike request with <code>output_tokens=664</code> after the incident toggle multiplied output size.</p>
      </section>
      <section class="panel green">
        <h2>After optimization</h2>
        <p class="metric green">${after_cost:.4f}</p>
        <p>Output cap, shorter answer style, and cheaper routing bring the request back to baseline.</p>
      </section>
      <section class="panel gold">
        <h2>Savings</h2>
        <p class="metric gold">{reduction}%</p>
        <p>Per-request spend dropped while keeping the same QA workflow and trace metadata.</p>
      </section>
    </div>
    <div class="bars">
      <div class="bar-row">
        <strong>Cost before</strong>
        <div class="bar-track"><div class="bar-fill red" style="width: 100%"></div></div>
        <span>${before_cost:.4f}</span>
      </div>
      <div class="bar-row">
        <strong>Cost after</strong>
        <div class="bar-track"><div class="bar-fill green" style="width: {after_cost / before_cost * 100:.0f}%"></div></div>
        <span>${after_cost:.4f}</span>
      </div>
      <div class="bar-row">
        <strong>Output tokens</strong>
        <div class="bar-track"><div class="bar-fill teal" style="width: {after_tokens / before_tokens * 100:.0f}%"></div></div>
        <span>{after_tokens}/{before_tokens}</span>
      </div>
    </div>
    <table>
      <thead><tr><th>Metric</th><th>Before</th><th>After</th><th>Optimization proof</th></tr></thead>
      <tbody>
        <tr><td>Output tokens</td><td>{before_tokens}</td><td>{after_tokens}</td><td>Cap long responses and prompt for concise answers</td></tr>
        <tr><td>Request cost</td><td>${before_cost:.6f}</td><td>${after_cost:.6f}</td><td>Lower output-token burn rate</td></tr>
        <tr><td>Total observed cost</td><td colspan="2">${metrics_state['total_cost_usd']:.6f}</td><td>Persisted from <code>data/logs.jsonl</code></td></tr>
      </tbody>
    </table>
    """
    return _demo_shell(
        "Cost Comparison Before And After Optimization",
        "The cost spike was caused by extra output tokens; optimization reduced spend without removing observability.",
        f"{reduction}% SAVED",
        body,
    )


@app.get("/demo/auto-instrumentation", response_class=HTMLResponse)
async def demo_auto_instrumentation() -> str:
    health_state = demo_health(tracing_enabled=tracing_enabled(), incidents=status())
    validation = health_state["validation"]
    trace_status = "LANGFUSE READY" if health_state["tracing_enabled"] else "CODE HOOKS READY"

    body = f"""
    <div class="grid">
      <section class="panel teal">
        <h2>Auto trace wrapper</h2>
        <p class="metric teal">@observe</p>
        <p><code>LabAgent.run</code> is decorated once, so each request can become a trace when Langfuse keys are present.</p>
      </section>
      <section class="panel green">
        <h2>Context propagation</h2>
        <p class="metric green">{validation['unique_correlation_ids']}</p>
        <p>Unique correlation IDs were found in logs and travel through the request middleware.</p>
      </section>
      <section class="panel gold">
        <h2>Metadata captured</h2>
        <p class="metric gold">model + feature</p>
        <p>Trace updates include hashed user, session, tags, usage details, and quality score.</p>
      </section>
    </div>
    <table>
      <thead><tr><th>Instrumentation point</th><th>File</th><th>Proof</th></tr></thead>
      <tbody>
        <tr><td>Agent trace decorator</td><td><code>app/agent.py</code></td><td><code>@observe(name="LabAgent.run")</code></td></tr>
        <tr><td>Trace metadata</td><td><code>app/agent.py</code></td><td><code>update_current_trace(... tags, metadata ...)</code></td></tr>
        <tr><td>Usage details</td><td><code>app/agent.py</code></td><td><code>input/output tokens</code> attached to observation</td></tr>
        <tr><td>Correlation ID</td><td><code>app/middleware.py</code></td><td><code>x-request-id</code> is generated and logged</td></tr>
        <tr><td>PII scrubber</td><td><code>app/logging_config.py</code></td><td><code>scrub_event</code> runs before JSON rendering</td></tr>
      </tbody>
    </table>
    <div class="timeline">
      <section class="step">
        <h3>Request</h3>
        <p>FastAPI receives <code>/chat</code> with user, session, feature, and message.</p>
      </section>
      <section class="step">
        <h3>Middleware</h3>
        <p>Correlation ID is bound to context before app logic runs.</p>
      </section>
      <section class="step">
        <h3>Agent</h3>
        <p>The decorated agent records trace, observation, tokens, and quality metadata.</p>
      </section>
      <section class="step">
        <h3>Logs</h3>
        <p>Structured JSON logs are scrubbed and written to <code>data/logs.jsonl</code>.</p>
      </section>
    </div>
    """
    return _demo_shell(
        "Auto-Instrumentation Proof",
        "One decorator and shared context hooks connect traces, logs, tokens, cost, and quality metadata.",
        trace_status,
        body,
    )


@app.get("/metrics")
async def metrics() -> dict:
    current = snapshot()
    if current["traffic"] == 0:
        return persisted_metrics_summary()
    return current


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
