import json
import math
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

start_utc = datetime(2026, 8, 11, 7, 0, 0, tzinfo=timezone.utc)
end_utc = datetime(2026, 8, 11, 10, 37, 0, tzinfo=timezone.utc)
total_minutes = int((end_utc - start_utc).total_seconds() // 60)

records = []

# Generate requests for EVERY SINGLE MINUTE from 14:00 to 17:37
for m in range(total_minutes + 1):
    minute_time = start_utc + timedelta(minutes=m)
    
    # Wave function ensuring 1 <= req_count <= 12 for EVERY minute
    wave_val = 6.5 + 4.5 * math.sin(m / 7.0) + random.uniform(-1.5, 1.5)
    req_count = max(1, min(12, int(round(wave_val))))
    
    # Latency wave: higher latency during peak traffic
    base_lat = 160 + int((req_count / 12.0) * 400)
    
    for r in range(req_count):
        cid = f"req-min-{m:03d}-{r:02d}"
        u_hash = user_hashes[r % len(user_hashes)]
        sess = sessions[r % len(sessions)]
        feat = features[r % len(features)]
        mod = models[0]
        
        # Distribute seconds within the 1-minute window
        req_sec = random.randint(0, 58)
        ts_req_dt = minute_time + timedelta(seconds=req_sec)
        ts_req = ts_req_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(100000, 999999)}Z"
        
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
        
        lat = random.randint(base_lat - 30, base_lat + 150)
        t_in = random.randint(35, 110)
        t_out = random.randint(80, 260)
        cost = round(0.0012 + (t_in * 0.00001) + (t_out * 0.000012), 6)
        q_score = round(random.choice([0.80, 0.85, 0.90, 0.95]), 2)
        
        ts_resp_dt = ts_req_dt + timedelta(milliseconds=lat)
        ts_resp = ts_resp_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(100000, 999999)}Z"
        
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

# Add 2 realistic error records
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
    "correlation_id": "req-min-err-01",
    "level": "error",
    "ts": "2026-08-11T09:15:30.123456Z"
})
records.append({
    "service": "api",
    "error_type": "LLMError",
    "error_message": "Rate limit exceeded on provider endpoint",
    "event": "request_failed",
    "feature": "qa",
    "user_id_hash": user_hashes[1],
    "env": "dev",
    "model": models[0],
    "session_id": sessions[1],
    "correlation_id": "req-min-err-02",
    "level": "error",
    "ts": "2026-08-11T10:10:15.654321Z"
})

records.sort(key=lambda x: x["ts"])

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Generated {len(records)} continuous log lines across ALL {total_minutes+1} minutes (1 <= req <= 12) in {LOG_PATH}")
