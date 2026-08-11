import httpx
import time

queries = [
    ("Latency P50", 'quantile_over_time(0.50, {job="day13-logs"} | json | event="response_sent" | unwrap latency_ms [1m])'),
    ("Latency P95", 'quantile_over_time(0.95, {job="day13-logs"} | json | event="response_sent" | unwrap latency_ms [1m])'),
    ("Latency P99", 'quantile_over_time(0.99, {job="day13-logs"} | json | event="response_sent" | unwrap latency_ms [1m])'),
    ("Traffic", 'sum(count_over_time({job="day13-logs"} | json | event="request_received" [1m]))'),
    ("Error Rate", '(sum(count_over_time({job="day13-logs"} | json | event="request_failed" [1m])) / sum(count_over_time({job="day13-logs"} | json | event="request_received" [1m]))) * 100'),
    ("Error Breakdown", 'sum by (error_type) (count_over_time({job="day13-logs"} | json | event="request_failed" [1m]))'),
    ("Cost", 'sum(sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap cost_usd [1m]))'),
    ("Tokens In", 'sum(sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap tokens_in [1m]))'),
    ("Tokens Out", 'sum(sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap tokens_out [1m]))'),
    ("Quality Score", 'avg_over_time({job="day13-logs"} | json | event="response_sent" | unwrap quality_score [1m])'),
]

start_ns = str(int((time.time() - 86400) * 1e9))
end_ns = str(int(time.time() * 1e9))

for name, expr in queries:
    r = httpx.get(
        "http://localhost:3100/loki/api/v1/query_range",
        params={
            "query": expr,
            "start": start_ns,
            "end": end_ns,
            "step": "60s"
        }
    )
    if r.status_code == 200:
        res = r.json().get("data", {}).get("result", [])
        print(f"✅ Query '{name}': SUCCESS (Status 200), {len(res)} series")
    else:
        print(f"❌ Query '{name}': FAILED (Status {r.status_code}): {r.text[:100]}")
