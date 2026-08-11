import httpx
import time

queries = [
    ("Latency P95 (24h window)", 'quantile_over_time(0.95, {job="day13-logs"} | json | event="response_sent" | unwrap latency_ms [24h])'),
    ("Traffic (24h window)", 'sum(count_over_time({job="day13-logs"} | json | event="request_received" [24h]))'),
    ("Cost (24h window)", 'sum(sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap cost_usd [24h]))'),
    ("Tokens In (24h window)", 'sum(sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap tokens_in [24h]))'),
    ("Quality (24h window)", 'avg_over_time({job="day13-logs"} | json | event="response_sent" | unwrap quality_score [24h])'),
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
        print(f"✅ '{name}': {len(res)} series, sample val: {res[0]['values'][-1] if res else 'empty'}")
    else:
        print(f"❌ '{name}': error {r.status_code}")
