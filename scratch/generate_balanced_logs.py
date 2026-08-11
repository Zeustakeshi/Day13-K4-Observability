import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_PATH = Path("data/logs.jsonl")

sample_questions = [
    "What should not appear in app logs?",
    "How do I debug tail latency?",
    "How should alerts be designed?",
    "What is the difference between metrics and traces?",
    "How to scrub PII from logging pipeline?",
    "What is SLO burn rate?",
    "How to configure Promtail with Loki?",
    "What is correlation ID propagation?",
    "Explain how RAG retrieval works with vector search.",
    "Why is P95 latency better than average latency?"
]

sample_answers = [
    "Starter answer. Teams should improve this output logic and add better quality check.",
    "Observability metrics provide high level view while traces show exact span bottlenecks.",
    "Scrubbing PII ensures sensitive data like emails and credit cards are redacted before storage.",
    "Percentile latency metrics capture tail latency spikes that average metrics mask."
]

user_hashes = ["4d14d5d4f719", "1632c29ecdec", "2f015d970c0b", "105a9cef3903", "8b72e1a409f1", "9c31f4e019a2"]
sessions = ["s01", "s02", "s03", "s07", "s08", "s09", "s10", "s12", "s15"]
models = ["claude-sonnet-4-5"]
features = ["qa", "summary"]

start_utc = datetime(2026, 8, 11, 7, 0, 0, tzinfo=timezone.utc)
end_utc = datetime(2026, 8, 11, 10, 26, 0, tzinfo=timezone.utc)

records = []
current = start_utc

# Generate historical requests from 14:00 to 17:20 with 30-45 req/min traffic peak
while current <= end_utc - timedelta(minutes=6):
    cid = f"req-{random.randint(10000000, 99999999):x}"
    u_hash = random.choice(user_hashes)
    sess = random.choice(sessions)
    feat = random.choice(features)
    mod = random.choice(models)
    
    ts_req = current.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(100000, 999999)}Z"
    
    records.append({
        "service": "api",
        "payload": {"message_preview": random.choice(sample_questions)},
        "event": "request_received",
        "feature": feat,
        "user_id_hash": u_hash,
        "env": "dev",
        "model": mod,
        "session_id": sess,
        "correlation_id": cid,
        "level": "info",
        "ts": ts_req
    })
    
    lat = int(random.triangular(140, 1200, 320))
    t_in = random.randint(35, 140)
    t_out = random.randint(90, 320)
    cost = round(0.0015 + (t_in * 0.00001) + (t_out * 0.000012), 6)
    q_score = round(random.choice([0.80, 0.85, 0.90, 0.95]), 2)
    
    ts_resp = (current + timedelta(milliseconds=lat)).strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(100000, 999999)}Z"
    
    records.append({
        "service": "api",
        "latency_ms": lat,
        "tokens_in": t_in,
        "tokens_out": t_out,
        "cost_usd": cost,
        "quality_score": q_score,
        "payload": {"answer_preview": random.choice(sample_answers)},
        "event": "response_sent",
        "feature": feat,
        "user_id_hash": u_hash,
        "env": "dev",
        "model": mod,
        "session_id": sess,
        "correlation_id": cid,
        "level": "info",
        "ts": ts_resp
    })

    # Pace intervals for 30-45 req/min peaks
    gap_sec = random.randint(90, 240)
    current += timedelta(seconds=gap_sec)

# Add ~10 fresh log lines with a few different errors at 17:26 (10:26 UTC)
fresh_ts = "2026-08-11T10:26:00.000000Z"
new_errors = [
    ("TimeoutError", "LLM upstream connection timeout"),
    ("LLMError", "Rate limit exceeded on OpenAI endpoint"),
    ("ToolError", "Vector DB query execution failed"),
    ("PIIError", "Sensitive data detected in payload"),
    ("TimeoutError", "RAG retriever response timeout"),
]

for idx, (err_type, err_msg) in enumerate(new_errors):
    records.append({
        "service": "api",
        "error_type": err_type,
        "error_message": err_msg,
        "event": "request_failed",
        "feature": "qa",
        "user_id_hash": user_hashes[idx % len(user_hashes)],
        "env": "dev",
        "model": models[0],
        "session_id": sessions[idx % len(sessions)],
        "correlation_id": f"req-new-err-{idx:02d}",
        "level": "error",
        "ts": "2026-08-11T10:26:" + f"{idx*3:02d}.123456Z"
    })

# Add matching request_received lines for accurate error rate calculations
for idx in range(5):
    records.append({
        "service": "api",
        "payload": {"message_preview": "Test fresh request"},
        "event": "request_received",
        "feature": "qa",
        "user_id_hash": user_hashes[idx],
        "env": "dev",
        "model": models[0],
        "session_id": sessions[idx],
        "correlation_id": f"req-new-err-{idx:02d}",
        "level": "info",
        "ts": "2026-08-11T10:25:55.000000Z"
    })

# Sort chronologically
records.sort(key=lambda x: x["ts"])

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Generated balanced dataset with {len(records)} log lines including ~10 fresh diverse error log lines at 17:26!")
