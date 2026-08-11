import httpx

r_in = httpx.get("http://localhost:3100/loki/api/v1/query", params={"query": 'sum by () (sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap tokens_in [24h]))'})
r_out = httpx.get("http://localhost:3100/loki/api/v1/query", params={"query": 'sum by () (sum_over_time({job="day13-logs"} | json | event="response_sent" | unwrap tokens_out [24h]))'})

print("Tokens In (Instant):", r_in.json().get("data", {}).get("result", []))
print("Tokens Out (Instant):", r_out.json().get("data", {}).get("result", []))
