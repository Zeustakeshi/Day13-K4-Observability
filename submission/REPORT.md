# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: 50s
- Repository URL: https://github.com/Zeustakeshi/Day13-K4-Observability
- Commit SHA cuối: `73faf215e56029b87fed064c049975dd1d8e9872`
- Thành viên và vai trò:
  1. **Phạm Minh Hiếu** - MSV: `2A202601562` - **Role A** (Logging & PII)
  2. **Đặng Nguyên Giáp** - MSV: `2A202601486` - **Role B** (Tracing & Prompt Versioning)
  3. **Mai Tuấn Quang** - MSV: `2A202601484` - **Role C** (Dashboard, SLO & Alert)
  4. **Nguyễn Thị Thu Trang** - MSV: `2A202601172` - **Role D** (Incident, Report & Demo)

## 2. Kết quả kỹ thuật

<!-- - Điểm `validate_logs.py`: **100/100** — 21 log records, 0 missing required fields, 0 missing enrichment, 10 unique correlation IDs, 0 PII leak. Xem [validate_logs_score.png](evidence/validate_logs_score.png). -->

- Baseline Checkpoint 0 `validate_logs.py`: **30/100**. Evidence: [validate_log_checkpoint0.png](evidence/validate_log_checkpoint0.png).
- Sau Checkpoint 1 `validate_logs.py`: **100/100** — 21 log records, 0 missing required fields, 0 missing enrichment, 10 unique correlation IDs, 0 PII leak. Evidence: [validate_logs_checkpoint1.png](evidence/validate_logs_checkpoint1.png).
- Tổng số traces: 6 traces / 12 observations trên Langfuse (user `95b6504a8bd6`, xem [detail_langfuse.png](evidence/detail_langfuse.png)).
- Số PII leak còn lại: 0 (theo `validate_logs.py`, kiểm tra độc lập bằng regex email/phone/CCCD/thẻ tín dụng trên toàn bộ record thô).
- Link/đường dẫn dashboard: _(điền ở mục 5 sau khi hoàn tất CP checkpoint dashboard)_

## 3. Logging và tracing

- Evidence correlation ID: middleware `CorrelationIdMiddleware` ([app/middleware.py](../app/middleware.py)) sinh `correlation_id` dạng `req-<uuid8>` từ header `x-request-id` (hoặc tự tạo nếu thiếu), bind vào `structlog` contextvars nên mọi log trong request đều mang cùng ID. Ví dụ trong `data/logs.jsonl`: `req-fd1621f6`, `req-6bdd3833`, `req-e6ed0d53` — mỗi ID lặp lại trên các log entry của cùng một request.
- Evidence PII redaction: `scrub_event` processor ([app/logging_config.py](../app/logging_config.py)) gọi `scrub_text` ([app/pii.py](../app/pii.py)) trên `payload` và `event` trước khi ghi ra `data/logs.jsonl`, dùng regex cho email, SĐT VN, CCCD, thẻ tín dụng, hộ chiếu, địa chỉ VN. Bằng chứng: [redacted_log_samples.png](evidence/redacted_log_samples.png) — ví dụ `"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"`, `"...my phone [REDACTED_PHONE_VN]..."`, `"...credit card [REDACTED_CREDIT_CARD]?"`. `validate_logs.py` xác nhận độc lập: 0 PII leak trên dữ liệu thô.
- Evidence trace waterfall: [detail_langfuse.png](evidence/detail_langfuse.png) — trace `run` (root, 0.91s, $0.002226) chứa 1 nested generation span `run` (Σ174 tokens, $0.002226), gắn `Session: s02`, `User ID: 95b6504a8bd6`, tags `claude-sonnet-4-5`, `lab`, `qa`. Trang [langfuse.png](evidence/langfuse.png) (Users overview) đối chiếu `user_id_hash` giữa Langfuse và log: `95b6504a8bd6` khớp đúng với `hash_user_id()` trong `data/logs.jsonl`. Evidence bổ sung cho prompt versioning (CP2): [trace_baseline_v2.jpg](evidence/trace_baseline_v2.jpg), [trace_candidate_v3.jpg](evidence/trace_candidate_v3.jpg).
- Giải thích một span đáng chú ý: span `generation` trong `LabAgent.run` ([app/agent.py](../app/agent.py)), bọc bằng `@observe(as_type="generation", capture_input=False, capture_output=False)`. Span này bao trọn RAG retrieve (`mock_rag.retrieve`) + gọi LLM (`FakeLLM.generate`), sau đó tự cập nhật metadata (`prompt_name`, `prompt_label`, `prompt_version`, `doc_count`, `query_preview` đã scrub PII) và usage/cost qua `update_current_generation`. `capture_input=False`/`capture_output=False` là chủ đích để tránh nội dung thô (có thể chứa PII) bị Langfuse tự động ghi lại — đúng trong ảnh evidence, `Input: null` và `Output: undefined` vì input/output không được SDK tự capture, chỉ metadata đã qua xử lý mới được gửi lên.

## 4. Prompt versioning

