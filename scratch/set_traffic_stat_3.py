import json
import random
from pathlib import Path

LOG_PATH = Path("data/logs.jsonl")

# 3 fresh requests at current minute 17:41 (10:41 UTC)
ts_now = "2026-08-11T10:41:15.000000Z"

sample_questions = [
    "What should not appear in app logs?",
    "How do I debug tail latency?",
    "How should alerts be designed?"
]

sample_answers = [
    "Starter answer. Teams should improve this output logic and add better quality check.",
    "Observability metrics provide high level view while traces show exact span bottlenecks.",
    "Scrubbing PII ensures sensitive data like emails and credit cards are redacted before storage."
]

user_hashes = ["4d14d5d4f719", "1632c29ecdec", "2f015d970c0b"]
sessions = ["s01", "s02", "s07"]

new_records = []
for i in range(3):
    cid = f"req-stat3-{i:02d}"
    
    # 1. request_received
    new_records.append({
        "service": "api",
        "payload": {"message_preview": sample_questions[i]},
        "event": "request_received",
        "feature": "qa",
        "user_id_hash": user_hashes[i],
        "env": "dev",
        "model": "claude-sonnet-4-5",
        "session_id": sessions[i],
        "correlation_id": cid,
        "level": "info",
        "ts": "2026-08-11T10:41:" + f"{i*15:02d}.100000Z"
    })
    
    # 2. response_sent
    new_records.append({
        "service": "api",
        "latency_ms": 150 + (i * 20),
        "tokens_in": 45 + i,
        "tokens_out": 130 + i,
        "cost_usd": 0.0021,
        "quality_score": 0.90,
        "payload": {"answer_preview": sample_answers[i]},
        "event": "response_sent",
        "feature": "qa",
        "user_id_hash": user_hashes[i],
        "env": "dev",
        "model": "claude-sonnet-4-5",
        "session_id": sessions[i],
        "correlation_id": cid,
        "level": "info",
        "ts": "2026-08-11T10:41:" + f"{i*15 + 1:02d}.200000Z"
    })

lines = [json.dumps(rec) + "\n" for rec in new_records]

with open(LOG_PATH, "a", encoding="utf-8") as f:
    f.writelines(lines)

print(f"✅ Successfully added 3 requests at 17:41 to set Request Traffic Stat card to 3 req/min!")
