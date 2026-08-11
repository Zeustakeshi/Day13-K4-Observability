from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

# Path Definitions
REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "dashboard.yaml"
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"

# Page Config
st.set_page_config(
    page_title="Day 13 AI Observability Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Glassmorphism UI)
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    .status-pass {
        color: #00E676;
        font-weight: bold;
    }
    .status-fail {
        color: #FF5252;
        font-weight: bold;
    }
    .title-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4DEEEA, #74EE15);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=5)
def load_config() -> dict:
    if not CONFIG_PATH.exists():
        st.error(f"Không tìm thấy file config tại: {CONFIG_PATH}")
        st.stop()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("dashboard", {})


def generate_mock_logs() -> list[dict]:
    """Tạo dữ liệu baseline giả lập khi chưa có file data/logs.jsonl"""
    now = datetime.now(timezone.utc)
    mock = []
    import random

    for i in range(120):
        ts = (now - timedelta(seconds=(120 - i) * 30)).isoformat()
        cid = f"req-{i:03d}"
        
        # request_received
        mock.append({
            "ts": ts,
            "level": "INFO",
            "service": "api",
            "event": "request_received",
            "correlation_id": cid,
            "user_id_hash": "user_hash_123",
            "session_id": "session_abc",
            "feature": "chat",
            "model": "gpt-4o-mini",
        })
        
        # 97% thành công, 3% thất bại
        is_error = random.random() < 0.03
        if is_error:
            mock.append({
                "ts": ts,
                "level": "ERROR",
                "service": "api",
                "event": "request_failed",
                "correlation_id": cid,
                "error_type": random.choice(["TimeoutError", "RateLimitError", "APIConnectionError"]),
            })
        else:
            mock.append({
                "ts": ts,
                "level": "INFO",
                "service": "api",
                "event": "response_sent",
                "correlation_id": cid,
                "latency_ms": round(random.uniform(400, 2200), 2),
                "cost_usd": round(random.uniform(0.001, 0.015), 5),
                "tokens_in": random.randint(100, 600),
                "tokens_out": random.randint(150, 800),
                "quality_score": round(random.uniform(0.80, 0.98), 2),
            })
    return mock


def load_logs() -> tuple[pd.DataFrame, bool]:
    records = []
    is_mock = False
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    
    if not records:
        records = generate_mock_logs()
        is_mock = True

    df = pd.DataFrame(records)
    if "ts" in df.columns:
        df["dt"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)
        df = df.dropna(subset=["dt"]).sort_values("dt")
    return df, is_mock


def main():
    config = load_config()
    st.markdown(f"<h1 class='title-header'>⚡ {config.get('title', 'Day 13 AI Observability')}</h1>", unsafe_allow_html=True)
    st.caption("Contract Dashboard Monitoring & SLO Enforcement — Day 13 Lab")

    # Sidebar Options
    st.sidebar.header("⚙️ Dashboard Controls")
    refresh_rate = config.get("refresh_seconds", 30)
    auto_refresh = st.sidebar.checkbox(f"Auto-refresh (Mỗi {refresh_rate}s)", value=False)
    
    time_window_min = config.get("time_range_minutes", 60)
    st.sidebar.info(f"🕒 Khung thời gian: **{time_window_min} phút gần nhất**")
    
    if st.sidebar.button("🔄 Refresh dữ liệu ngay"):
        st.rerun()

    df, is_mock = load_logs()
    
    if is_mock:
        st.warning("⚠️ Chưa có file `data/logs.jsonl` hoặc file rỗng! Đang hiển thị dữ liệu Baseline giả lập để test giao diện. Hãy chạy API/Load test để sinh log thực tế.")
    else:
        st.success(f"✅ Đang đọc dữ liệu thực tế từ `data/logs.jsonl` ({len(df)} dòng log).")

    # Filter logs to last time_window_min minutes
    if not df.empty and "dt" in df.columns:
        latest_time = df["dt"].max()
        cutoff_time = latest_time - pd.Timedelta(minutes=time_window_min)
        df = df[df["dt"] >= cutoff_time]

    panels_cfg = {p["id"]: p for p in config.get("panels", [])}

    # -------------------------------------------------------------
    # Row 1: Latency & Traffic
    # -------------------------------------------------------------
    col1, col2 = st.columns(2)

    # --- PANEL 1: LATENCY ---
    with col1:
        st.subheader("1. Latency Percentiles (ms)")
        p_cfg = panels_cfg.get("latency", {})
        res_df = df[df["event"] == "response_sent"].copy()
        
        if not res_df.empty and "latency_ms" in res_df.columns:
            res_df["minute"] = res_df["dt"].dt.floor("1min")
            latency_by_min = res_df.groupby("minute")["latency_ms"].agg(
                p50=lambda x: x.quantile(0.50),
                p95=lambda x: x.quantile(0.95),
                p99=lambda x: x.quantile(0.99)
            ).reset_index()

            overall_p95 = res_df["latency_ms"].quantile(0.95)
            thresh_val = p_cfg.get("threshold", {}).get("value", 3000)
            status_cls = "status-pass" if overall_p95 <= thresh_val else "status-fail"
            status_txt = "PASSED (≤ 3000ms)" if overall_p95 <= thresh_val else "VIOLATED (> 3000ms)"

            st.markdown(f"**P95 Hiện Tại:** `{overall_p95:.1f} ms` | Trạng thái SLO: <span class='{status_cls}'>{status_txt}</span>", unsafe_allow_html=True)

            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=latency_by_min["minute"], y=latency_by_min["p50"], mode="lines", name="P50"))
            fig1.add_trace(go.Scatter(x=latency_by_min["minute"], y=latency_by_min["p95"], mode="lines", name="P95", line=dict(width=3)))
            fig1.add_trace(go.Scatter(x=latency_by_min["minute"], y=latency_by_min["p99"], mode="lines", name="P99"))
            
            # Threshold line
            fig1.add_hline(y=thresh_val, line_dash="dash", line_color="#FF5252", annotation_text=f"SLO Threshold ({thresh_val}ms)")
            fig1.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="ms", legend=dict(orientation="h"))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu `response_sent`")

    # --- PANEL 2: TRAFFIC ---
    with col2:
        st.subheader("2. Request Traffic (req/min)")
        p_cfg = panels_cfg.get("traffic", {})
        req_df = df[df["event"] == "request_received"].copy()
        
        if not req_df.empty:
            req_df["minute"] = req_df["dt"].dt.floor("1min")
            traffic_by_min = req_df.groupby("minute").size().reset_index(name="count")

            avg_rate = traffic_by_min["count"].mean() if not traffic_by_min.empty else 0
            thresh_val = p_cfg.get("threshold", {}).get("value", 1)
            status_cls = "status-pass" if avg_rate >= thresh_val else "status-fail"
            status_txt = "PASSED (≥ 1 req/m)" if avg_rate >= thresh_val else "LOW TRAFFIC (< 1 req/m)"

            st.markdown(f"**Trung Bình Traffic:** `{avg_rate:.1f} req/min` | SLO Status: <span class='{status_cls}'>{status_txt}</span>", unsafe_allow_html=True)

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=traffic_by_min["minute"], y=traffic_by_min["count"], name="Requests", marker_color="#4DEEEA"))
            fig2.add_hline(y=thresh_val, line_dash="dash", line_color="#00E676", annotation_text=f"SLO Min ({thresh_val} req/m)")
            fig2.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="req/min")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu `request_received`")

    # -------------------------------------------------------------
    # Row 2: Errors & Cost
    # -------------------------------------------------------------
    col3, col4 = st.columns(2)

    # --- PANEL 3: ERRORS ---
    with col3:
        st.subheader("3. Error Rate & Breakdown (%)")
        p_cfg = panels_cfg.get("errors", {})
        total_reqs = len(df[df["event"] == "request_received"])
        failed_df = df[df["event"] == "request_failed"]
        total_fails = len(failed_df)

        err_rate_pct = (total_fails / total_reqs * 100) if total_reqs > 0 else 0.0
        thresh_val = p_cfg.get("threshold", {}).get("value", 2.0)
        status_cls = "status-pass" if err_rate_pct <= thresh_val else "status-fail"
        status_txt = "PASSED (≤ 2%)" if err_rate_pct <= thresh_val else "HIGH ERROR RATE (> 2%)"

        st.markdown(f"**Tỷ lệ lỗi tổng thể:** `{err_rate_pct:.2f}%` | SLO Status: <span class='{status_cls}'>{status_txt}</span>", unsafe_allow_html=True)

        if not failed_df.empty and "error_type" in failed_df.columns:
            err_counts = failed_df["error_type"].value_counts().reset_index()
            err_counts.columns = ["error_type", "count"]
            fig3 = go.Figure(data=[go.Pie(labels=err_counts["error_type"], values=err_counts["count"], hole=0.4)])
            fig3.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.success("🎉 Không ghi nhận lỗi nào trong cửa sổ làm việc!")

    # --- PANEL 4: COST ---
    with col4:
        st.subheader("4. Cost Over Time ($ USD)")
        p_cfg = panels_cfg.get("cost", {})
        res_df = df[df["event"] == "response_sent"].copy()

        if not res_df.empty and "cost_usd" in res_df.columns:
            res_df["minute"] = res_df["dt"].dt.floor("1min")
            cost_by_min = res_df.groupby("minute")["cost_usd"].sum().reset_index()
            cost_by_min["cumulative"] = cost_by_min["cost_usd"].cumsum()

            total_cost = res_df["cost_usd"].sum()
            thresh_val = p_cfg.get("threshold", {}).get("value", 2.5)
            status_cls = "status-pass" if total_cost <= thresh_val else "status-fail"
            status_txt = "PASSED (≤ $2.50)" if total_cost <= thresh_val else "BUDGET EXCEEDED (> $2.50)"

            st.markdown(f"**Tổng Chi Phí Tích Lũy:** `${total_cost:.4f}` | SLO Status: <span class='{status_cls}'>{status_txt}</span>", unsafe_allow_html=True)

            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=cost_by_min["minute"], y=cost_by_min["cumulative"], mode="lines", name="Tích lũy ($)", fill="tozeroy"))
            fig4.add_hline(y=thresh_val, line_dash="dash", line_color="#FF5252", annotation_text=f"Max Budget (${thresh_val})")
            fig4.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="USD ($)")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu `cost_usd`")

    # -------------------------------------------------------------
    # Row 3: Tokens & Quality
    # -------------------------------------------------------------
    col5, col6 = st.columns(2)

    # --- PANEL 5: TOKENS ---
    with col5:
        st.subheader("5. Input & Output Tokens")
        p_cfg = panels_cfg.get("tokens", {})
        res_df = df[df["event"] == "response_sent"].copy()

        if not res_df.empty and "tokens_in" in res_df.columns and "tokens_out" in res_df.columns:
            tot_in = int(res_df["tokens_in"].sum())
            tot_out = int(res_df["tokens_out"].sum())
            tot_tokens = tot_in + tot_out
            
            thresh_val = p_cfg.get("threshold", {}).get("value", 50000)
            status_cls = "status-pass" if tot_tokens <= thresh_val else "status-fail"
            status_txt = "PASSED (≤ 50k)" if tot_tokens <= thresh_val else "EXCEEDED LIMIT (> 50k)"

            st.markdown(f"**Tổng Tokens:** `{tot_tokens:,}` (In: {tot_in:,} | Out: {tot_out:,}) | Status: <span class='{status_cls}'>{status_txt}</span>", unsafe_allow_html=True)

            fig5 = go.Figure(data=[
                go.Bar(name="Tokens In", x=["Sum"], y=[tot_in], marker_color="#74EE15"),
                go.Bar(name="Tokens Out", x=["Sum"], y=[tot_out], marker_color="#4DEEEA")
            ])
            fig5.add_hline(y=thresh_val, line_dash="dash", line_color="#FF5252", annotation_text=f"Limit ({thresh_val:,})")
            fig5.update_layout(barmode="stack", height=320, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="Tokens")
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu Tokens")

    # --- PANEL 6: QUALITY PROXY ---
    with col6:
        st.subheader("6. Quality Proxy Score")
        p_cfg = panels_cfg.get("quality", {})
        res_df = df[df["event"] == "response_sent"].copy()

        if not res_df.empty and "quality_score" in res_df.columns:
            res_df["minute"] = res_df["dt"].dt.floor("1min")
            q_by_min = res_df.groupby("minute")["quality_score"].mean().reset_index()

            mean_q = res_df["quality_score"].mean()
            thresh_val = p_cfg.get("threshold", {}).get("value", 0.75)
            status_cls = "status-pass" if mean_q >= thresh_val else "status-fail"
            status_txt = "PASSED (≥ 0.75)" if mean_q >= thresh_val else "BELOW TARGET (< 0.75)"

            st.markdown(f"**Quality Score Trung Bình:** `{mean_q:.2f}` | Status: <span class='{status_cls}'>{status_txt}</span>", unsafe_allow_html=True)

            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(x=q_by_min["minute"], y=q_by_min["quality_score"], mode="lines+markers", name="Quality Score", line=dict(color="#FFD700")))
            fig6.add_hline(y=thresh_val, line_dash="dash", line_color="#00E676", annotation_text=f"SLO Min ({thresh_val})")
            fig6.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="Score (0..1)", yaxis_range=[0, 1.05])
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu `quality_score`")

    # Auto refresh timer
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()


if __name__ == "__main__":
    main()
