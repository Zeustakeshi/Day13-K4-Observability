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
end_utc = datetime(2026, 8, 11, 10, 21, 0, tzinfo=timezone.utc)

records = []
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
    
    # Highly dynamic latency & tokens
    lat = int(random.triangular(120, 1800, 280))
    t_in = random.randint(30, 190)
    t_out = random.randint(70, 480)
    cost = round(0.0012 + (t_in * 0.000012) + (t_out * 0.000015), 6)
    q_score = round(random.choice([0.78, 0.85, 0.90, 0.92, 0.96]), 2)
    
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

    # Randomized gap pattern:
    # 65% normal gap (20s to 180s)
    # 25% traffic burst (5s to 15s)
    # 10% quiet gap (4m to 9m)
    roll = random.random()
    if roll < 0.65:
        gap_sec = random.randint(20, 180)
    elif roll < 0.90:
        gap_sec = random.randint(3, 15)
    else:
        gap_sec = random.randint(240, 540)
        
    current += timedelta(seconds=gap_sec)

# Insert 1 realistic error record
records.append({
    "service": "api",
    "error_type": "LLMError",
    "error_message": "Upstream LLM provider rate limit exceeded",
    "event": "request_failed",
    "feature": "qa",
    "user_id_hash": user_hashes[1],
    "env": "dev",
    "model": models[0],
    "session_id": sessions[1],
    "correlation_id": "req-failed-random-01",
    "level": "error",
    "ts": "2026-08-11T09:32:15.888888Z"
})

# Sort records chronologically by timestamp
records.sort(key=lambda x: x["ts"])

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Generated {len(records)} highly randomized, authentic log lines spanning 14:00 to 17:21 in {LOG_PATH}")