- Prompt name: `day13-chat` (type `text`, giữ 3 biến `{{feature}}`, `{{docs}}`, `{{message}}`).
- Version/label baseline: version 2, label `baseline` (+ `production` sau khi rollback).
- Version/label candidate: version 3, label `candidate` (từng được gắn thêm `production` tạm thời).
- Trace ID của mỗi version:
  - `baseline` (v2): `cffb6afe0632cf8870fa5a3d293d85f4`
  - `candidate` (v3): `ef0db4dacb210ab24d93acd91f4ab6d2`
  - `production` trỏ v3 (sau khi đổi label): `174fd07377ff...` (session `cp2-production-v3-session`)
  - `production` sau rollback về v2: `e55d596f91b5...` (session `cp2-rollback-session`)
- Bằng chứng đổi label hoặc rollback: xác nhận qua Langfuse API — trước khi đổi, `production -> v2`;
  sau `PATCH /api/public/v2/prompts/day13-chat/versions/3 {newLabels:["candidate","production"]}`,
  `production -> v3`; sau rollback `PATCH .../versions/2 {newLabels:["baseline","production"]}`,
  `production -> v2` trở lại. 10 trace chạy `load_test.py` ngay sau rollback (session `s01`–`s10`,
  timestamp `08:43:50–51Z`) đều ghi `prompt_label=production, prompt_version=2`, xác nhận rollback
  có hiệu lực trên toàn bộ traffic thật, không chỉ 1 request thử. Chi tiết đầy đủ và nội dung
  prompt trong [evidence/prompt_versions.md](evidence/prompt_versions.md).
- Ảnh evidence:
  - [evidence/prompt_v3_candidate_production.jpg](evidence/prompt_v3_candidate_production.jpg) — version #3 mang label `production` (trước rollback)
  - [evidence/prompt_v2_baseline_production.jpg](evidence/prompt_v2_baseline_production.jpg) — version #2 mang label `production` (sau rollback)
  - [evidence/trace_baseline_v2.jpg](evidence/trace_baseline_v2.jpg) — trace baseline, chip `Prompt: day13-chat - v2`
  - [evidence/trace_candidate_v3.jpg](evidence/trace_candidate_v3.jpg) — trace candidate, chip `Prompt: day13-chat - v3`

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: **`HỢP LỆ: 6/6 panel`** có trong dashboard contract (xem `config/dashboard.yaml`).
- Evidence dashboard: Grafana Dashboard tự động nạp 6 panel chuẩn contract từ `data/logs.jsonl` qua Loki (`http://localhost:3000/d/day13-ai-observability/day-13-ai-observability-dashboard`):
  ![Grafana Dashboard Evidence](evidence/dashboard.png)
  1. Latency percentiles (P50, P95, P99) với threshold line 3000 ms.
  2. Request traffic rate (req/min) với threshold line 1 req/min.
  3. Error rate (%) và breakdown theo `error_type` (Bar/Donut chart) với threshold line 2%.
  4. Cost over time ($ USD) với threshold line $2.50.
  5. Input & output tokens (Tokens In vs Tokens Out) với threshold 50,000 tokens.
  6. Quality proxy (Mean quality score gauge) với threshold line 0.75.
- SLO đã chọn và lý do:
  - `latency_p95_ms`: Objective 3000ms, target 99.5% (đảm bảo trải nghiệm người dùng không bị chậm trễ khi chat).
  - `error_rate_pct`: Objective 2%, target 99.0% (giữ tỷ lệ phản hồi lỗi ở mức thấp chấp nhận được).
  - `daily_cost_usd`: Objective $2.50, target 100.0% (kiểm soát ngân sách vận hành API LLM).
  - `quality_score_avg`: Objective 0.75, target 95.0% (đảm bảo chất lượng câu trả lời từ RAG/LLM).
- Alert rules và runbook: Cấu hình 3 alert rules trong [config/alert_rules.yaml](../config/alert_rules.yaml) tương ứng với runbook chi tiết trong [docs/alerts.md](../docs/alerts.md):
  1. `Chat response latency SLO burn` (P1): `p95_latency_ms > 3000 for 5m` -> Runbook `docs/alerts.md#alert-1`.
  2. `Chat error rate above SLO` (P1): `error_rate_pct > 2 for 5m` -> Runbook `docs/alerts.md#alert-2`.
  3. `Token or cost spike impacting chat sessions` (P2): `total_cost_usd > 2.5 OR total_tokens > 50000 for 60m` -> Runbook `docs/alerts.md#alert-3`.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
| ---------- | --------- | --------- | ----------- |
| **Phạm Minh Hiếu** (2A202601562) | **Role A** - Logging & PII: Middleware correlation_id, log enrichment, processor scrub PII | `main` branch | Hiểu sâu về Structlog processors, contextvars và cơ chế khử PII tự động |
| **Đặng Nguyên Giáp** (2A202601486) | **Role B** - Tracing & Prompt Versioning: Quản lý Langfuse prompts, versioning & rollback | `main` branch | Nắm vững quy trình Prompt Engineering, A/B Testing và Rollback an toàn trên Langfuse |
| **Mai Tuấn Quang** (2A202601484) | **Role C** - Dashboard, SLO & Alert: Xây dựng 6 Grafana Panels, Loki queries, SLO thresholds | `main` branch | Làm chủ LogQL, thiết kế Dashboard chuẩn contract và định nghĩa SLO burn rate |
| **Nguyễn Thị Thu Trang** (2A202601172) | **Role D** - Incident, Report & Demo: Xây dựng Runbooks, điều tra root cause, tổng hợp Báo cáo | `main` branch | Kỹ năng liên kết Metrics → Traces → Logs để tìm nguyên nhân gốc rễ sự cố nhanh chóng |

