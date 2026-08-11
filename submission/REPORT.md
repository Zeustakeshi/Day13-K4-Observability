# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** — 21 log records, 0 missing required fields, 0 missing enrichment, 10 unique correlation IDs, 0 PII leak. Xem [validate_logs_score.png](evidence/validate_logs_score.png).
- Tổng số traces: 6 traces / 12 observations trên Langfuse (user `95b6504a8bd6`, xem [detail_langfuse.png](evidence/detail_langfuse.png)).
- Số PII leak còn lại: 0 (theo `validate_logs.py`, kiểm tra độc lập bằng regex email/phone/CCCD/thẻ tín dụng trên toàn bộ record thô).
- Link/đường dẫn dashboard: _(điền ở mục 5 sau khi hoàn tất CP checkpoint dashboard)_

## 3. Logging và tracing

- Evidence correlation ID: middleware `CorrelationIdMiddleware` ([app/middleware.py](../app/middleware.py)) sinh `correlation_id` dạng `req-<uuid8>` từ header `x-request-id` (hoặc tự tạo nếu thiếu), bind vào `structlog` contextvars nên mọi log trong request đều mang cùng ID. Ví dụ trong `data/logs.jsonl`: `req-fd1621f6`, `req-6bdd3833`, `req-e6ed0d53` — mỗi ID lặp lại trên các log entry của cùng một request.
- Evidence PII redaction: `scrub_event` processor ([app/logging_config.py](../app/logging_config.py)) gọi `scrub_text` ([app/pii.py](../app/pii.py)) trên `payload` và `event` trước khi ghi ra `data/logs.jsonl`, dùng regex cho email, SĐT VN, CCCD, thẻ tín dụng, hộ chiếu, địa chỉ VN. Bằng chứng: [redacted_log_samples.png](evidence/redacted_log_samples.png) — ví dụ `"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"`, `"...my phone [REDACTED_PHONE_VN]..."`, `"...credit card [REDACTED_CREDIT_CARD]?"`. `validate_logs.py` xác nhận độc lập: 0 PII leak trên dữ liệu thô.
- Evidence trace waterfall: [detail_langfuse.png](evidence/detail_langfuse.png) — trace `run` (root, 0.91s, $0.002226) chứa 1 nested generation span `run` (Σ174 tokens, $0.002226), gắn `Session: s02`, `User ID: 95b6504a8bd6`, tags `claude-sonnet-4-5`, `lab`, `qa`. Trang [langfuse.png](evidence/langfuse.png) (Users overview) đối chiếu `user_id_hash` giữa Langfuse và log: `95b6504a8bd6` khớp đúng với `hash_user_id()` trong `data/logs.jsonl`.
- Giải thích một span đáng chú ý: span `generation` trong `LabAgent.run` ([app/agent.py](../app/agent.py)), bọc bằng `@observe(as_type="generation", capture_input=False, capture_output=False)`. Span này bao trọn RAG retrieve (`mock_rag.retrieve`) + gọi LLM (`FakeLLM.generate`), sau đó tự cập nhật metadata (`prompt_name`, `prompt_label`, `prompt_version`, `doc_count`, `query_preview` đã scrub PII) và usage/cost qua `update_current_generation`. `capture_input=False`/`capture_output=False` là chủ đích để tránh nội dung thô (có thể chứa PII) bị Langfuse tự động ghi lại — đúng trong ảnh evidence, `Input: null` và `Output: undefined` vì input/output không được SDK tự capture, chỉ metadata đã qua xử lý mới được gửi lên.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

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
|---|---|---|---|
| | | | |
