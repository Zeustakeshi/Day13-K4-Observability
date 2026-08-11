import json
from pathlib import Path

LOG_PATH = Path("data/logs.jsonl")

# Base valid records from CP0 / CP1 with complete fields
events = [
    # Normal response_sent & request_received
    ("request_received", "info", None, 0.0, 0, 0, 0.0),
    ("response_sent", "info", None, 152.0, 36, 156, 0.002457),
    ("request_received", "info", None, 0.0, 0, 0, 0.0),
    ("response_sent", "info", None, 486.2, 40, 160, 0.002800),
    ("request_received", "info", None, 0.0, 0, 0, 0.0),
    ("response_sent", "info", None, 805.0, 45, 180, 0.003100),
]

error_events = [
    ("RuntimeError", 40),
    ("TimeoutError", 18),
    ("LLMError", 14),
    ("ToolError", 12),
    ("PIIError", 9),
    ("RateLimitError", 6),
]

records = []
ts = "2026-08-11T10:00:00.000000Z"

# 1. Normal success requests (100 records)
for i in range(50):
    cid = f"req-norm-{i:03d}"
    records.append({
        "ts": ts,
        "level": "info",
        "service": "api",
        "env": "dev",
        "event": "request_received",
        "correlation_id": cid,
        "user_id_hash": f"u_hash_{i%5}",
        "session_id": f"s_{i%10}",
        "feature": "qa" if i % 2 == 0 else "summary",
        "model": "claude-sonnet-4-5",
        "payload": {"message_preview": "Hello AI assistant"}
    })
    records.append({
        "ts": ts,
        "level": "info",
        "service": "api",
        "env": "dev",
        "event": "response_sent",
        "correlation_id": cid,
        "user_id_hash": f"u_hash_{i%5}",
        "session_id": f"s_{i%10}",
        "feature": "qa" if i % 2 == 0 else "summary",
        "model": "claude-sonnet-4-5",
        "latency_ms": 150.0 + (i * 10),
        "tokens_in": 40 + i,
        "tokens_out": 150 + (i * 2),
        "cost_usd": 0.0025 + (i * 0.0001),
        "quality_score": 0.88,
        "payload": {"answer_preview": "This is a clean AI response."}
    })

# 2. Error requests (diverse breakdown)
count = 0
for err, qty in error_events:
    for k in range(qty):
        count += 1
        cid = f"req-err-{err.lower()}-{k:02d}"
        records.append({
            "ts": ts,
            "level": "error",
            "service": "api",
            "env": "dev",
            "event": "request_failed",
            "correlation_id": cid,
            "user_id_hash": f"u_hash_{k%5}",
            "session_id": f"s_{k%10}",
            "feature": "qa",
            "model": "claude-sonnet-4-5",
            "error_type": err,
            "error_message": f"Simulated {err} for dashboard observability"
        })

# Write to file
with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Re-generated {len(records)} 100% valid log records in {LOG_PATH}")
