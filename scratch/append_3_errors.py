import json
from pathlib import Path

LOG_PATH = Path("data/logs.jsonl")

# 3 new error log lines: 1 NEW error type (DatabaseError) + 2 existing error types (TimeoutError, LLMError)
new_errors = [
    {
        "service": "api",
        "error_type": "DatabaseError",  # 1 NEW error type!
        "error_message": "PostgreSQL connection pool exhausted",
        "event": "request_failed",
        "feature": "qa",
        "user_id_hash": "4d14d5d4f719",
        "env": "dev",
        "model": "claude-sonnet-4-5",
        "session_id": "s01",
        "correlation_id": "req-err-db-01",
        "level": "error",
        "ts": "2026-08-11T10:40:01.111111Z"
    },
    {
        "service": "api",
        "error_type": "TimeoutError",  # Merged with existing TimeoutError!
        "error_message": "LLM gateway timeout during peak request",
        "event": "request_failed",
        "feature": "qa",
        "user_id_hash": "1632c29ecdec",
        "env": "dev",
        "model": "claude-sonnet-4-5",
        "session_id": "s02",
        "correlation_id": "req-err-timeout-02",
        "level": "error",
        "ts": "2026-08-11T10:40:02.222222Z"
    },
    {
        "service": "api",
        "error_type": "LLMError",  # Merged with existing LLMError!
        "error_message": "OpenAI API returned 503 Service Unavailable",
        "event": "request_failed",
        "feature": "summary",
        "user_id_hash": "2f015d970c0b",
        "env": "dev",
        "model": "claude-sonnet-4-5",
        "session_id": "s07",
        "correlation_id": "req-err-llm-02",
        "level": "error",
        "ts": "2026-08-11T10:40:03.333333Z"
    }
]

lines = [json.dumps(err) + "\n" for err in new_errors]

with open(LOG_PATH, "a", encoding="utf-8") as f:
    f.writelines(lines)

print(f"✅ Successfully appended 3 new error log lines (1 DatabaseError + 1 TimeoutError + 1 LLMError) to {LOG_PATH}!")
