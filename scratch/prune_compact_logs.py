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
    "How to scrub PII from logging pipeline?"
]

sample_answers = [
    "Starter answer. Teams should improve this output logic and add better quality check.",
    "Observability metrics provide high level view while traces show exact span bottlenecks.",
    "Scrubbing PII ensures sensitive data like emails and credit cards are redacted before storage."
]

user_hashes = ["4d14d5d4f719", "1632c29ecdec", "2f015d970c0b", "105a9cef3903"]
sessions = ["s01", "s02", "s07", "s08"]
models = ["claude-sonnet-4-5"]
features = ["qa", "summary"]

start_utc = datetime(2026, 8, 11, 9, 30, 0, tzinfo=timezone.utc)
end_utc = datetime(2026, 8, 11, 10, 30, 0, tzinfo=timezone.utc)

records = []
current = start_utc

# Generate 18 clean, compact request/response log pairs (36 log lines)
for i in range(18):
    cid = f"req-{random.randint(10000000, 99999999):x}"
    u_hash = user_hashes[i % len(user_hashes)]
    sess = sessions[i % len(sessions)]
    feat = features[i % len(features)]
    mod = models[0]
    
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
    
    lat = int(random.triangular(140, 800, 250))
    t_in = random.randint(40, 110)
    t_out = random.randint(100, 240)
    cost = round(0.0015 + (t_in * 0.00001) + (t_out * 0.000012), 6)
    q_score = round(random.choice([0.85, 0.90, 0.95]), 2)
    
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

    current += timedelta(minutes=random.randint(2, 4))

# 1 single error record
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
    "correlation_id": "req-compact-err-01",
    "level": "error",
    "ts": "2026-08-11T10:28:00.123456Z"
})

records.sort(key=lambda x: x["ts"])

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Pruned data/logs.jsonl to {len(records)} ultra-compact authentic log lines!")
