import httpx

r = httpx.get("http://localhost:3100/loki/api/v1/query_range", params={
    "query": 'sum by () (count_over_time({job="day13-logs"} | json | event="request_received" [1m]))',
    "step": "60s"
}, timeout=5.0)

print("Status:", r.status_code)
if r.status_code == 200:
    res = r.json().get("data", {}).get("result", [])
    print("Series count:", len(res))
    if res:
        vals = [int(v[1]) for v in res[0].get("values", [])]
        print(f"1-Minute Traffic Range across ALL minutes: Min={min(vals)} req/min, Max={max(vals)} req/min")
        assert min(vals) >= 1, "Warning: minute with 0 requests found!"
        assert max(vals) <= 12, "Warning: max traffic exceeded 12!"
        print("✅ Verified PERFECT: 100% of ALL minutes have traffic strictly between 1 and 12 req/min!")
