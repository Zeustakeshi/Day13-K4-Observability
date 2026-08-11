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
        latest_val = res[0].get("values", [])[-1]
        print(f"Latest Minute Request Traffic Stat: {latest_val[1]} req/min (Timestamp={latest_val[0]})")
