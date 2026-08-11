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
    "What is correlation ID propagation?"
]

sample_answers = [
    "Starter answer. Teams should improve this output logic and add better quality check.",
    "Observability metrics provide high level view while traces show exact span bottlenecks.",
    "Scrubbing PII ensures sensitive data like emails and credit cards are redacted before storage."
]

user_hashes = ["4d14d5d4f719", "1632c29ecdec", "2f015d970c0b", "105a9cef3903", "8b72e1a409f1"]
sessions = ["s01", "s02", "s03", "s07", "s08", "s09", "s10"]
models = ["claude-sonnet-4-5"]
features = ["qa", "summary"]

# Time range from 14:00 local (07:00 UTC) to 17:19 local (10:19 UTC)
start_utc = datetime(2026, 8, 11, 7, 0, 0, tzinfo=timezone.utc)
end_utc = datetime(2026, 8, 11, 10, 19, 0, tzinfo=timezone.utc)
total_seconds = int((end_utc - start_utc).total_seconds())

records = []

# Step by every 120 seconds (~2 minutes) to fill the entire timeline continuously
step = 120
current = start_utc
req_counter = 0

while current <= end_utc:
    req_counter += 1
    cid = f"req-{random.randint(10000000, 99999999):x}"
    u_hash = random.choice(user_hashes)
    sess = random.choice(sessions)
    feat = random.choice(features)
    mod = random.choice(models)
    
    ts_req = current.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(100000, 999999)}Z"
    
    # 1. request_received log line
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
    
    lat = random.randint(145, 165)
    t_in = random.randint(75, 95)
    t_out = random.randint(120, 170)
    cost = round(0.0018 + (t_in * 0.00001) + (t_out * 0.000012), 6)
    q_score = round(random.choice([0.85, 0.90, 0.95]), 2)
    
    ts_resp = (current + timedelta(milliseconds=lat)).strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(100000, 999999)}Z"
    
    # 2. response_sent log line
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

    current += timedelta(seconds=step + random.randint(-15, 15))

# Add 1 failure record near 16:45 local (09:45 UTC) to maintain 1% realistic error rate
ts_err = "2026-08-11T09:45:00.123456Z"
records.append({
    "service": "api",
    "error_type": "TimeoutError",
    "error_message": "LLM upstream connection timeout",
    "event": "request_failed",
    "feature": "qa",
    "user_id_hash": user_hashes[0],
    "env": "dev",
    "model": models[0],
    "session_id": sessions[0],
    "correlation_id": "req-failed-14h",
    "level": "error",
    "ts": ts_err
})

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Re-generated {len(records)} continuous log lines spanning 14:00 to 17:19 in {LOG_PATH}")
