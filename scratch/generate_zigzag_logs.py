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

start_utc = datetime(2026, 8, 11, 7, 0, 0, tzinfo=timezone.utc)
end_utc = datetime(2026, 8, 11, 10, 30, 0, tzinfo=timezone.utc)

records = []

# Define distinct peak and valley time points (in minutes from start)
# High Peak (15 req) -> Quiet Valley (0 req) -> Mid Peak (8 req) -> Low Valley (1 req) -> High Peak (12 req)...
traffic_timeline = [
    (10, 12, 140, 220),   # 14:10 Peak: 12 requests (140ms latency)
    (25, 2,  450, 680),   # 14:25 Valley: 2 requests (450ms latency)
    (40, 18, 180, 290),   # 14:40 High Peak: 18 requests (180ms latency)
    (55, 1,  850, 1200),  # 14:55 Valley: 1 request (850ms latency spike)
    (75, 15, 160, 240),   # 15:15 Peak: 15 requests (160ms latency)
    (90, 3,  310, 520),   # 15:30 Valley: 3 requests (310ms latency)
    (110, 22, 150, 210),  # 15:50 High Peak: 22 requests (150ms latency)
    (130, 2,  620, 950),  # 16:10 Valley: 2 requests (620ms latency)
    (150, 14, 170, 280),  # 16:30 Peak: 14 requests (170ms latency)
    (175, 2,  410, 710),  # 16:55 Valley: 2 requests (410ms latency)
    (195, 20, 155, 230),  # 17:15 High Peak: 20 requests (155ms latency)
    (205, 3,  320, 480),  # 17:25 Valley: 3 requests (320ms latency)
]

for min_offset, req_count, min_lat, max_lat in traffic_timeline:
    minute_time = start_utc + timedelta(minutes=min_offset)
    
    for r in range(req_count):
        cid = f"req-zz-{min_offset:03d}-{r:02d}"
        u_hash = user_hashes[r % len(user_hashes)]
        sess = sessions[r % len(sessions)]
        feat = features[r % len(features)]
        mod = models[0]
        
        # Requests occur within the same minute window
        req_sec = random.randint(0, 55)
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
        
        lat = random.randint(min_lat, max_lat)
        t_in = random.randint(35, 120)
        t_out = random.randint(80, 310)
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

# 1 error record
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
    "correlation_id": "req-zz-err-01",
    "level": "error",
    "ts": "2026-08-11T10:15:30.123456Z"
})

records.sort(key=lambda x: x["ts"])

with open(LOG_PATH, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Generated {len(records)} zigzag peak-and-valley log lines in {LOG_PATH}")
