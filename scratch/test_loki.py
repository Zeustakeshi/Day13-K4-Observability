import httpx
import time

queries = [
    ("Latency P50", 'avg by () (avg_over_time({job="day13-logs"} | json | event="response_sent" | unwrap latency_ms [24h]))'),
    ("Latency P95", 'max by () (avg_over_time({job="day13-logs"} | json | event="response_sent" | unwrap latency_ms [24h]))'),
    ("Latency P99", 'max by () (avg_over_time({job="day13-logs"} | json | event="response_sent" | unwrap latency_ms [24h]))'),
    ("Traffic", 'sum by () (count_over_time({job="day13-logs"} | json | event="request_received" [24h]))'),
    ("Error Rate", '(sum by () (count_over_time({job="day13-logs"} | json | event="request_failed" [24h])) / sum by () (count_over_time({job="day13-logs"} | json | event="request_received" [24h]))) * 100'),
    ("Cost", 'sum by () (sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap cost_usd [24h]))'),
    ("Tokens In", 'sum by () (sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap tokens_in [24h]))'),
    ("Tokens Out", 'sum by () (sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap tokens_out [24h]))'),
    ("Quality Score", 'avg by () (avg_over_time({job="day13-logs"} | json | event="response_sent" | unwrap quality_score [24h]))'),
]

start_ns = str(int((time.time() - 86400) * 1e9))
end_ns = str(int(time.time() * 1e9))

for name, expr in queries:
    r = httpx.get("http://localhost:3100/loki/api/v1/query_range", params={"query": expr, "start": start_ns, "end": end_ns, "step": "60s"})
    if r.status_code == 200:
        res = r.json().get("data", {}).get("result", [])
        print(f"✅ '{name}': {len(res)} series (Series count={len(res)})")
    else:
        print(f"❌ '{name}': Error {r.status_code}")
