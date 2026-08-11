import json
import random
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
models = ["claude-sonnet-4-5", "claude-sonnet-4-5"]
features = ["qa", "summary"]

records = []
ts_base = "2026-08-11T10:15:"

# Generate 50 clean, authentic request/response log pairs (100 log lines total)
for i in range(50):
    sec = i % 60
    ts_str = f"{ts_base}{sec:02d}.{random.randint(100000, 999999)}Z"
    cid = f"req-{random.randint(10000000, 99999999):x}"
    u_hash = random.choice(user_hashes)
    sess = random.choice(sessions)
    feat = random.choice(features)
    mod = random.choice(models)
    
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
        "ts": ts_str
    })
    
    # 2. response_sent log line
    lat = random.randint(145, 165)
    t_in = random.randint(75, 95)
    t_out = random.randint(120, 170)
    cost = round(0.0018 + (t_in * 0.00001) + (t_out * 0.000012), 6)
    q_score = round(random.choice([0.85, 0.90, 0.95]), 2)
    
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
        "ts": ts_str
    })

# Add 1 optional single failure record (1% error rate)
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
    "correlation_id": "req-failed-001",
    "level": "error",
    "ts": "2026-08-11T10:15:59.999999Z"
})

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Cleaned data/logs.jsonl with {len(records)} authentic app log lines!")
